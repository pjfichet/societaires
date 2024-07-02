% include('header.tpl')

<section>
	<h3>Droits d'accès</h3>
<table>
	<tr>
		<th>Prenom</th>
		<th>Nom</th>
		<th>Droits</th>
		<th></th>
	</tr>
% for personne in personnes:
	<tr>
		<td>{{personne['prenom']}}</td>
		<td>{{personne['nom']}}</td>
		<td>{{personne['droit']}}</td>
		<td><a href="{{url}}/personne/droit/{{personne['uid']}}">Modifier</a></td>
	</tr>
% end
</table>
</section>
% include('footer.tpl')
