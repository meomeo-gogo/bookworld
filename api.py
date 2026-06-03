from flask import Flask, jsonify, request
import sqlite3
import pandas as pd

app = Flask(__name__)

TOKEN = "read4you_read4ever"

def check_token():
    key = request.args.get("key")

    if key != TOKEN:
        return False

    return True


@app.route("/health", methods=["GET"])
def health():

    if not check_token():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"status": "API is running"})


@app.route("/sales-by-country", methods=["GET"])
def get_sales_by_country():

    if not check_token():
        return jsonify({"error": "Unauthorized"}), 401

    conn = sqlite3.connect("bookworld_final.db")

    df = pd.read_sql_query(
        "SELECT * FROM sales_by_country",
        conn
    )

    conn.close()

    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)