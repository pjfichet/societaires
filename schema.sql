-- .load ./icu.so
pragma foreign_keys = 1;
pragma journal_mode = 'wal';

create table if not exists personne (
	uid integer not null primary key,
	nature integer not null,
	genre integer not null,
	nom varchar(255) not null,
	prenom varchar(255) not null,
	date_naissance date not null,
	societe varchar(255),
	adresse varchar(255) not null,
	code_postal varchar(255) not null,
	ville varchar(255) not null,
	telephone varchar(255),
	courriel varchar(255),
	secret varchar(255),
	droit integer not null,
	note text,
	foreign key (nature) references nature (uid),
	foreign key (genre) references genre (uid),
	foreign key (droit) references droit (uid)
);

create table if not exists nature (
	uid integer not null primary key,
	nature varchar(255) not null
);

insert into nature (uid, nature) values
	(1, 'physique'),
	(2, 'morale')
;

create table if not exists genre (
	uid integer not null primary key,
	genre varchar(255) not null
);

insert into genre (uid, genre) values
	(0, 'inconnu'),
	(1, 'masculin'),
	(2, 'féminin'),
	(9, 'sans objet')
;

create table if not exists droit (
	uid integer not null primary key,
	droit varchar(255) not null
);

insert into droit (uid, droit) values
	(0, 'aucun'),
	(1, 'données personnelles'),
	(2, 'personnes'),
	(3, 'participations'),
	(4, 'courriels'),
	(5, 'droits d''accès')
;

create table if not exists participation (
	uid integer not null primary key,
	personne integer not null,
	date date not null,
	evenement integer not null,
	categorie integer not null,
	provision integer,
	capital integer,
	part integer not null,
	foreign key (personne) references personne (uid),
	foreign key (evenement) references evenement (uid),
	foreign key (categorie) references categorie (uid)
);

create index participation_personne on participation (personne);
create index participation_categorie on participation (categorie);

create table if not exists evenement (
	uid integer not null primary key,
	evenement varchar (255) not null
);

insert into evenement (uid, evenement) values
	(0, 'autre'),
	(1, 'souscription'),
	(2, 'admission'),
	(3, 'changement de catégorie'),
	(4, 'augmentation de capital'),
	(5, 'diminution de capital'),
	(6, 'démission'),
	(7, 'remboursement')
	(8, 'don à la coopérative')
;

create table if not exists categorie (
	uid integer not null primary key,
	categorie varchar (255) not null
);

insert into categorie (uid, categorie) values
	(0, 'ancien'),
	(1, 'nouveau'),
	(2, 'salarié'),
	(3, 'bénévole'),
	(4, 'client'),
	(5, 'partenaire')
	(6, 'sortant')
;


create table if not exists courriel (
	uid integer not null primary key,
	pid integer not null,
	statut integer not null,
	date date not null,
	sujet varchar(255) not null,
	message text not null,
	fichier varchar(255),
	envois integer
);

create table if not exists envoi (
	uid integer not null primary key,
	personne integer not null,
	courriel integer not null,
	horodate datetime not null,
	statut integer not null,
	foreign key (personne) references personne (uid),
	foreign key (courriel) references courriel (uid) on delete cascade
);

create index envoi_personne on envoi (personne);	
create index envoi_courriel on envoi (courriel);

create table if not exists session (
	uid varchar(255) not null primary key,
	debut datetime not null,
	fin datetime not null,
	droit integer not null,
	personne integer not null,
	foreign key (personne) references personne (uid)
);

create index session_personne on session (personne);
