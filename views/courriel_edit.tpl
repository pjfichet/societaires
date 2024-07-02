% include('header.tpl')
<section>
<form class="form" action="{{url}}/courriel/nouveau" method="post" enctype="multipart/form-data">

	<label for="sujet">Sujet</label>
	<input type="text" name="sujet" value=""/>

	<label for="fichier">Fichier</label>
	<input type="file" name="fichier"/>

	<label for="destinataires">Destinataires</label>
	<select name="destinataires">
		<option value="test">{{courriel['courriel']}}</option>
		<option value="societaires">societaires et nouveaux</option>
	</select>
	<label for="message">Message</label>
	<textarea name="message"></textarea>
	<input value="enregistrer" type="submit"/>
</form>
</section>
% include('footer.tpl')
