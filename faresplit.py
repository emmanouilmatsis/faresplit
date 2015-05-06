import os
import time
import datetime
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import farespliter


DATABASE="/tmp/faresplit.db"
DEBUG=True
SECRET_KEY="development key"
USERNAME="admin"
PASSWORD="default"


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar("FLASKR_SETTINGS", silent=True)


def init_db():
    with sqlite3.connect(app.config["DATABASE"]) as db:
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())


def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = sqlite3.connect(app.config["DATABASE"])
        #g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/")
def index():
    db = get_db()

    cur = db.execute("select * from transactions order by id desc")
    transactions = cur.fetchall()

    return render_template("index.html", transactions=transactions)


@app.route("/post_transaction", methods=["POST"])
def post_transaction():
    db = get_db()

    db.execute("insert into transactions (payer, payee, amount) values (?, ?, ?)",
            [request.form["payer"], request.form["payee"], request.form["amount"]])
    db.commit()

    flash("Transaction was successfully posted.")

    return redirect(url_for("index"))


@app.route("/get_transaction", methods=["GET"])
def get_transaction():
    db = get_db()

    cur = db.execute("select * from transactions")
    transactions = cur.fetchall()

    transactions = [farespliter.Transaction(transaction[1], transaction[2], transaction[3]) for transaction in transactions]
    transactions = farespliter.Farespliter().faresplit(transactions)
    transactions = [(transaction.payer, transaction.payee, str(transaction.amount)) for transaction in transactions]

    db.executemany("insert into transactions (payer, payee, amount) values (?, ?, ?)",
            transactions)
    db.commit()

    flash("Transaction was successfully getted.")

    return redirect(url_for("index"))


@app.route("/clear_transaction", methods=["GET"])
def clear_transaction():
    db = get_db()

    cur = db.execute("delete from transactions")
    db.commit()

    flash("Transaction was successfully cleared.")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
