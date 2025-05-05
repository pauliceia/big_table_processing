--(a) Corrigir as coordenadas (x,y) de todos os places que estão
--no sistema métrico. Exemplo: o place de número 200 deve estar a
--200 metros do início da rua.

--------------------------------------------------

CREATE OR REPLACE FUNCTION saboya_geometry(streetId integer, numberPlace Float)
    RETURNS text
AS
$BODY$
DECLARE
    zeroGeom geometry;
    streetGeom geometry;
    oldGeomPlace text;
    streetSize Float;
    startPoint geometry;
    newGeom geometry;
    newStreetGeom geometry;
    fraction Float;
    equals boolean;
BEGIN
    RAISE NOTICE 'Processando streetId: %, numberPlace: %', streetId, numberPlace;

    -- Busca a geometria do local com número 0 para referência
    SELECT places.geom INTO zeroGeom
    FROM places_pilot_area AS places
    INNER JOIN streets_pilot_area AS street ON places.id_street = street.id
    WHERE places.number = 0 AND street.id = streetId
    ORDER BY date DESC
    LIMIT 1;
    RAISE NOTICE 'zeroGeom: %', ST_AsText(zeroGeom);

    -- Busca e une as geometrias da rua, filtrando por tipos de linha
    SELECT ST_LineMerge(geom) INTO streetGeom
    FROM streets_pilot_area
    WHERE id = streetId AND ST_GeometryType(geom) IN ('ST_LineString', 'ST_MultiLineString');
    RAISE NOTICE 'streetGeom (após LineMerge e filtro): %', ST_AsText(streetGeom);
    RAISE NOTICE 'Tipo de streetGeom: %', ST_GeometryType(streetGeom);

    -- Calcula o comprimento da rua
    SELECT ST_Length(ST_Transform(geom, 29100)) INTO streetSize
    FROM streets_pilot_area
    WHERE id = streetId;
    RAISE NOTICE 'streetSize: %', streetSize;

    -- Busca o ponto inicial da rua
    SELECT ST_StartPoint(ST_LineMerge(geom)) INTO startPoint
    FROM streets_pilot_area
    WHERE id = streetId AND ST_GeometryType(geom) IN ('ST_LineString', 'ST_MultiLineString');
    RAISE NOTICE 'startPoint: %', ST_AsText(startPoint);

    -- Verifica se o ponto inicial está contido em um buffer ao redor da geometria do número 0
    SELECT ST_Contains(
        (SELECT ST_Buffer(ST_StartPoint(ST_LineMerge(geom)), 0.0002) FROM streets_pilot_area WHERE id = streetId AND ST_GeometryType(geom) IN ('ST_LineString', 'ST_MultiLineString')),
        zeroGeom
    ) INTO equals;
    RAISE NOTICE 'equals: %', equals;

    -- Calcula o ponto interpolado com base na direção da rua
    IF streetGeom IS NOT NULL AND ST_GeometryType(streetGeom) = 'ST_LineString' AND streetSize > 0 THEN
        fraction := numberPlace / streetSize;
        fraction := GREATEST(0, LEAST(1, fraction)); -- Garante que a fração esteja entre 0 e 1
        SELECT ST_LineInterpolatePoint(streetGeom, fraction) INTO newGeom;
        RAISE NOTICE 'newGeom (caso equals TRUE), fraction: %, newGeom: %', fraction, ST_AsText(newGeom); -- CORRIGIDO
    ELSE
        newGeom := NULL;
        RAISE NOTICE 'newGeom definido como NULL (streetGeom não é LINESTRING ou é NULL ou streetSize <= 0)';
    END IF;

    IF newGeom IS NULL THEN
        IF streetGeom IS NOT NULL AND ST_GeometryType(streetGeom) = 'ST_LineString' AND streetSize > 0 THEN
            SELECT ST_Reverse(ST_GeometryN(ST_LineMerge(geom),1)) INTO newStreetGeom
            FROM streets_pilot_area
            WHERE id = streetId AND ST_GeometryType(geom) IN ('ST_LineString', 'ST_MultiLineString');
            RAISE NOTICE 'newStreetGeom (após Reverse e GeometryN): %', ST_AsText(newStreetGeom);
            RAISE NOTICE 'Tipo de newStreetGeom: %', ST_GeometryType(newStreetGeom);
            IF newStreetGeom IS NOT NULL AND ST_GeometryType(newStreetGeom) = 'ST_LineString' THEN
                fraction := numberPlace / streetSize;
                fraction := GREATEST(0, LEAST(1, fraction)); -- Garante que a fração esteja entre 0 e 1
                SELECT ST_LineInterpolatePoint(newStreetGeom, fraction) INTO newGeom;
                RAISE NOTICE 'newGeom (caso equals FALSE), fraction: %, newGeom: %', fraction, ST_AsText(newGeom); -- CORRIGIDO
            ELSE
                newGeom := NULL;
                RAISE NOTICE 'newGeom definido como NULL (newStreetGeom não é LINESTRING ou é NULL)';
            END IF;
        END IF;
    END IF;

    -- Retorna a geometria como texto, se não for nula
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
