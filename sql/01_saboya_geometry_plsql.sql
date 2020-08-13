--(a) Corrigir as coordenadas (x,y) de todos os places que estão
--no sistema métrico. Exemplo: o place de número 200 deve estar a
--200 metros do início da rua.

--------------------------------------------------

CREATE OR REPLACE FUNCTION saboya_geometry(streetId integer, numberPlace Float)
	RETURNS text
AS
$BODY$
DECLARE
	zeroGeom text;
	streetGeom text;
	oldGeomPlace text;
	streetSize Float;
	startPoint text;
	newGeom text;
	newStreetGeom text;
	equals boolean;
BEGIN
	zeroGeom := (SELECT places.geom FROM places_pilot_area AS places INNER JOIN streets_pilot_area AS street ON places.id_street = street.id WHERE places.number = 0 AND street.id = streetId ORDER BY date DESC LIMIT 1);
	streetGeom := (SELECT  ST_LineMerge(geom) FROM streets_pilot_area WHERE id = streetId);
	streetSize := (SELECT ST_Length(ST_Transform(geom, 29100)) FROM streets_pilot_area where id = streetId);
	startPoint := (SELECT  ST_StartPoint(ST_LineMerge(geom)) FROM streets_pilot_area WHERE id = streetId);
	equals := (SELECT ST_Contains(startPt.geom,zeropt.geo) As ST_Contains FROM ( SELECT ST_Buffer(ST_StartPoint(ST_LineMerge(geom)), 0.0002) As geom FROM streets_pilot_area WHERE id = streetId ) As startPt, ( SELECT places.geom as geo FROM places_pilot_area AS places  INNER JOIN streets_pilot_area AS street ON places.id_street = street.id WHERE places.number = 0 AND street.id = streetId ORDER BY date DESC LIMIT 1 ) As zeroPt);
	IF equals = TRUE THEN
		newGeom := (SELECT ST_LineInterpolatePoint(streetGeom, numberPlace/streetSize));
	ELSE
		newStreetGeom := (SELECT  ST_Reverse(ST_GeometryN(ST_LineMerge(geom),1)) FROM streets_pilot_area WHERE id = streetId);
		newGeom := (SELECT ST_LineInterpolatePoint(newStreetGeom, numberPlace/streetSize));
	END IF;
	IF newGeom IS NOT NULL THEN
		RETURN st_astext(newGeom);
	ELSE
		RETURN NULL;
	END IF;
END;
$BODY$
LANGUAGE plpgsql;

--------------------------------------------------

-- select id, street.name, saboya_geometry(street.id,0) from  streets_pilot_area AS street;

--------------------------------------------------
