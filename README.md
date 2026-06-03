# BookWorld

---

## Contexte

L'objectif de ce projet est de construire un pipeline de données permettant de consolider des ventes de livres provenant de plusieurs sources et de produire un indicateur simple : les ventes agrégées par pays.

Les données proviennent :
* d'un fichier CSV de ventes ;
* d'une base SQLite contenant des données de référence ;
* d'un site web utilisé pour récupérer les prix des livres ;
* d'une API de taux de change.

---

## Sources utilisées

### Fichier CSV
sales_raw.csv
Contient les ventes, les pays, les canaux de vente, les quantités et les informations clients.

### Base SQLite
bookworld_reference.db

Contient 3 tables :
* countries
* channels
* category_rules

### Site web
https://books.toscrape.com/
La première page est utilisée pour récupérer les prix des livres.

### API de taux de change
API Frankfurter utilisée pour convertir les revenus GBP en EUR.

---

## Exécution du pipeline
Lancer (bash) :
python3 pipeline.py

Le pipeline :
* charge les données de ventes (csv);
* charge les tables de référence (base sqlite);
* récupère les prix des livres (web scraping);
* récupère le taux de change GBP/EUR (api);
* enrichit les ventes ;
* calcule les revenus ;
* produit la table sales_by_country ;
* crée la base finale.

---

## Base finale
bookworld_final.db
Où se trouve la lable principale sales_by_country

Colonnes :
* country_code
* country_name
* total_orders
* total_quantity
* total_revenue_gbp
* total_revenue_eur

---

## API
Lancer (bash) :
python3 api.py

Endpoints disponibles :
* GET /health (Vérification de l'API)
* GET /sales-by-country (Ventes par pays)

---

## Authentification

L'accès à l'API est protégé par une clé (TOKEN) : read4you_read4ever

http://127.0.0.1:5000/health?key=read4you_read4ever
http://127.0.0.1:5000/sales-by-country?key=read4you_read4ever

---

## Organisation des fichiers
pipeline.py
api.py
queries.sql
schema_final.sql

sales_raw.csv
bookworld_reference.db
bookworld_final.db

---

## RGPD

Les colonnes customer_first_name et customer_last_name sont présentes dans les données sources mais ne sont pas conservées dans la base finale. La base finale contient uniquement des données agrégées par pays.
