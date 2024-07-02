% include('header.tpl')
<section>
	<h3>Courriel</h3>
<a class="button" href="{{url}}/courriel">Liste</a>

<ul>
% courriel = envois[0]
	<li>Statut: <span class="{{courriel['statut']}}">{{courriel['statut']}} ({{courriel['pid']}})</span></li>
	<li>Sujet: {{courriel['sujet']}}</li>
	<li>Pièce jointe: <a href="{{url}}/fichiers/{{courriel['fichier']}}">{{courriel['fichier']}}</a></li>
	<li>Destinataires: {{courriel['envois']}}</li>

</ul>
<p>
% for line in courriel['message'].split('\n'):
	{{line}}<br/>
% end
</p>
<table>
	<tr>
		<th>Prénom</th>
		<th>Nom</th>
		<th>Courriel</th>
		<th>Date</th>
		<th>Statut</th>
	</tr>
% for envoi in envois:
	<tr>
		<td>{{envoi['prenom']}}</td>
		<td>{{envoi['nom']}}</td>
		<td>{{envoi['courriel']}}</td>
% if envoi['horodate'] is not None:
		<td>{{envoi['horodate'].strftime('%d/%m/%Y %H:%M:%S')}}</td>
% else:
	<td>non envoyé</td>
% end
		<td><span class="{{envoi['statut']}}">{{envoi['statut']}}</span></td>
	</tr>
% end
</table>
<a class="button" href="{{url}}/courriel/supprimer/{{courriel['uid']}}">Supprimer</a>
<a class="button" href="{{url}}/courriel/envoyer/{{courriel['uid']}}">Envoyer</a>
</section>
% include('footer.tpl')
