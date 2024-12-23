create table if not exists saves (
    id integer primary key autoincrement,
    name varchar(26),
    created_at timestamp default CURRENT_TIMESTAMP,
    last_update timestamp default CURRENT_TIMESTAMP
);

create table if not exists dungeons (
    id integer primary key autoincrement,
    name varchar(100),
    save_id integer not null,
    foreign key (save_id) references saves (id)
);

create table if not exists floors (
    id integer primary key autoincrement,
    floor_id integer not null,
    dungeon_id integer not null,
    seed integer not null,
    foreign key (dungeon_id) references dungeons (id)
);

create table if not exists save_data (
    id integer primary key autoincrement,
    save_id integer not null,
    current_dungeon integer not null,
    current_floor integer not null,
    level integer not null,
    health integer not null,
    foreign key (save_id) references saves (id),
    foreign key (current_dungeon) references dungeons (id),
    foreign key (current_floor) references floors (floor_id)
);