.societaires.beg
% uid = None
%for per in personnes:
	% if uid != per['uid']:
		% if uid:
.personne.end
		% end
.personne.beg
.	nr uid {{per['uid']}}
.	nr droit {{per['droit']}}
.	nr nature {{per['nature']}}
.	nr genre {{per['genre']}}
.	ds prenom {{per['prenom']}}
.	ds nom {{per['nom']}}
.	ds date_naissance {{per['date_naissance']}}
.	ds societe {{per['societe']}}
.	ds adresse {{per['adresse']}}
.	ds code_postal {{per['code_postal']}}
.	ds ville {{per['ville']}}
.	ds telephone {{per['telephone']}}
.	ds courriel {{per['courriel']}}
.	participation.beg
.		ds date {{per['date']}}
.		ds evenement {{per['evenement']}}
.		ds categorie {{per['categorie']}}
.		nr provision {{per['provision']}}
.		nr capital {{per['capital']}}
.		nr part {{per['part']}}
.	participation.end
	% else:
.	participation.beg
.		ds date {{per['date']}}
.		ds evenement {{per['evenement']}}
.		ds categorie {{per['categorie']}}
.		nr provision {{per['provision']}}
.		nr capital {{per['capital']}}
.		nr part {{per['part']}}
.	participation.end
	% end
	% uid = per['uid']
% end
.societaires.end
