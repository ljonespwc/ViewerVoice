from flask_login import UserMixin
from db import get_db
import psycopg2


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, board_id):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.board_id = board_id

    @staticmethod
    def get(user_id):
        db = get_db()
        db.execute('''
                    SELECT * FROM users WHERE id = %s
                    ''', (user_id,))
        if db.rowcount > 0:
            row = db.fetchone()
            user = User(id_=row[0], name=row[1], email=row[2],
                        profile_pic=row[3], board_id=row[5])
            return user
        else:
            return None

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        try:
            db.execute('''
                    INSERT INTO users (id, name, email, profile_pic, last_login) VALUES(%s,%s,%s,%s,timestamp '2020-01-01 00:00:00.001') ON CONFLICT (email) DO NOTHING
                    ''', (id_, name, email, profile_pic),)
        except psycopg2.OperationalError as error:
            print("Failed to update table", error)
            pass

    @staticmethod
    def update(email):
        db = get_db()
        try:
            db.execute('''
                    UPDATE users SET last_login=CURRENT_TIMESTAMP where email=%s
                    ''', (email,))
        except psycopg2.OperationalError as error:
            print("Failed to update table", error)
            pass
