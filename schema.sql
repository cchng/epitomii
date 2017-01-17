-- drop table if exists entries;
-- create table entries (
--   id integer primary key autoincrement,
--   'url' text not null
-- );


create table posts (
       id integer primary key autoincrement,
       'title' text not null,
       'filepath' text not null,
       'jam' int
);
