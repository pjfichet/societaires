% include('header.tpl')
<section>
<p>
	<a class="button" href="{{url}}/societaires.troff">export troff</a>
	<a class="button" href="{{url}}/societaires.sqlite">export sqlite</a>
	<a class="button" href="{{url}}/societaires.fods">export libreoffice</a>
</p>
<p>
<form class="inline" action="{{url}}/historique" method="post">
	<label for="date">Historique en date du:</label>
	<input type="text" name="date"/>
	<input value="Afficher" type="submit"/>
</form>
</p>

	<h3>Historique</h3>
% for row in data:
<h4>Au {{row['date_fin'].strftime('%d %B %Y')}}&nbsp;:</h4>
<p>
Au {{row['date_fin'].strftime('%d %B %Y')}}, la scic
se compose de {{row['societaires']}} sociétaires possédant {{row['part']}} parts sociales
constituant un capital de {{row['capital']}}&nbsp;€.
Le sociétariat se répartit ainsi:
<ul>
	<li>{{row['femmes']}} femmes, {{row['hommes']}} hommes,
	% if row['autres'] > 0:
		et {{row['autres']}} au genre non défini,
	%end
	</li>
	<li>{{row['mineurs']}} mineurs, {{row['adultes']}} adultes, {{row['aines']}} aînés (+64 ans),</li>
	<li>{{row['personnes_2']}} salariés possédant {{row['part_2']}} parts, soit {{row['capital_2']}}&nbsp;€ de capital,</li>
	<li>{{row['personnes_3']}} bénévoles possédant {{row['part_3']}} parts, soit {{row['capital_3']}}&nbsp;€ de capital,</li>
	<li>{{row['personnes_4']}} clients possédant {{row['part_4']}} parts, soit {{row['capital_4']}}&nbsp;€ de capital,</li>
	<li>{{row['personnes_5']}} partenaires possédant {{row['part_5']}} parts, soit {{row['capital_5']}}&nbsp;€ de capital.</li>
	% if row['personnes_6'] > 0:
		<li>{{row['personnes_6']}} personnes sortent de la coopérative et attendent la validation des comptes par l'assemblée générale pour que 	leur capital libéré.
		% if row['capital_6'] > 0:
		Elles possèdent toujours un capital de {{row['capital_6']}}&nbsp;€ au sein de la coopérative.
		% end
		</li>
	%end 
	% if row['personnes_1'] > 0:
		<li>{{row['personnes_1']}} personnes sont en attente de validation par l'assemblée générale pour intégrer la coopérative.
		Elles apportent un capital de {{row['provision_1']}}&nbsp;€.</li>
	% end
	% if row['personnes_0'] > 0:
		<li>{{row['personnes_0']}} personnes ont quitté la coopérative depuis sa création.</li>
	% end 
</ul>
</p>
%end

</section>
% include('footer.tpl')
