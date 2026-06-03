'toutes ces requetes contiennent des filtres (WHERE) et des informations qui enrichissent le ficher pipeline (SELECT)'

SELECT *
FROM countries
WHERE is_active = 1;


SELECT *
FROM channels
WHERE is_active = 1;


SELECT *
FROM category_rules
WHERE is_active = 1;
