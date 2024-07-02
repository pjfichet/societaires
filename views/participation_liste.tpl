% include('header.tpl')

<section>
	<h3>Participations</h3>
<table>
	<tr>
		<th>Date</th>
		<th>Prenom</th>
		<th>Nom</th>
		<th>Événement</th>
		<th>Provision</th>
		<th>Participation</th>
		<th>Total provisions</th>
		<th>Total capital</th>
		<th></th>
	</tr>
% provision = 0
% capital = 0
% for participation in participations:
	% capital += (participation['capital'])
	% provision += participation['provision']
	<tr>
		<td>{{participation['date'].strftime("%d/%m/%Y")}}</td>
		<td>{{participation['prenom']}}</td>
		<td>{{participation['nom']}}</td>
		<td>{{participation['evenement']}}</td>
		<td>{{participation['provision']}}&nbsp;€</td>
		<td>{{participation['capital']}}&nbsp;€</td>
		<td>{{provision}}&nbsp;€</td>
		<td>{{capital}}&nbsp;€</td>
		<td><a href="{{url}}/personne/participation/{{participation['personne']}}">info</a></td>
	</tr>
% end
</table>

</section>
% include('footer.tpl')
