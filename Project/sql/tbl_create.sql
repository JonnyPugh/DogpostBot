/*
This file creates the tables in the database.
Tables (formatted "<table name>: <field1>, <field2>, etc."):
Posts: time, hash, filename, source, id
Sources: id, type, time
*/

create table Posts (time timestamp not null default current_timestamp unique, hash varchar(16) not null primary key, filename varchar(255) not null, source varchar(16), id varchar(16) not null unique);
create table Sources (id varchar(16) not null primary key, type enum("page", "group") not null, time timestamp not null default '1970-01-01 00:00:01');
