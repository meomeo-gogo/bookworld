'Ces requetes contiennent des filtres (WHERE)'

SELECT *
FROM countries
WHERE is_active = 1;


SELECT *
FROM channels
WHERE is_active = 1;


SELECT *
FROM category_rules
WHERE is_active = 1;


'Cette requête permet d enrichir les ventes en ajoutant le nom du pays'
SELECT
    country_code,
    country_name
FROM countries
WHERE is_active = 1;
