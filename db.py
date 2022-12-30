from flask import current_app, g
import psycopg2


def get_db():
    if "db" not in g:
        hostname = 'localhost'
        username = 'postgres'
        password = 'Porsche911'
        database = 'youtuber'
        conn = psycopg2.connect(
            host=hostname, user=username, password=password, dbname=database)
        conn.autocommit = True
        g.db = conn.cursor()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
