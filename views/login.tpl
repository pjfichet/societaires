<!DOCTYPE html>
<html lang="fr">
<head>
	<meta charset="utf-8"/>
	<title>Sociétaires</title>
	<link rel="stylesheet" href="{{url}}/style.css"/>
    <!-- script type="text/javascript" src="{{url}}/jquery.js"></script -->
    <!-- script type="text/javascript" src="{{url}}/script.js"></script -->
</head>
<body>

<header>
	<h1>Sociétaires</h1>
</header>

<section>
	<form class="form" action="{{url}}/" method="post" id="login">
		<label for="prenom">Prénom</label>
		<input type="text" name="prenom"/>
		<label for="nom">Nom</label>
		<input type="text" name="nom"/>
		<label for="password">Mot de passe</label>
		<input type="password" name="password"/>
		<label></label>	
		<input value="Entrer" type="submit"/>
	</form>
%end
</section>
% include('footer.tpl')
