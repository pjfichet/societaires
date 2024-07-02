import smtplib
import ssl
import sqlite3
import datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
import mimetypes
import os
import time


debug = False
path_root = ''
path_files = path_root + 'fichiers'
dbfile = 'data/societaires.sqlite'
smtp_user = ""
smtp_host = ""
smtp_port = 465 # 587 pour start tls
smtp_pass = ""
dest_debug = smtp_user
mail_delay = 20

state_invalid_address = "adresse invalide"
state_server_error = "serveur_indisponible"
state_connection_error = "erreur_de_connection"
state_interrupted = "processus_interrompu"
state_draft = "brouillon"
state_sending = "envoi_en_cours"
state_partially_sent = "envoi_partiel"
state_sent = "envoi_complet"

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

def send_message(msg):
	context = ssl.create_default_context()
	try:
		smtp = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
	except:
		return state_server_error
	try:
		smtp.login(smtp_user, smtp_pass)
	except:
		return state_connection_error
	try:
		smtp.send_message(msg)
	except:
		return state_interrupted
	smtp.quit()
	return state_sent

def set_message(uid):
	db = connect()
	courriel = db.execute("select * from courriel where uid = :uid",
		{'uid':uid}).fetchone()
	if not courriel:
		print(uid, "not in database")
		sys.exit(1)
	db.execute("update courriel set statut = :statut, pid = :pid where uid = :uid",
		{'statut': state_sending, 'pid': os.getpid(), 'uid': uid})

	# statut_final will update on failure
	statut_final = state_sent

	# create email
	msg = EmailMessage()
	msg['From'] = smtp_user 
	msg['Subject'] = courriel['sujet']
	msg['Date'] = formatdate(localtime=True)
	msg['Message-ID'] = make_msgid()
	msg['Errors-To'] = smtp_user
	msg.set_content(courriel['message'])
	# add attachment 
	if courriel['fichier'] != '':
		path = os.path.join(path_files, courriel['fichier'])
		if os.path.isfile(path):
			ctype, encoding = mimetypes.guess_type(path)
			if ctype is None or encoding is not None:
				ctype = 'application/octet-stream'
			maintype, subtype = ctype.split('/', 1)
			with open(path, 'rb') as fp:
				msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=courriel['fichier'])

	# send to dests
	destinataires = db.execute("""select personne.courriel, envoi.statut, envoi.uid
		from envoi left join personne on envoi.personne = personne.uid
		where envoi.courriel = :uid""", {'uid':uid}).fetchall()
	first = True
	for dest in destinataires:
		if not first:
			print("sleeping", mail_delay)
			time.sleep(mail_delay)
		first = False
		if not dest['courriel'] or dest['courriel'] == '':
			continue
		if dest['statut'] == state_sent:
			continue
		print("sending to ", dest['courriel'])
		del msg['To']
		del msg['Date']
		del msg['Message-ID']
		if debug:
			msg['To'] = dest_debug
		else:
			msg['To'] = dest['courriel']
		msg['Date'] = formatdate(localtime=True)
		msg['Message-ID'] = make_msgid()
		statut = send_message(msg)
		print("    ", dest['courriel'], statut)
		db.execute("""update envoi set statut = :statut, horodate = :horodate
			where uid = :uid""",
			{'statut': statut, 'horodate': datetime.datetime.now(), 'uid': dest['uid']})
		db.commit()

		# update statut_final in case of failure
		if statut != state_sent:
			statut_final = state_partially_sent

	# record state
	db.execute("update courriel set statut = :statut where uid = :uid",
		{'statut': statut_final, 'uid': uid})
	db.commit()

def usage():
	print(sys.argv[0], 'uid')
	sys.exit(1)


import sys
if len(sys.argv) != 2:
	usage()
else:
	set_message(sys.argv[1])
	sys.exit()
