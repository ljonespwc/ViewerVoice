from flask import current_app, g
import psycopg2
import os
import re
import urllib.parse


# def get_db():
#     if "db" not in g:
#         hostname = 'localhost'
#         username = 'postgres'
#         password = 'Porsche911'
#         database = 'youtuber'
#         conn = psycopg2.connect(
#             host=hostname, user=username, password=password, dbname=database)
#         conn.autocommit = True
#         g.db = conn.cursor()
#     return g.db


def get_db():
    if "db" not in g:
        DATABASE_URI = os.getenv("DATABASE_URI")
        parsed_uri = urllib.parse.urlparse(DATABASE_URI)
        username = parsed_uri.username
        password = parsed_uri.password
        host = parsed_uri.hostname
        port = parsed_uri.port
        database = parsed_uri.path[1:]
        conn = psycopg2.connect(
            host=host, user=username, password=password, dbname=database, port=port
        )
        conn.autocommit = True
        g.db = conn.cursor()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
