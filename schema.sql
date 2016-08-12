drop table if exists entries;
create table rent_payment (
	room_id integer primary key autoincrement,
	rent_price integer not null,
	pay_date datetime not null,
	water_fee real not null
);