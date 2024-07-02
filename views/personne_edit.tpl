% include('header.tpl')
<section>
<h3>Personne</h3>

% if erreur != ():
<h4 class='erreur'>Erreur:</h4>
<ul>
	% for err in erreur:
		<li class='erreur'>{{err}}</li>
	% end
</ul>
% end

<form class="form" action="{{url}}/personne/edit/{{personne['uid']}}" method="post">
	<label for="nature">Nature</label>
	<select name="nature">
		<option value="1" {{"selected" if personne['nature']==1 else ''}}>Physique</option>
		<option value="2" {{"selected" if personne['nature']==2 else ''}}>Morale</option>
	</select>

	<label for="genre">Genre</label>
	<select name="genre">
		<option value="0" {{"selected" if personne['genre']==0 else ''}}>inconnu</option>
		<option value="1" {{"selected" if personne['genre']==1 else ''}}>homme</option>
		<option value="2" {{"selected" if personne['genre']==2 else ''}}>femme</option>
	</select>

	<label for="nom">Nom</label>
	<input type="text" name="nom" value="{{personne['nom']}}"/>

	<label for="prenom">Prénom</label>
	<input type="text" name="prenom" value="{{personne['prenom']}}"/>

	<label for="date_naissance">Date de naissance (jj/mm/aaaa)</label>
% if personne['date_naissance'] == '' or not personne['date_naissance']:
	<input type="text" name="date_naissance" value=""/>
% else:
	<input type="text" name="date_naissance" value="{{personne['date_naissance'].strftime('%d/%m/%Y')}}"/>
% end

	<label for="societe">Société</label>
	<input type="text" name="societe" value="{{personne['societe']}}"/>

	<label for="adresse">Adresse</label>
	<input type="text" name="adresse" value="{{personne['adresse']}}"/>

	<label for="code_postal">Code postal</label>
	<input type="text" name="code_postal" value="{{personne['code_postal']}}"/>

	<label for="ville">Ville</label>
	<input type="text" name="ville" value="{{personne['ville']}}"/>

	<label for="telephone">Téléphone</label>
	<input type="text" name="telephone" value="{{personne['telephone']}}"/>

	<label for="courriel">Courriel</label>
	<input type="text" name="courriel" value="{{personne['courriel']}}"/>

	<label for="note">Note</label>
	<textarea name="note">{{personne['note']}}</textarea>

	<input value="enregistrer" type="submit"/>
</form>


</section>
% include('footer.tpl')
