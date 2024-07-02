% include('header.tpl')
<section>
% personne = participations[0]
<h3>Participations de {{personne['prenom']}} {{personne['nom']}}</h3>
<table>
	<tr>
		<th>Date</th>
		<th>Événement</th>
		<th>Catégorie</th>
		<th>Provision</th>
		<th>Capital</th>
		<th></th>
	</tr>

% provision = 0
% capital = 0
% for participation in participations:
	%if participation['date']:
		% provision += participation['provision']
		% capital += participation['capital']
		<tr>
			<td>{{participation['date'].strftime("%d/%m/%Y")}}</td>
			<td>{{participation['evenement']}}</td>
			<td>{{participation['categorie']}}</td>
			<td>{{participation['provision']}}&nbsp;€</td>
			<td>{{participation['capital']}}&nbsp;€</td>
			<td><a href="{{url}}/participation/edit/{{participation['uid']}}">Modifier</a></td>
		</tr>
	% end
	%end
		<tr>
			<td></td>
			<td></td>
			<td><b>total</b></td>
			<td><b>{{provision}}&nbsp;€</b></td>
			<td><b>{{capital}}&nbsp;€</b></td>
			<td></td>
</table>

<div>
<p>
	<a class="button" href="{{url}}/personne/item/{{personne['personne_uid']}}">Fiche</a>
	<a class="button" href="{{url}}/personne/participation/nouveau/{{personne['personne_uid']}}">Nouvelle participation</a>
</p>
</div>


</section>
% include('footer.tpl')
