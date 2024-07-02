% include('header.tpl')

<section>
<h3>Aide</h3>
<h4>Les participations</h4>
<p>Cette nouvelle interface répond au besoin de conserver l'évolution du
sociétariat au fil du temps. Dorénavant chaque personne a un historique
daté de «participations»: souscription, admission, achat de nouvelle
part sociale, changement de catégorie, démission, et remboursement.
Il faut donc, pour chacun de ces événements, créer une nouvelle
participation.</p>
<p>Les participations comprennent différent champs&nbsp;:
<ul>
	<li><b>date&nbsp;:</b> date de la signature du bulletin de
	souscription pour la souscription, date de l'assemblée générale
	pour l'admission, etc.</li>
	<li><b>événement&nbsp;:</b> à sélectionner dans la liste déroulante</li>
	<li><b>catégorie&nbsp;:</b> sélectionner parmi la liste déroulante ainsi:
		<ul>
			<li>«&nbsp;<i>nouveau</i>&nbsp;» lors de la remise du bulletin de souscription,</li>
			<li>la catégorie statutaire décidée en AG lors
		de l'admission («&nbsp;<i>salarié</i>&nbsp;»,
		«&nbsp;<i>bénévole</i>&nbsp;»,
		«&nbsp;<i>client</i>&nbsp;»,
		«&nbsp;<i>partenaire</i>&nbsp;»),</li>
			<li>«&nbsp;<i>sortant</i>&nbsp;» lorsque la personne annonce sa démission,</li>
			<li>et «&nbsp;<i>ancien</i>&nbsp;» lorsque le capital
		d'un sortant est traîté (remboursement ou don à la
		coopérative).</li>
		</ul>
	<li><b>provision&nbsp;:</b> le compte provision permet de
	comptabiliser les sommes versées ou les demandes de remboursement
	en attendant la décision de l'assemblée générale. Y indiquer
	par exemple +50€ lors de l'achat d'une part, et -50€ lors
	de la demande de remboursement d'une part.</li>
	<li><b>capital&nbsp;:</b> lorsqu'un sociétaire est admis
	par l'assemblée générale, le montant du compte provision
	devient du capital. De même, lorsque l'AG valide les comptes, le
	capital peut être remboursé aux sociétaires le demandant. Le
	champ capital est alors précisé, de la façon suivante: ce
	qu'on ajoute au capital, on le supprime du compte provision,
	et vice versa.</li>
	<li><b>parts&nbsp;:</b> le nombre de parts concernées par les
	opérations sur le capital. Indiquer 0 lorsque seul le compte
	«&nbsp;<i>provision</i>&nbsp;» est affecté.</li>
</ul>
<h4>Exemple</h4>
<p>On souhaite ajouter M. Jean Dupont. Il souscrit à un bulletin de
souscription le 1er janvier pour une part sociale, est admis en AG le
1er février, achète une nouvelle part sociale le 1er mars, démissionne
le 1er avril et est remboursé le 1er juin.</p>
<ul>
	<li>aller dans <a href="{{url}}/personne">personnes</a> et cliquer sur <b>nouveau</b>,</li>
	<li>remplir l'état civil et les coordonnées, cliquer sur <b>enregistrer</b>,</li>
	<li>cliquer sur <b>participation</b>, <b>nouvelle participation</b> pour enregistrer sa souscription.
	Selectionner l'événement «&nbsp;<i>souscription</i>&nbsp;», catégorie «&nbsp;<i>nouveau</i>&nbsp;»,
	la date du 1er janvier, provision 50€, capital 0, parts 0.
	<b>Enregistrer</b>.</li>
	<li>cliquer sur <b>participation</b>, <b>nouvelle participation</b> pour enregistrer son admission.
	Selectionner l'événement «&nbsp;<i>admission</i>&nbsp;», catégorie «&nbsp;<i>client</i>&nbsp;»,
	la date du 1er février, provision -50€, capital 50€, parts 1.
	<b>Enregistrer</b>.</li>
	<li>cliquer sur <b>participation</b>, <b>nouvelle participation</b> pour enregistrer son augmentation de capital.
	Selectionner l'événement «&nbsp;<i>augmentation de capital</i>&nbsp;», catégorie «&nbsp;<i>client</i>&nbsp;»,
	la date du 1er mars, provision 0, capital 50€, parts 1.
	<b>Enregistrer</b>.</li>
	<li>cliquer sur <b>participation</b>, <b>nouvelle participation</b> pour enregistrer sa démission.
	Selectionner l'événement «&nbsp;<i>démission</i>&nbsp;», catégorie «&nbsp;<i>sortant</i>&nbsp;»,
	la date du 1er avril, provision -100, capital 0€, parts 0.
	<b>Enregistrer</b></li>
	<li>cliquer sur <b>participation</b>, <b>nouvelle participation</b> pour enregistrer son remboursement.
	Selectionner l'événement «&nbsp;<i>remboursement</i>&nbsp;», catégorie «&nbsp;<i>ancien</i>&nbsp;»,
	la date du 1er juin, provision +100, capital -100€, parts 2.
	<b>Enregistrer</b></li>
	<li>Au final, les comptes participation et capital sont bien à 0.</li>
</ul>
</section>
% include('footer.tpl')
