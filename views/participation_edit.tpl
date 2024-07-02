% include('header.tpl')
<section>
<h3>Participation de {{participation['prenom']}} {{participation['nom']}}</h3>

% if erreur != ():
<h4 class='erreur'>Erreur:</h4>
<ul>
	% for err in erreur:
	<li class='erreur'>{{err}}</li>
	% end
</ul>
% end

<form class="form" action="{{url}}/participation/edit/{{participation['uid']}}" method="post">
<!-- catégorie: {{participation['categorie']}}
% for categorie in categories:
{{categorie['uid']}}:{{categorie['categorie']}}
% end
-->

	<input type="hidden" name="personne_uid" value="{{participation['personne']}}"/>

	<label for="evenement">Événement</label>
	<select name="evenement">
	% for evenement in evenements:
		<option value="{{evenement['uid']}}" {{'selected' if participation['evenement']==evenement['uid'] else ''}}>{{evenement['evenement']}}</option>
	%end
	</select>


	<label for="date">Date (jj/mm/aaaa)</label>
	% if participation['date'] == '' or not participation['date']:
		<input type="text" name="date" value=""/>
	% else:
		<input type="text" name="date" value="{{participation['date'].strftime("%d/%m/%Y")}}"/>
	% end

	<label for="categorie">Catégorie</label>
	<select name="categorie">
	% for categorie in categories:
		<!-- {{participation['categorie']}} {{categorie['uid']}} {{categorie['categorie']}} -->
		<option value="{{categorie['uid']}}" {{'selected' if participation['categorie'] == categorie['uid'] else ''}}>{{categorie['categorie']}}</option>
	%end
	</select>

	<label for="provision">Provision</label>
	<input type="text" name="provision" value="{{participation['provision']}}"/>

	<label for="capital">Capital</label>
	<input type="text" name="capital" value="{{participation['capital']}}"/>

	<label for="part">Parts sociales</label>
	<input type="text" name="part" value="{{participation['part']}}"/>

	<input value="enregistrer" type="submit"/>
</form>

</section>
% include('footer.tpl')
