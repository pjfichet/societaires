% include('header.tpl')
<section>
	<h3>Courriels</h3>
<a class="button" href="{{url}}/courriel/nouveau">Nouveau</a>
<table>
	<tr>
		<th>Date</th>
		<th>Sujet</th>
		<th>Destinataires</th>
		<th>Statut</th>
		<th></th>
	</tr>
% for courriel in courriels:
	<tr>
		<td>{{courriel['date'].strftime('%d/%m/%Y')}}</td>
		<td>{{courriel['sujet']}}</td>
		<td>{{courriel['envois']}}</td>
		<td><span class="{{courriel['statut']}}">{{courriel['statut']}}</span></td>
		<td><a href="{{url}}/courriel/item/{{courriel['uid']}}">Éditer</a></td>
	</tr>
% end
</table>
</section>
% include('footer.tpl')
