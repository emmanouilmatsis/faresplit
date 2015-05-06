drop table if exists transactions;
create table transactions (
    id integer primary key autoincrement,
    payer text not null,
    payee text not null,
    amount text not null
);
