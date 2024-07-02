% include('header.tpl')

<section>
<h3>Droits d'accès de {{personne['prenom']}} {{personne['nom']}}</h3>

% if erreur != ():
	<h4>Erreur:</h4>
	<ul>
		% for err in erreur:
		<li class='erreur'>{{err}}</li>
		% end
	</ul>
% end

<form class="form" action="{{url}}/personne/droit/{{personne['uid']}}" method="post">

	<input type="hidden" name="uid" value="{{personne['uid']}}"/>

	<label for="droit">droit</label>
	<select name="droit">
	% for droit in droits:
	<option value="{{droit['uid']}}"{{' selected' if personne['droit'] == droit['uid'] else ''}}>{{droit['droit']}}</option>
	% end
	</select>

	<label for="password">Nouveau mot de passe</label>
	<input type="text" name="password" value=""/>

	<label for="confirm_password">Confirmer le mot de passe</label>
	<input type="text" name="confirm_password" value=""/>

	<input value="enregistrer" type="submit"/>
</form>


</section>
% include('footer.tpl')
