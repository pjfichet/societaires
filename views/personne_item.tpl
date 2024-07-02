% include('header.tpl')

% personne = participations[0]
% civilite = { 1:'M.', 2:'Mme'}
<section>
<h3>{{civilite[personne['genre']]}} {{personne['prenom']}} {{personne['nom']}} {{personne['societe']}}</h3>
<h4>Civilité</h4>
<p>
<ul>
	<li>{{"née" if personne['genre'] == 2 else "né"}}
	le {{personne['date_naissance'].strftime("%d %B %Y")}},</li>
% if personne['nature'] == 2:
	<li>représentant {{personne['societe']}}</li>
	<li>dont le siège est situé au {{personne['adresse']}}, {{personne['code_postal']}} {{personne['ville']}}.</li>
% else:
	<li>demeurant au {{personne['adresse']}}, {{personne['code_postal']}} {{personne['ville']}}.</li>
% end
	<li>{{personne['telephone']}} &ndash; {{personne['courriel']}}</li>
</ul></p>

<h4>Participations</h4>
<p><ul>
% if personne['categorie']:
	% capital = 0
	% part = 0
	% provision = 0
	% categorie = None
	% for participation in participations:
		% capital += participation['capital']
		% part += participation['part']
		% provision += participation['provision']
		% categorie = participation['categorie']
	% end

	% if categorie:
		% if provision == 0 and capital == 0:
			<li>De la catégorie <b>{{categorie}}:</b>
		% else:
			<li>De la catégorie <b>{{categorie}}</b>
		% end

		% if provision > 0 and capital == 0:
			avec <b>{{provision}}&nbsp;€</b> de provision sur le capital:
		% elif provision > 0:
			avec <b>{{provision}}&nbsp;€</b> de provision sur le capital
		% end
		% if provision < 0 and capital == 0:
			en attente de remboursement de <b>{{provision}}&nbsp;€:</b>
		% elif provision < 0:
			en attente de remboursement de <b>{{provision}}&nbsp;€</b>
		% end
		% if capital > 0:
		et possédant <b>{{capital}}&nbsp;€</b> de capital ({{part}} {{'parts' if part>1 else 'part'}})&nbsp;:
		% end
		</b></li>

		<ul>
		% for participation in participations:
			<li><b>{{participation['evenement']}}</b> le {{participation['date'].strftime("%d %B %Y")}}&nbsp;:
			% if participation['provision'] == 0 and participation['capital'] == 0:
				{{participation['categorie']}}.
			% else:
				{{participation['categorie']}},
			% end

			% if participation['provision'] != 0 and participation['capital'] == 0:
				{{participation['provision']}}&nbsp;€ de provision.
			% elif participation['provision'] != 0 and participation['capital'] != 0:
				{{participation['provision']}}&nbsp;€ de provision,
			% end
			% if participation['capital'] > 0:
				+{{participation['capital']}}&nbsp;€ de capital ({{participation['part']}} {{'parts' if participation['part']>1 else 'part'}}).
			%elif participation['capital'] != 0:
				{{participation['capital']}}&nbsp;€ de capital ({{participation['part']}} {{'parts' if participation['part']>1 else 'part'}}).
			%end
			</li>
		% end
		</ul>
	% end
	</ul></p>
% end

<h4>Droits d'accès</h4>
<p><ul>
% if personne['droit_uid'] == 0:
	<li>N'a aucun droit d'accès au fichier des sociétaires.</li>
% elif personne['droit_uid'] == 1:
	<li>Peut modifier ses {{personne['droit']}} sur le fichier des sociétaires.</li>
% else:
	<li>Peut modifier les {{personne['droit']}} du fichier des sociétaires.</li>
% end

</ul></p>

	<div>
		<a class="button" href="{{url}}/personne/edit/{{personne['uid']}}">État civil</a>
		<a class="button" href="{{url}}/personne/participation/{{personne['uid']}}">Participations</a>
		<a class="button" href="{{url}}/personne/droit/{{personne['uid']}}">Droits d'accès</a>
	</div>

</section>
% include('footer.tpl')
