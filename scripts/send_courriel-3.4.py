import shelve
import smtplib
import ssl
import time
from datetime import datetime
#from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes


debug = False

db_courriel = "databases/courriel"

path_root = ''
path_files = path_root + 'fichiers'


smtp_user = ""
smtp_host = ""
smtp_port = 465 # 587 pour start tls
smtp_pass = ""

mail_delay = 30

state_invalid_address = "adresse invalide"
state_server_error = "serveur_indisponible"
state_connection_error = "erreur_de_connection"
state_interrupted = "processus_interrompu"
state_draft = "brouillon"
state_sending = "envoi_en_cours"
state_partially_sent = "envoi_partiel"
state_sent = "envoi_complet"



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
	with shelve.open(db_courriel) as db:
		if uid in db:
			data = db[uid]
			data['statut'] = state_sending
			data['pid'] = os.getpid()
			db[uid] = data
		else:
			print(uid, "not in", db_courriel)
			sys.exit(1)
	statut_final = state_sent
	# create email
	msg = MIMEMultipart()
	msg['From'] = smtp_user 
	msg['Subject'] = data['sujet']
	msg['Date'] = formatdate(localtime=True)
	msg['Message-ID'] = make_msgid()
	msg['Errors-To'] = smtp_user
	text_part = MIMEText(data['message'], 'plain')
	msg.attach(text_part)
	# add attachment 
	if data['fichier'] != '':
		path = os.path.join(path_files, data['fichier'])
		if os.path.isfile(path):
			ctype, encoding = mimetypes.guess_type(path)
			if ctype is None or encoding is not None:
				ctype = 'application/octet-stream'
			maintype, subtype = ctype.split('/', 1)
			if maintype == "text":
				with open(path) as fp:
					attachment = MIMEText(fp.read(), _subtype=subtype)
			elif maintype == "image":
				with open(path, 'rb') as fp:
					attachment = MIMEImage(fp.read(), _subtype=subtype)
			elif maintype == "audio":
				with open(path, 'rb') as fp:
					attachment = MIMEAudio(fp.read(), _subtype=subtype)
			elif ctype == "application/pdf":
				with open(path, 'rb') as fp:
					attachment = MIMEApplication(fp.read(), "pdf")
			else:
				with open(path, 'rb') as fp:
					attachment = MIMEBase(maintype, subtype)
					attachment.set_payload(fp.read())
				encoders.encode_base64(attachment)
			attachment.add_header("Content-Disposition", "attachment", filename=data['fichier'])
			msg.attach(attachment)
	# send to dests
	for dest in data['destinataires']:
		if not dest['courriel'] or dest['courriel'] == '':
			continue
		if dest['statut'] == state_sent:
			continue
		print(dest['courriel'])
		del msg['To']
		del msg['Date']
		del msg['Message-ID']
		if debug:
			msg['To'] = smtp_user 
		else:
			msg['To'] = dest['courriel']
		msg['Date'] = formatdate(localtime=True)
		msg['Message-ID'] = make_msgid()
		statut = send_message(msg)
		dest['statut'] = statut
		dest['date'] = datetime.now()
		if statut != state_sent:
			statut_final = state_partially_sent
		with shelve.open(db_courriel) as db:
			db[uid] = data
		time.sleep(mail_delay)
	data["statut"] = statut_final
	with shelve.open(db_courriel) as db:
		db[uid] = data

def usage():
	print(sys.argv[0], 'uid')
	sys.exit(1)


import sys
if len(sys.argv) != 2:
	usage()
else:
	set_message(sys.argv[1])
