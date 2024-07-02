% include('header.tpl')
<section>
<p>
<form class="inline" action="{{url}}/personne/recherche" method="post">
	<input type="text" name="recherche"/>
	<input value="recherche" type="submit"/>
</form>

	<a class="button" href="{{url}}/personne/nouveau">nouveau</a>
</p>
<p>
<form class="inline" action="{{url}}/personne" method="post">
	<label for="date">Liste en date du:</label>
	<input type="text" name="date"/>
	<input value="Afficher" type="submit"/>
</form>
</p>

<h3>Personnes (au {{date.strftime('%d %B %Y')}})</h3>

<table>
	<tr>
		<th>Civ.</th>
		<th>Prénom</th>
		<th>Nom</th>
		<th>Société</th>
		<th>Courriel</th>
		<th>Catégorie</th>
		<th>Provision</th>
		<th>Capital</th>
		<th></th>
	</tr>
% for per in personnes:
	<tr  class="item">
		<td>{{"Mme" if per['genre']==2 else "M."}}</td>
		<td>{{per['prenom']}}</td>
		<td>{{per['nom']}}</td>
		<td>{{per['societe']}}</td>
		<td>{{per['courriel']}}</td>
		<td>{{per['categorie']}}</td>
		<td>{{per['provision']}}&nbsp;€</td>
		<td>{{per['capital']}}&nbsp;€</td>
		<td><a href="{{url}}/personne/item/{{per['uid']}}">info</a></td>
	</tr>
% end

</table>
</section>
% include('footer.tpl')
