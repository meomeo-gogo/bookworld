import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup

# 1.1 Extraire les données depuis les différences sources
# fichier CSV : sales_raw.csv
def get_sales():
    try:
        df_sales = pd.read_csv("sales_raw.csv")

        print("df_sales chargé :", df_sales.shape)
        print(df_sales.head(3))
        print("--------------------")

        return df_sales

    except Exception as e:
        print("Erreur lors de la lecture du fichier sales_raw.csv :", e)
        return pd.DataFrame()


# table countries
def get_countries():
    try:
        conn = sqlite3.connect("bookworld_reference.db")

        query = """
        SELECT *
        FROM countries
        WHERE is_active = 1
        """

        df_countries = pd.read_sql_query(query, conn)

        conn.close()

        print("df_countries chargé :", df_countries.shape)
        print(df_countries.head(3))
        print("--------------------")

        return df_countries

    except Exception as e:
        print("Erreur lors de la lecture de countries :", e)
        return pd.DataFrame()


# table channels
def get_channels():
    try:
        conn = sqlite3.connect("bookworld_reference.db")

        query = """
        SELECT *
        FROM channels
        WHERE is_active = 1
        """

        df_channels = pd.read_sql_query(query, conn)

        conn.close()

        print("df_channels chargé :", df_channels.shape)
        print(df_channels.head(3))
        print("--------------------")

        return df_channels

    except Exception as e:
        print("Erreur lors de la lecture de channels :", e)
        return pd.DataFrame()


# table category_rules
def get_category_rules():
    try:
        conn = sqlite3.connect("bookworld_reference.db")

        query = """
        SELECT *
        FROM category_rules
        WHERE is_active = 1
        """

        df_category_rules = pd.read_sql_query(query, conn)

        conn.close()

        print("df_category_rules chargé :", df_category_rules.shape)
        print(df_category_rules.head(3))
        print("--------------------")

        return df_category_rules

    except Exception as e:
        print("Erreur lors de la lecture de category_rules :", e)
        return pd.DataFrame()


# scraping de la première page du catalogue
def get_books():
    try:
        url = "https://books.toscrape.com/"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        books = []

        articles = soup.find_all("article", class_="product_pod")

        for article in articles:

            title = article.h3.a["title"]

            price = article.find("p", class_="price_color").text
            price = price.replace("£", "")
            price = price.replace("Â", "")
            price = float(price)

            books.append({
                "book_name": title,
                "price_gbp": price
            })

        df_books = pd.DataFrame(books)

        print("df_books chargé :", df_books.shape)
        print(df_books.head(3))
        print("--------------------")

        return df_books

    except Exception as e:
        print("Erreur lors du scraping :", e)
        return pd.DataFrame()


# API Frankfurter
def get_exchange_rate():
    try:
        url = "https://api.frankfurter.app/latest?from=GBP&to=EUR"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        rate = data["rates"]["EUR"]

        print("Taux GBP -> EUR :", rate)
        print("--------------------")

        return rate

    except Exception as e:
        print("Erreur lors de la récupération du taux de change :", e)
        return None
    

# 2.1 Nettoyer, enrichir et agréger les données
def create_sales_by_country(df_sales, df_countries, df_books, rate):
    try:
        # merge avec df_books pour récupérer le prix
        df_sales_books = df_sales.merge(df_books, on="book_name", how="left")

        # Vérifier si prix = 0
        missing_prices = df_sales_books["price_gbp"].isna().sum()
        print("Nombre de ventes sans prix :", missing_prices)

        # merge avec df_countries 
        df_sales_country = df_sales_books.merge(df_countries[["country_code", "country_name"]], on="country_code", how="left")

        # Calcul du revenu en pounds
        df_sales_country["revenue_gbp"] = (
            df_sales_country["quantity"]
            * df_sales_country["price_gbp"]
            * (1 - df_sales_country["discount_rate"])
        )

        # Calcul du revenu en euros
        df_sales_country["revenue_eur"] = df_sales_country["revenue_gbp"] * rate

        # Agrégation par pays
        sales_by_country = df_sales_country.groupby(
            ["country_code", "country_name"],
            as_index=False
        ).agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("revenue_gbp", "sum"),
            total_revenue_eur=("revenue_eur", "sum")
        )

        print("sales_by_country créé :", sales_by_country.shape)
        print(sales_by_country.head())
        print("--------------------")

        return sales_by_country

    except Exception as e:
        print("Erreur lors de la création de sales_by_country :", e)
        return pd.DataFrame()
    

# 3.1 Créer la base finale en prenant en compte le RGPD
# etape 1 : créer le schema de la table dans schema_final.sql (dans terminal)
# etape 2 : excucte le schema_final.sql pour créer une table dans bookworld_final.db
def init_database():
    try:
        conn = sqlite3.connect("bookworld_final.db")

        with open("schema_final.sql", "r") as f:
            conn.executescript(f.read())

        conn.close()

        print("Base finale créée")

    except Exception as e:
        print("Erreur lors de la création de la base finale :", e)
    
# etape 3 : remplir la table dans bookworld_final.db par de df sales_by_country
def save_sales_by_country(sales_by_country):
    try:
        conn = sqlite3.connect("bookworld_final.db")

        print("Vérification RGPD : ok")
        # La base finale ne conserve pas les noms et prénoms des clients.
        # La table sales_by_country est agrégée par pays et ne contient aucune donnée personnelle

        sales_by_country.to_sql(
            "sales_by_country",
            conn,
            if_exists="append",
            index=False
        )

        conn.close()

        print("Table sales_by_country enregistrée dans bookworld_final.db")

    except Exception as e:
        print("Erreur lors de l'enregistrement de sales_by_country :", e)

# Execution pipeline       
if __name__ == "__main__":
    df_sales = get_sales()
    df_countries = get_countries()
    df_channels = get_channels()
    df_category_rules = get_category_rules()
    df_books = get_books()
    rate = get_exchange_rate()

    sales_by_country = create_sales_by_country(df_sales, df_countries, df_books, rate)
    
    init_database()
    save_sales_by_country(sales_by_country)