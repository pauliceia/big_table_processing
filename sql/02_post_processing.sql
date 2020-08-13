ALTER TABLE public.${table_name} ADD COLUMN geom geometry(Point, 4326);

UPDATE public.${table_name} SET geom = ST_SetSRID(cordinate, 4326);

ALTER TABLE public.${table_name} DROP COLUMN cordinate;

ALTER TABLE public.${table_name} ALTER COLUMN index TYPE integer;

ALTER TABLE public.${table_name} ALTER COLUMN id_street TYPE integer;

ALTER TABLE public.${table_name} ALTER COLUMN number TYPE float USING number::double precision;

ALTER TABLE public.${table_name} ALTER COLUMN original_n TYPE VARCHAR(255);

ALTER TABLE public.${table_name} ALTER COLUMN source TYPE VARCHAR(255);

ALTER TABLE public.${table_name} ALTER COLUMN author TYPE VARCHAR(255);

ALTER TABLE public.${table_name} ALTER COLUMN date TYPE VARCHAR(255);

ALTER TABLE public.${table_name} ALTER COLUMN first_day TYPE integer USING first_day::integer;

ALTER TABLE public.${table_name} ALTER COLUMN first_month TYPE integer USING first_month::integer;

ALTER TABLE public.${table_name} ALTER COLUMN first_year TYPE integer USING first_year::integer;

ALTER TABLE public.${table_name} ALTER COLUMN last_day TYPE integer USING last_day::integer;

ALTER TABLE public.${table_name} ALTER COLUMN last_month TYPE integer USING last_month::integer;

ALTER TABLE public.${table_name} ALTER COLUMN last_year TYPE integer USING last_year::integer;

ALTER TABLE public.${table_name} ADD CONSTRAINT ${table_name}_constraint_fk_id_street FOREIGN KEY (id_street) REFERENCES public.streets_pilot_area (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE public.${table_name} RENAME index TO id;

ALTER TABLE public.${table_name} ADD CONSTRAINT ${table_name}_pk_id PRIMARY KEY (id);
