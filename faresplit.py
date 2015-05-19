from flask import Flask, request, g, redirect, url_for, render_template, flash
from sqlite3 import dbapi2 as sqlite3

import farespliter


SECRET_KEY='development key'
DEBUG = True
DATABASE = "/tmp/faresplit.db"


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar("FLASKR_SETTINGS", silent=True)


def init_database():
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        with app.open_resource("schema.sql", mode="r") as f:
            connection.cursor().executescript(f.read())


def get_database_connection():
    if not hasattr(g, "database_connection"):
        g.database_connection = sqlite3.connect(app.config["DATABASE"])
    return g.database_connection


@app.teardown_appcontext
def close_database_connection(exception):
    if hasattr(g, "database_connection"):
        g.database_connection.close()


@app.route("/")
def index():
    connection = get_database_connection()

    cursor = connection.execute("select * from transactions order by id desc")
    transactions = cursor.fetchall()

    return render_template("index.html", transactions=transactions)


@app.route("/post_transaction", methods=["POST"])
def post_transaction():
    connection = get_database_connection()

    connection.execute("insert into transactions (payer, payee, amount) values (?, ?, ?)",
            [request.form["payer"], request.form["payee"], request.form["amount"]])
    connection.commit()

    flash("Transaction was successfully posted.")

    return redirect(url_for("index"))


@app.route("/get_transaction", methods=["GET"])
def get_transaction():
    connection = get_database_connection()

    cursor = connection.execute("select * from transactions")
    transactions = cursor.fetchall()

    transactions = [farespliter.Transaction(transaction[1], transaction[2], transaction[3]) for transaction in transactions]
    transactions = farespliter.Farespliter().faresplit(transactions)
    transactions = [(transaction.payer, transaction.payee, str(transaction.amount)) for transaction in transactions]

    connection.executemany("insert into transactions (payer, payee, amount) values (?, ?, ?)",
            transactions)
    connection.commit()

    flash("Transaction was successfully getted.")

    return redirect(url_for("index"))


@app.route("/clear_transaction", methods=["GET"])
def clear_transaction():
    connection = get_database_connection()

    cursor = connection.execute("delete from transactions")
    connection.commit()

    flash("Transaction was successfully cleared.")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
