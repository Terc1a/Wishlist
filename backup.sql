BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "wishlist_wish" (
	"id"	integer NOT NULL,
	"item_name"	varchar(200) NOT NULL,
	"item_description"	text NOT NULL,
	"item_url"	varchar(200) NOT NULL,
	"item_price"	real NOT NULL,
	"item_image"	varchar(100),
	"created_at"	datetime NOT NULL,
	"wishlist_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("wishlist_id") REFERENCES "wishlist_wishlist"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "wishlist_wishlist" (
	"id"	integer NOT NULL,
	"title"	varchar(200) NOT NULL,
	"description"	text NOT NULL,
	"created_at"	datetime NOT NULL,
	"user_id"	integer NOT NULL,
	"likes"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO "wishlist_wish" VALUES (3,'Кейс для наушников nothing','Оранжевый или белый, они крутые','https://ozon.ru/t/m8916vk',239.0,'images/7117859111.webp','2025-05-27 18:30:48.249295',1);
INSERT INTO "wishlist_wish" VALUES (4,'Вишневый чай','Шу Пуэр, очень хочется попробовать...','https://ozon.ru/t/L4EA1xe',293.0,'images/чай.jpg','2025-05-27 18:34:20.963385',1);
INSERT INTO "wishlist_wish" VALUES (5,'Сумка на плечо','Хочется белую или серую...','https://ozon.ru/t/GN8qzh8',775.0,'images/сумощке.jpg','2025-05-27 18:36:08.639481',1);
INSERT INTO "wishlist_wish" VALUES (6,'Наручные часы','Очень интересно попробовать SKMEI, говорят они мега классные. Серебристые кайф','https://ozon.ru/t/fcOLO3J',1220.0,'images/часы.jpg','2025-05-27 18:38:55.972526',1);
INSERT INTO "wishlist_wishlist" VALUES (1,'Дешевые хотелки','Тут будет все подряд с озона и не только','2025-05-27 18:29:09.852305',1,0);
CREATE INDEX IF NOT EXISTS "wishlist_wish_wishlist_id_d6b1f156" ON "wishlist_wish" (
	"wishlist_id"
);
CREATE INDEX IF NOT EXISTS "wishlist_wishlist_user_id_13f28b16" ON "wishlist_wishlist" (
	"user_id"
);
COMMIT;
