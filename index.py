#! /usr/bin/env python3

from bottle import *
import datetime
import uuid
from hashlib import md5
import subprocess
import sqlite3


import locale
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

url = ''
path_root = '/home/pj/doc/src/societaires/'
path_static = path_root + 'assets'
path_files = path_root + 'fichiers'
path_data = path_root + 'data'
state_draft = "brouillon"
state_sending = "envoi_en_cours"
state_interrupted = "envoi_interrompu"
script_courriel = 'send_courriel.py'
dbfile = path_data + '/societaires.sqlite'
maintenance = False

###########################################################
# Sqlite3 configuration

def adapt_date_iso(val):
	"""Adapt datetime.date to ISO 8601 date."""
	return val.isoformat()

def adapt_datetime_iso(val):
	"""Adapt datetime.datetime to timezone-naive ISO 8601 date."""
	return val.isoformat()

def convert_date(val):
	"""Convert ISO 8601 date to datetime.date object."""
	return datetime.date.fromisoformat(val.decode())

def convert_datetime(val):
	"""Convert ISO 8601 datetime to datetime.datetime object."""
	return datetime.datetime.fromisoformat(val.decode())

sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)

def connect():
	db = sqlite3.connect(dbfile,
		detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
	#db.set_trace_callback(print) # use to debug
	db.row_factory = sqlite3.Row
	#db.enable_load_extension(True)
	#db.load_extension('./icu.so')
	#db.execute("select icu_load_collation('fr_FR', 'french')")
	db.execute("pragma foreign_keys = 1")
	db.execute("pragma journal_mode = 'wal'")
	return db

# https://bottlepy.org/docs/dev/plugindev.html#how-plugins-work-the-basics
def sqliteplugin(callback):
	def wrapper(*args, **kwargs):
		db = connect()
		kwargs['db'] = db
		try:
			rv = callback(*args, **kwargs)
		except HTTPError as e:
			raise
		except HTTPResponse as e:
			raise
		finally:
			db.close()
		return rv
	return wrapper

#install(sqliteplugin)

###########################################################
# utilities

def sanitize_str(string):
	if string:
		#string = string.encode('latin1').decode('utf8')
		return string.replace('\r', '').replace('\n', ' ')
	return ''

def sanitize_int(string):
	if string and string.lstrip('-').isdigit():
		return int(string)
	else:
		return 0

def sanitize_date(string):
	date_str = sanitize_str(string)
	if date_str == '':
		return ''
	try:
		date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
	except ValueError:
		date = ''
	return date

###########################################################
# login routes

def check_rights(request, droit):
	"Check if the cookie identify a logged in user."
	if maintenance:
		redirect(url + '/')
	uid = request.get_cookie('uid')
	if not uid:
		redirect(url + '/')
	db = connect()
	session = db.execute("select uid, fin, droit from session where uid = :uid",
		{'uid': uid}).fetchone()
	if not session:
		redirect(url + '/')
	if datetime.datetime.now() > session['fin']:
		redirect(url + '/')
	fin = datetime.datetime.now() + datetime.timedelta(minutes=30)
	db.execute("update session set fin = :fin where uid = :uid",
		{'fin': fin, 'uid': uid} )
	db.commit()
	if session['droit'] < droit:
		redirect(url + '/')

@get('/')
def index():
	if maintenance:
		return template('maintenance', url=url)
	return template('login', url=url)

@post('/', apply=[sqliteplugin])
def login(db):
	"Log in an user."
	password = sanitize_str(request.forms.password)
	values = {
		'secret': md5(password.encode()).hexdigest(),
		'prenom': sanitize_str(request.forms.prenom),
		'nom': sanitize_str(request.forms.nom)
	}
	personne = db.execute("""select uid, droit from personne
		where prenom = :prenom and nom = :nom
		and secret = :secret and droit > 0""", values).fetchone()
	if not personne:
		redirect(url + '/')
	uid = uuid.uuid4().hex
	values = {
		'uid' : uid,
		'debut': datetime.datetime.now(),
		'fin': datetime.datetime.now() + datetime.timedelta(minutes=30),
		'droit': personne['droit'],
		'personne': personne['uid']
	}
	db.execute("""insert into session (uid, debut, fin, droit, personne)
		values (:uid, :debut, :fin, :droit, :personne)""", values)
	db.commit()
	response.set_cookie('uid', uid)
	redirect(url + '/historique')

@get('/quitter')
def quitter():
	response.delete_cookie('uid')
	redirect(url + '/')

@get('/aide')
def aide():
	check_rights(request, 2)
	return template('aide', url=url)

def query_historique():
	nb_categories = 7
	query = """select societaires, provision, capital, part,
		hommes, femmes, autres, mineurs, adultes, aines, """
	for num in range(nb_categories):
		query += "\npersonnes_{num}, provision_{num}, capital_{num}, categorie_{num}, part_{num},".format(num=num)
	query +="""\ndate_fin as 'date_fin [date]'

	from
	-- societaires
	(select count(*) as societaires from
		(select max(date), categorie from participation
		where date <= :date_fin
		group by personne)
	where (categorie = 2 or categorie = 3
	or categorie = 4 or categorie = 5)
	),
	-- provision, capital, parts
	(
		select sum(provision) as provision,
			sum(capital) as capital,
			sum(part) as part
			from participation where date <= :date_fin
	),

	-- hommes
	(select count(*) as hommes from
		(select max(date), categorie, genre from participation, personne
		where date <= :date_fin and participation.personne = personne.uid
		group by personne)
		where (categorie = 2 or categorie = 3
		or categorie = 4 or categorie = 5)
		and genre = 1
	),
	-- femmes
	(select count(*) as femmes from
		(select max(date), categorie, genre from participation, personne
		where date <= :date_fin and participation.personne = personne.uid
		group by personne)
		where (categorie = 2 or categorie = 3
		or categorie = 4 or categorie = 5)
		and genre = 2
	),
	-- autres
	(select count(*) as autres from
		(select max(date), categorie, genre from participation, personne
		where date <= :date_fin and participation.personne = personne.uid
		group by personne)
		where (categorie = 2 or categorie = 3
		or categorie = 4 or categorie = 5)		
		and (genre = 0 or genre = 3)
	),
	-- mineurs
	(select count(*) as mineurs from
		(select max(date), categorie, date_naissance from participation, personne
		where date <= :date_fin and participation.personne = personne.uid
		group by personne)
		where (categorie = 2 or categorie = 3
		or categorie = 4 or categorie = 5)		
		and date_naissance > date(:date_fin, '-18 year')
	),
	-- adultes
	(select count(*) as adultes from
		(select max(date), categorie, date_naissance from participation, personne
		where date <= :date_fin and participation.personne = personne.uid
		group by personne)
		where (categorie = 2 or categorie = 3
		or categorie = 4 or categorie = 5)		
		and date_naissance <= date(:date_fin, '-18 year')
		and date_naissance > date(:date_fin, '-64 year')
	),
	-- aines
	(select count(*) as aines from
		(select max(date), categorie, date_naissance from participation, personne
		where date <= :date_fin and participation.personne = personne.uid
		group by personne)
		where (categorie = 2 or categorie = 3
		or categorie = 4 or categorie = 5)		
		and date_naissance <= date(:date_fin, '-64 year')
	),
	"""
	for num in range(nb_categories):
		query += """
	-- categorie_{num}
	(select categorie as categorie_{num} from categorie where uid={num}),
	-- personnes_{num}, capital_{num}, provision_{num}, part_{num}
	(select count(*) as personnes_{num}, sum(capital_perso) as capital_{num}, sum(provision_perso) as provision_{num},
		sum(part_perso) as part_{num}
		from (
			select max(date), sum(provision) as provision_perso, sum(capital) as capital_perso,
			sum(part) as part_perso, categorie
			from participation
			where date <= :date_fin
			group by personne)
		where categorie = {num}
	),
	""".format(num = num)
	query += "(select :date_fin as date_fin)"
	return query



@get('/historique', apply=[sqliteplugin])
def historique(db):
	check_rights(request, 2)
	query = query_historique()
	# données récoltées pour chaque dates
	data = ()
	date = {}
	# jour de la création
	date['date_fin'] = datetime.date(2019, 4, 30)
	while date['date_fin'] < datetime.date.today():
		row = db.execute(query, date).fetchone()
		data= data + (row,)
		# et pour toutes les années qui suivent jusqu'à aujourd'hui
		date['date_fin'] = datetime.date(date['date_fin'].year + 1, 6, 30)
	# Et pour aujourd'hui
	date['date_fin'] = datetime.date.today()
	row = db.execute(query, date).fetchone()
	data = data + (row,)

	return template('historique', data=reversed(data), url=url)
	
@post('/historique', apply=[sqliteplugin])
def historique_date(db):
	check_rights(request, 2)
	date = {}
	date['date_fin'] = sanitize_date(request.forms.date)
	if date['date_fin'] == '':
		redirect (url + '/historique')
	query = query_historique()
	row = db.execute(query, date).fetchone()
	return template('historique', data=(row, ), url=url)
	

###########################################################
# Personne routes

@get('/personne', apply=[sqliteplugin])
def personne_liste(db):
	check_rights(request, 2)
	personnes = db.execute("""
		select personne.uid, personne.genre, personne.prenom,
		personne.nom, personne.societe, personne.courriel,
		max(participation.date) as maxdate, sum(participation.capital) as capital,
		sum(participation.provision) as provision,
		categorie.categorie as categorie
		from personne
		left join participation on participation.personne = personne.uid
		left join categorie on participation.categorie = categorie.uid
		group by participation.personne
		order by participation.categorie, personne.nom, personne.prenom""")
	return template('personne_liste', personnes=personnes, date=datetime.date.today(), url=url)

@post('/personne', apply=[sqliteplugin])
def personne_liste(db):
	check_rights(request, 2)
	date = {}
	date['date_fin'] = sanitize_date(request.forms.date)
	if date['date_fin'] == '':
		redirect (url + '/personne')
	personnes = db.execute("""
		select personne.uid, personne.genre, personne.prenom,
			personne.nom, personne.societe, personne.courriel,
		max(participation.date) as maxdate, sum(participation.capital) as capital,
		sum(participation.provision) as provision,
		categorie.categorie as categorie
		from personne
		left join participation on participation.personne = personne.uid
		left join categorie on participation.categorie = categorie.uid
		where participation.date <= :date_fin
		group by participation.personne
		order by participation.categorie, personne.nom, personne.prenom""", date)
	return template('personne_liste', personnes=personnes, date=date['date_fin'], url=url)


@post('/personne/recherche', apply=[sqliteplugin])
def personne_recherche(db):
	check_rights(request, 2)
	string = sanitize_str(request.forms.recherche).lower()
	personnes = db.execute("""
		select * from
			(select personne.uid, personne.genre, personne.prenom,
			personne.nom, personne.societe, personne.courriel,
			max(participation.date) as maxdate, sum(participation.capital) as capital,
			sum(participation.provision) as provision,
			categorie.categorie as categorie
			from personne
			left join participation on participation.personne = personne.uid
			left join categorie on participation.categorie = categorie.uid
			group by participation.personne)
		where prenom like :string or nom like :string or societe like :string
		or courriel like :string or categorie like :string
		order by nom, prenom""", {'string': '%'+string+'%'})
	return template("personne_liste", personnes=personnes, date=datetime.date.today(), url=url)

@get('/personne/item/<uid>', apply=[sqliteplugin])
def personne_item(uid, db):
	check_rights(request, 2)
	participations = db.execute("""
		select personne.uid, personne.nature, personne.genre, personne.prenom,
		personne.nom, personne.date_naissance, personne.societe, personne.adresse,
		personne.code_postal, personne.ville, personne.telephone, personne.courriel,
		personne.note, droit.uid as droit_uid, droit.droit, categorie.categorie,
		evenement.evenement, participation.date, participation.provision,
		participation.capital, participation.part
		from personne
		left join participation on participation.personne = personne.uid
		left join evenement on evenement.uid = participation.evenement
		left join categorie on categorie.uid = participation.categorie
		left join droit on personne.droit = droit.uid
		where personne.uid = :uid""", {'uid': uid}).fetchall()
	return template("personne_item", participations=participations, url=url)

@get('/personne/nouveau')
def personne_nouveau():
	check_rights(request, 2)
	personne = {
		'uid': '',
		'nature': '',
		'genre': '',
		'nom': '',
		'prenom': '',
		'date_naissance': '',
		'societe': '',
		'adresse': '',
		'code_postal': '',
		'ville': '',
		'telephone': '',
		'courriel': '',
		'note': '',
		'droit': 0
	}
	return template('personne_edit', personne=personne, erreur=(), url=url)

def personne_verifie(personne):
	# vérifie les données
	erreur = ()
	if personne['nature'] < 1 or personne['nature'] > 2:
		erreur += ('préciser la nature de la personne',)
	if personne['genre'] < 0 or personne['genre'] > 2:
		erreur += ('préciser le genre de la personne',)
	if personne['date_naissance'] == '':
		erreur += ('indiquer une date de naissance au format JJ/MM/AAAA',)
	for key in ('nom', 'prenom', 'adresse', 'code_postal', 'ville'):
		if personne[key] == '':
			erreur += ('préciser le champ ' + key + ' de la personne',)
	return erreur

@post('/personne/edit/', apply=[sqliteplugin])
def personne_creer(db):
	check_rights(request, 2)
	personne = {
		'nature': sanitize_int(request.forms.nature),
		'genre': sanitize_int(request.forms.genre),
		'nom': sanitize_str(request.forms.nom),
		'prenom': sanitize_str(request.forms.prenom),
		'date_naissance': sanitize_date(request.forms.date_naissance),
		'societe': sanitize_str(request.forms.societe),
		'adresse': sanitize_str(request.forms.adresse),
		'code_postal': sanitize_str(request.forms.code_postal),
		'ville': sanitize_str(request.forms.ville),
		'telephone': sanitize_str(request.forms.telephone),
		'courriel': sanitize_str(request.forms.courriel),
		'note': sanitize_str(request.forms.note),
		'droit': 0
	}
	erreur = personne_verifie(personne)
	if erreur != ():
		return template('personne_edit', personne=personne, erreur=erreur, url=url)
	cur = db.cursor()
	cur.execute("""insert into personne (nature, genre, nom, prenom,
		date_naissance, societe, adresse, code_postal, ville, telephone,
		courriel, note, droit)
		values (:nature, :genre, :nom, :prenom, :date_naissance, :societe,
		:adresse, :code_postal, :ville, :telephone, :courriel, :note,
		:droit)""", personne)
	uid = cur.lastrowid
	db.commit()
	redirect(url + '/personne/item/' + str(uid))

@get('/personne/edit/<uid>', apply=[sqliteplugin])
def personne_edit(uid, db):
	check_rights(request, 2)
	personne = db.execute("select * from personne where uid = :uid",
		{'uid': uid}).fetchone()
	if not personne:
		redirect(url + '/personne')
	return template('personne_edit', personne=personne, erreur=(), url=url)


@post('/personne/edit/<uid>', apply=[sqliteplugin])
def personne_modifier(uid, db):
	check_rights(request, 2)
	personne = {
		'uid': uid,
		'nature': sanitize_int(request.forms.nature),
		'genre': sanitize_int(request.forms.genre),
		'nom': sanitize_str(request.forms.nom),
		'prenom': sanitize_str(request.forms.prenom),
		'date_naissance': sanitize_date(request.forms.date_naissance),
		'societe': sanitize_str(request.forms.societe),
		'adresse': sanitize_str(request.forms.adresse),
		'code_postal': sanitize_str(request.forms.code_postal),
		'ville': sanitize_str(request.forms.ville),
		'telephone': sanitize_str(request.forms.telephone),
		'courriel': sanitize_str(request.forms.courriel),
		'note': sanitize_str(request.forms.note)
	}
	erreur = personne_verifie(personne)
	if erreur != ():
		return template('personne_edit', personne=personne, erreur=erreur, url=url)
	db.execute("""update personne set
		nature = :nature, genre = :genre, nom = :nom, prenom = :prenom,
		date_naissance = :date_naissance, societe = :societe,
		adresse = :adresse, code_postal = :code_postal, ville = :ville,
		telephone = :telephone, courriel = :courriel, note = :note
		where uid = :uid""", personne)
	db.commit()
	redirect(url + '/personne/item/' + str(uid))

##########################################################
# participation routes

@get('/participation', apply=[sqliteplugin])
def participation_liste(db):
	check_rights(request, 3)
	participations = db.execute("""select
	participation.date, participation.provision, participation.capital,
	participation.personne, categorie.categorie, evenement.evenement,
	personne.nom, personne.prenom
	from participation
	left join personne on participation.personne = personne.uid
	left join categorie on participation.categorie = categorie.uid
	left join evenement on participation.evenement= evenement.uid
	order by date desc, nom, prenom""").fetchall()
	return template('participation_liste', participations=participations, url=url)

@get('/personne/participation/<uid>', apply=[sqliteplugin])
def personne_participation(uid, db):
	check_rights(request, 3)
	participations = db.execute("""select
	personne.uid as personne_uid, personne.nom, personne.prenom,
	participation.uid, participation.date, participation.provision,
	participation.capital, participation.part,
	evenement.evenement, categorie.categorie
	from personne
	left join participation on participation.personne = personne.uid
	left join categorie on participation.categorie = categorie.uid
	left join evenement on participation.evenement = evenement.uid
	where personne.uid = :uid
	order by date""", {'uid': uid}).fetchall()
	return template("personne_participation", participations=participations, url=url)

@get('/personne/participation/nouveau/<uid>', apply=[sqliteplugin])
def participation_nouveau(uid, db):
	check_rights(request, 3)
	personne = db.execute("select prenom, nom from personne where uid = :uid",
		{'uid': uid}).fetchone()
	if not personne:
		redirect(url + '/participation')
	categories = db.execute("select * from categorie").fetchall()
	evenements = db.execute("select * from evenement").fetchall()
	participation = {
		'uid': '',
		'prenom': personne['prenom'],
		'nom': personne['nom'],
		'personne': uid,
		'date': '',
		'evenement': '',
		'provision': 0,
		'capital': 0,
		'part': 0,
		'categorie': ''
	}
	return template('participation_edit', participation=participation,
		categories=categories, evenements=evenements, erreur=(), url=url)

def participation_verifie(participation):
	erreur=()
	# on génère l'erreur
	if participation['date'] == '':
		erreur += ('indiquer une date au format JJ/MM/AAAA',)
	if participation['categorie'] == '':
		erreur += ("""indiquer une catégorie.
			Si celle-ci n'est pas modifiée, indiquer la catégorie actuelle.""",)
	# 1 = souscription
	if participation['evenement'] == 1:
		if participation['capital'] != 0 or participation['provision'] < 1:
			erreur += ("""lors de souscription, indiquer le montant souscrit
				dans le compte provision, et un capital nul.
				La modification de capital suppose l'admission
				du nouveau sociétaire par l'assemblée générale.""",)
		if participation['part'] != 0:
			erreur += ("""le champ part sociale suppose décision d'assemblée générale
				et doit rester à 0 lors de la souscription.""",)
		if participation['categorie'] != 1:
			erreur += ("lors de la souscription, choisir la catégorie 'nouveau'",)
	# 2 = admission
	elif participation['evenement'] == 2:
		if (participation['provision'] >= 0 or participation['capital'] <= 0
			or participation['provision']+participation['capital'] !=0):
			erreur += ("""pour l'admission, débitter le champ 'provision',
				et créditer le champ 'capital' du montant souscrit.""",)
		if participation['part'] <= 0:
			erreur += ("""indiquer le nombre de parts sociales souscrites.""",)
		# Todo: on doit pouvoir admettre un sociétaire comme ancien, lorsque la démission
		# a été prononcée avant l'AG.
		if participation['categorie'] < 2:
			erreur += ("""lors de l'admission, choisir une catégorie parmi les
				les catégories de sociétaires définies par les statuts""",)
	# 3 = changement de catégorie
	elif participation['evenement'] == 3:
		if participation['capital'] != 0:
			erreur +=("""ne pas modifier le capital lors du changement de catégorie
				(laisser le champ à 0)""",)
		if participation['provision'] != 0:
			erreur +=("""ne pas modifier le compte provision
				lors du changement de catégorie (laisser le champ à 0)""",)
		if participation['part'] != 0:
			erreur +=("""ne pas modifier le nombre de parts sociales
				lors du changement de catégorie (laisser le champ à 0)""",)
		if participation['categorie'] < 2:
			erreur +=("""lors du changement de catégorie, choisir une catégorie parmi
				les catégories de sociétaires définies par les statuts.""",)
	# 4 = augmentation de capital
	elif participation['evenement'] == 4:
		if participation['provision'] != 0:
			erreur += ("""ne pas modifier le compte provision
				lors de l'augmentation de capital (laisser le champ à 0""",)
		if participation['categorie'] < 2:
			erreur += ("""lors d'une augmentation de capital, ne pas modifier
				la catégorie du sociétaire.""",)
		if participation['capital'] <= 0:
			erreur += ("""indiquer le capital supplémentaire souscrit.""",)
		if participation['part'] <= 0:
			erreur += ("""indiquer le nombre de parts sociales supplémentaires souscrites.""",)
	# 5 = diminution de capital
	elif participation['evenement'] == 5:
		if participation['categorie'] < 2:
			erreur += ("""lors d'une diminution de capital, ne pas modifier
				la catégorie du sociétaire.""",)
	# 6 = démission
	elif participation['evenement'] == 6:
		if participation['provision'] >= 0:
			erreur += ("""lors de la démission, débiter le compte provision
				du montant du capital possédé par la personne.""",)
		if participation['capital'] != 0:
			erreur += ("""lors de la démission, laisser le champ capital à 0.
			Le remboursement ne peut être décidé qu'après l'assemblée générale.""",)
		if participation['part'] != 0:
			erreur += ("""lors de la démission, laisser le champ parts sociales à 0.""",)
		if participation['categorie'] != 6:
			erreur += ("""lors de la démission, sélectionner la catégorie 'sortant'""",)
	# 7 = remboursement
	elif participation['evenement'] == 7:
		if participation['categorie'] != 0:
			erreur += ("""lors du remboursement, sélectionner la catégorie 'ancien'""",)
		if (participation['provision'] <= 0 or participation['capital'] >= 0
			or participation['provision']+participation['capital'] !=0):
			erreur += ("""lors du remboursement, créditer le champ 'provision',
			et débiter le champ 'capital' du montant remboursé.""",)
		if participation['part'] >= 0:
			erreur += ("""lors du remboursement, débiter le champ parts sociales du nombre
			de parts remboursées.""",)
	# 8 = don à la coopérative
	elif participation['evenement'] == 8:
		if participation['categorie'] != 0:
			erreur += ("""lors du don à la coopérative, sélectionner la catégorie 'ancien'""",)
		if (participation['provision'] <= 0 or participation['capital'] >= 0
			or participation['provision']+participation['capital'] !=0):
			erreur += ("""lors du don à la coopérative, créditer le champ 'provision',
			et débiter le champ 'capital' du montant donné.""",)
		if participation['part'] >= 0:
			erreur += ("""lors du don à la coopérative, débiter le champ parts sociales du nombre
			de parts données.""",)
	else:
		if participation['capital'] != 0 and participation['part'] == 0:
			erreur += ("indiquer le nombre de parts concernées par la modification du capital",)
		if participation['part'] != 0 and participation['capital'] == 0:
			erreur += ("la modification du champ part sociale suppose modification du capital",)
	# on retourne l'erreur générée
	return erreur

@post('/participation/edit/', apply=[sqliteplugin])
def participation_creer(db):
	check_rights(request, 3)
	participation = {
		'date': sanitize_date(request.forms.date),
		'evenement': sanitize_int(request.forms.evenement),
		'categorie': sanitize_int(request.forms.categorie),
		'provision': sanitize_int(request.forms.provision),
		'capital': sanitize_int(request.forms.capital),
		'part':  sanitize_int(request.forms.part),
		'personne': sanitize_int(request.forms.personne_uid)
	}
	erreur = participation_verifie(participation)
	if erreur != ():
		per = db.execute("select prenom, nom from personne where uid = :personne", participation).fetchone()
		participation['prenom'] = per['prenom']
		participation['nom'] = per['nom']
		participation['uid'] = ''
		categories = db.execute("select * from categorie").fetchall()
		evenements = db.execute("select * from evenement").fetchall()
		return template('participation_edit', participation=participation,
			categories=categories, evenements=evenements, erreur=erreur, url=url)
	db.execute("""insert into participation
		(date, evenement, categorie, provision, capital, part, personne)
		values (:date, :evenement, :categorie, :provision, :capital, :part, :personne)""", participation)
	db.commit()
	redirect(url + '/personne/participation/' + str(participation['personne']))

@get('/participation/edit/<uid>', apply=[sqliteplugin])
def participation_edit(uid, db):
	check_rights(request, 3)
	participation = db.execute("""select participation.*, personne.nom, personne.prenom
	from participation join personne on participation.personne = personne.uid
	where participation.uid = :uid""", {'uid': uid}).fetchone()
	evenements = db.execute("select * from evenement").fetchall()
	categories = db.execute("select * from categorie").fetchall()
	return template('participation_edit', participation=participation,
		evenements=evenements, categories=categories, erreur=(), url=url)

@post('/participation/edit/<uid>', apply=[sqliteplugin])
def participation_modifier(uid, db):
	check_rights(request, 3)
	participation = {
		'uid': uid,
		'date': sanitize_date(request.forms.date),
		'evenement': sanitize_int(request.forms.evenement),
		'categorie': sanitize_int(request.forms.categorie),
		'provision': sanitize_int(request.forms.provision),
		'capital': sanitize_int(request.forms.capital),
		'part': sanitize_int(request.forms.part),
		'personne': sanitize_int(request.forms.personne_uid)
	}
	erreur = participation_verifie(participation)
	if erreur != ():
		per = db.execute("select prenom, nom from personne where uid = :personne", participation).fetchone()
		participation['prenom'] = per['prenom']
		participation['nom'] = per['nom']
		categories = db.execute("select * from categorie").fetchall()
		evenements = db.execute("select * from evenement").fetchall()
		return template('participation_edit', participation=participation,
			categories=categories, evenements=evenements, erreur=erreur, url=url)
	db.execute("""update participation set date = :date,
	evenement = :evenement, categorie = :categorie, provision = :provision,
	capital = :capital, part = :part, personne = :personne
	where uid = :uid""", participation)
	db.commit()
	redirect(url + '/personne/participation/' + str(participation['personne']))

###########################################################
# Droit routes

@get('/droit', apply=[sqliteplugin])
def droit_liste(db):
	check_rights(request, 5)
	personnes = db.execute("""select personne.uid, prenom, nom, droit.droit
	from personne join droit on personne.droit = droit.uid
	where personne.droit > 1""").fetchall()
	return template('droit_liste', personnes=personnes, url=url)

@get('/personne/droit/<uid>', apply=[sqliteplugin])
def personne_droit(uid, db):
	check_rights(request, 5)
	personne = db.execute("""select personne.uid, personne.prenom, personne.nom,
	personne.droit from personne
	where personne.uid = :uid""", {'uid': uid}).fetchone()
	if not personne:
		redirect(url + '/droit')
	droits = db.execute("select * from droit").fetchall()
	return template('personne_droit', personne=personne, droits=droits, erreur=(), url=url)

@post('/personne/droit/<uid>', apply=[sqliteplugin])
def droit_modifier(uid, db):
	check_rights(request, 5)
	personne = {
		'uid': uid,
		'droit': sanitize_int(request.forms.droit)
	}
	password = sanitize_str(request.forms.password)
	confirm_password = sanitize_str(request.forms.confirm_password)
	if password == '':
		# mot de passe non modifié, on enregistre seulement les droits
		db.execute("""update personne set droit = :droit where uid = :uid""", personne)
	elif password == confirm_password:
		# mot de passe correctement modifié, on l'enregistre
		personne['secret'] = md5(password.encode()).hexdigest()
		db.execute("""update personne set droit = :droit, secret = :secret
			where uid = :uid""", personne)
	else:
		# mot de passe incorrect, on renvoie l'erreur
		erreur = ('le mot de passe et sa confirmation ne sont pas identiques',)
		per = db.execute("select prenom, nom from personne where uid = :uid", personne).fetchone()
		personne['prenom'] = per['prenom']
		personne['nom'] = per['nom']
		droits = db.execute("select * from droit").fetchall()
		return template('personne_droit', personne=personne, droits=droits, erreur=erreur, url=url)
	db.commit()
	redirect(url + '/personne/item/' + str(uid))


##########################################################
# courriel routes

def process_interrupted(pid, statut):
	""" Check For the existence of a unix pid. """
	if statut == state_sending:
		if pid == 0:
			return False
		try:
			import warnings
			warnings.simplefilter("ignore")
			os.kill(pid, 0)
			warnings.resetwarnings()
		except OSError:
			# returns OSError if pid does not exist,
			# proof that the process has been interrupted
			return True
	return False
	

@get('/courriel', apply=[sqliteplugin])
def courriel_liste(db):
	check_rights(request, 4)
	courriels = db.execute("""select * from courriel order by date""").fetchall()
	data = ()
	for courriel in courriels:
		if process_interrupted(courriel['pid'], courriel['statut']):
				new = []
				new['uid'] = courriel['uid']
				new['statut'] = state_interrupted
				new['pid'] = 0
				data = data + (new,)
	if data != ():
		db.executemany("""update courriel, set statut = :statut,
			pid = :pid, where uid = :uid""", data)
		courriels = db.execute("""select * from courriel order by date""")
		db.commit()
	return template('courriel_liste', courriels=courriels, url=url)	

@get('/courriel/item/<uid>', apply=[sqliteplugin])
def courriel_item(uid, db):
	check_rights(request, 4)
	courriel = db.execute("select * from courriel where uid = ?", (uid,)).fetchone()
	if not courriel:
		redirect(url + '/courriel')
	if process_interrupted(courriel['pid'], courriel['statut']):
		db.execute("""update courriel set
			statut = :statut, pid = :pid where uid = :uid""", 
			{'uid': uid, 'statut': state_interrupted, 'pid': 0})
		db.commit()
	envois = db.execute("""select courriel.*, personne.nom,
		personne.prenom, personne.courriel, envoi.statut, envoi.horodate
		from envoi
		left join courriel on envoi.courriel = courriel.uid
		left join personne on envoi.personne = personne.uid""").fetchall()
	return template('courriel_item', envois=envois, url=url)

@get('/courriel/supprimer/<uid>', apply=[sqliteplugin])
def courriel_supprimer(uid, db):
	check_rights(request, 4)
	courriel = db.execute("select * from courriel where uid = :uid",
		{'uid': uid}).fetchone()
	if not courriel:
		redirect(url + '/courriel')
	if courriel['fichier'] != '':
		path = os.path.join(path_files, courriel['fichier'])
		if os.path.isfile(path):
			os.remove(path)
	db.execute("delete from courriel where uid = :uid", {'uid': uid})
	db.commit()
	redirect(url + '/courriel')

@get('/courriel/envoyer/<uid>', apply=[sqliteplugin])
def courriel_envoyer(uid, db):
	check_rights(request, 4)
	courriel = db.execute("select * from courriel where uid = :uid",
		{'uid': uid}).fetchone()
	if not courriel:
		redirect(url + '/courriel')	
	if courriel['statut'] == state_sending:
			redirect(url + '/courriel/item/' + uid)
	db.execute("update courriel set statut = :statut where uid = :uid",
		{'statut': state_sending, 'uid': uid})
	db.commit()
	cmd = ['python3', 'scripts/' + script_courriel, uid]
	p = subprocess.Popen(cmd, start_new_session=True)
	redirect(url + '/courriel/item/' + str(uid))

@get('/courriel/nouveau', apply=[sqliteplugin])
def courriel_nouveau(db):
	check_rights(request, 4)
	courriel = {
		'uid': '',
		'pid': '',
		'statut': '',
		'horodate': '',
		'sujet': '',
		'message': '',
		'fichier': '',
		'envois': '',
		'courriel': ''}
	uid = request.get_cookie('uid')
	adresse = db.execute("""select courriel from session
		left join personne on session.personne = personne.uid
		where session.uid = :uid""", {'uid':uid}).fetchone()
	courriel['courriel'] = adresse['courriel']
	return template('courriel_edit', courriel=courriel, url=url)

@post('/courriel/nouveau', apply=[sqliteplugin])
def courriel_enregistrer(db):
	check_rights(request, 4)
	filename = ''
	fichier = request.files.get('fichier')
	if fichier:
		filename = fichier.filename
		if filename != 'empty':
			fichier.save(path_files, overwrite=True)
		else:
			filename = ''
	# le courriel
	courriel = {
		'pid': 0,
		'statut': state_draft,
		'sujet': sanitize_str(request.forms.sujet),
		'message': request.forms.message.replace('\r', '') + '\n',
		'fichier': filename
	}
	cur = db.cursor()
	cur.execute("""insert into courriel (pid, statut, date, sujet, message, fichier)
	values (:pid, :statut, date(), :sujet, :message, :fichier)""", courriel)
	uid = cur.lastrowid
	db.commit()
	# on construit la liste des destinataires
	destinataires = sanitize_str(request.forms.destinataires)
	if destinataires == 'test':
		# un seul destinataire, la personne qui l'envoie:
		session_uid = request.get_cookie('uid')
		db.execute("""insert into envoi (personne, courriel, horodate, statut)
			select personne_uid, :uid, datetime(), :statut
			from (select session.personne as personne_uid
			from session where uid = :session_uid)""",
			{'uid': uid, 'statut': state_draft, 'session_uid': session_uid})
	else:
		# tous sociétaires actifs et les nouveaux sont destinataires
		# on construit la liste en excluant les anciens sociétaires
		db.execute("""
			insert into envoi (personne, courriel, horodate, statut)
			select personne_uid, :uid, datetime(), :statut
			from (
				select max(participation.date) as maxdate,
				participation.categorie as categorie, personne.uid as personne_uid
				from participation
				left join personne on participation.personne = personne.uid
				group by participation.personne
				order by personne.nom, personne.prenom
			)
			where categorie != 0""",
			{'uid': uid, 'statut': state_draft})
	db.execute("""update courriel set envois =
		(select count(*) from envoi where envoi.courriel = :uid)""",
		{'uid': uid})
	db.commit()
	redirect(url + '/courriel/item/' + str(uid))

###########################################################
# export
@get('/societaires.sqlite')
def export_sqlite():
	check_rights(request, 2)
	return static_file('societaires.sqlite', root=path_data)

@get('/societaires.tr', apply=[sqliteplugin])
def export_troff(db):
	check_rights(request, 2)
	personnes = db.execute("""select personne.*, participation.date,
	participation.provision, participation.capital, participation.part, evenement.evenement, categorie.categorie
	from personne
	left join participation on participation.personne = personne.uid
	left join evenement on participation.evenement = evenement.uid
	left join categorie on participation.categorie = categorie.uid
	order by personne.nom, personne.prenom, participation.date
	""").fetchall()
	response.content_type = 'text/plain; charset=UTF8'
	return template('export_troff', personnes=personnes)

@get('/societaires.fods', apply=[sqliteplugin])
def export_libreoffice(db):
	check_rights(request, 2)
	personnes = db.execute("""select personne.uid, nature.nature, genre.genre,
	nom, prenom, date_naissance, societe,
	adresse, code_postal, ville, telephone, courriel,
	max(participation.date) as date_modif, categorie.categorie as categorie,
	sum(participation.provision) as provision, sum(participation.capital) as capital,
	sum(participation.part) as parts, note
	from personne
	left join participation on participation.personne = personne.uid
	left join categorie on categorie.uid = participation.categorie
	left join nature on nature.uid = personne.nature
	left join genre on genre.uid = personne.genre
	group by personne
	order by categorie, nom, prenom""").fetchall()
	participations = db.execute("""select personne, nom, prenom, date,
	evenement.evenement, categorie.categorie,
	provision, capital, part
	from participation
	left join personne on personne.uid = participation.personne
	left join evenement on evenement.uid = participation.evenement
	left join categorie on categorie.uid = participation.categorie
	order by date""").fetchall()
	response.content_type = 'application/vnd.oasis.opendocument.spreadsheet; charset=utf-8'
	horodate = datetime.datetime.now()
	return template('export_fods', horodate=horodate,
		personnes=personnes, participations=participations)

###########################################################
# static and error routes
@error(404)
def error404(error):
	return template('login', url=url)

@error(405)
def error405(error):
	return template('login', url=url)

@get('/style.css')
def css():
	return static_file('style.css', root=path_static)

@get('/fichiers/<filename>')
def fichier(filename):
	check_rights(request, 4)
	return static_file(filename, root=path_files)

############################################################
# Starting block
debug(True)
run(host='localhost', port=8080)
