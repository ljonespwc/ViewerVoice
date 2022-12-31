from db import get_db
import psycopg2
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)


views = Blueprint("views", __name__)


@views.route("/", methods=['GET', 'POST'])
def index():
    db = get_db()
    board_id = ''
    board = ''
    if current_user.is_authenticated:
        if request.method == "POST":
            board = request.form.get('board')
            board = board.lower()
            if board == '' or len(board) < 3 or not board.isalpha():
                flash(
                    'Sorry, your URL snippet must be at least 3 characters and may contain letters only.', category="error")
            else:
                db.execute(
                    '''SELECT board_id FROM users WHERE board_id = %s''', (board,))
                board_exists = db.fetchone()
                if board_exists:
                    flash('Sorry, that board already exists. Try again.',
                          category="error")
                else:
                    db.execute('''
                    UPDATE users SET board_id=%s where id=%s
                        ''', (board, current_user.id))
                    flash('Board URL saved!', category="success")
                    board_id = board
        db.execute(
            '''SELECT board_id FROM users WHERE id = %s''', (current_user.id,))
        board_id = db.fetchone()[0]
        if not board_id:
            board_id = ''
    return render_template("home.html", board_id=board_id, board=board)


@views.route("/board/<board>")
def show_board(board):
    db = get_db()
    # check to see if board exists
    db.execute(
        '''SELECT board_id, id, name FROM users WHERE board_id = %s''', (board,))
    board_exists = db.fetchone()
    if not board_exists:
        flash('Sorry, there\'s no such board. Try again.',
              category="error")
        return render_template("posts_div.html")
    else:
        db.execute(
            '''SELECT text, to_char(date_created AT TIME ZONE 'GMT', 'Month DD, YYYY HH24:MI') || ' (GMT)' as date_created,
            users.name, post.id, author, users.profile_pic, users.board_id
            FROM post INNER JOIN users ON author = users.id WHERE post.board_id = %s''', (board,))
        posts = db.fetchall()
        db.execute(
            '''SELECT comment.text, to_char(comment.date_created AT TIME ZONE 'GMT', 'Month DD, YYYY HH24:MI') || ' (GMT)' as date_created,
            comment.author, comment.post_id, users.name, users.profile_pic
            FROM comment, users WHERE comment.author = users.id AND comment.board_id = %s''', (board,))
        comments = db.fetchall()
        db.execute(
            '''SELECT id, author, post_id FROM likes WHERE board_id = %s''', (board,))
        likes = db.fetchall()
        return render_template("posts_div.html", posts=posts, comments=comments, likes=likes, board=board, board_owner=board_exists)


@views.route("/create-post/<board>", methods=['GET', 'POST'])
@login_required
def create(board):
    if request.method == "POST":
        text = request.form.get('text')
        if not text:
            flash('Sorry, the question field cannot be empty.', category="error")
        else:
            db = get_db()
            db.execute('''
                        INSERT INTO post (text, author, board_id) VALUES(%s,%s,%s)
                        ''', (text, current_user.id, board))
            flash('Question submitted!', category="success")
    return render_template("create_post.html", board=board)


@views.route("/delete-post/<board>/<id>")
@login_required
def delete_post(board, id):
    db = get_db()
    db.execute(
        '''SELECT id, author FROM post WHERE id = %s AND board_id = %s''', (id, board))
    post = db.fetchone()
    if not post:
        flash('Sorry, that question does not exist.', category="error")
    elif current_user.id == post[1] or current_user.board_id == board:
        db.execute(
            '''DELETE FROM post WHERE id = %s AND board_id = %s''', (id, board))
        flash('Question deleted!', category="success")
    else:
        flash('You don\'t have permission to delete this question.', category="error")
    return redirect(url_for("views.show_board", board=board))


@views.route("/posts/<board>/<author>")
def posts(board, author):
    db = get_db()
    db.execute(
        '''SELECT id FROM users WHERE id = %s''', (author,))
    author_exists = db.fetchone()
    if not author_exists:
        flash('Sorry, that person does not exist.', category="error")
        return redirect(url_for("views.index"))
    db.execute(
        '''SELECT post.text, to_char(post.date_created AT TIME ZONE 'GMT', 'Month DD, YYYY HH24:MI') || ' (GMT)',
        users.name, post.id, post.author,
        users.profile_pic, users.email, users.id FROM users, post WHERE users.id=post.author AND post.author = %s
        AND post.board_id = %s''', (author, board))
    posts = db.fetchall()
    db.execute(
        '''SELECT comment.text, to_char(comment.date_created AT TIME ZONE 'GMT', 'Month DD, YYYY HH24:MI') || ' (GMT)',
        comment.author, comment.post_id, users.name, users.profile_pic
        FROM comment, users WHERE comment.author = users.id AND comment.board_id = %s''', (board,))
    comments = db.fetchall()
    db.execute(
        '''SELECT id, author, post_id FROM likes WHERE board_id = %s''', (board,))
    likes = db.fetchall()
    return render_template("posts.html", posts=posts, comments=comments, likes=likes, board=board)


@views.route("/create-comment/<board>/<post_id>", methods=['POST'])
@login_required
def create_comment(board, post_id):
    db = get_db()
    text = request.form.get('text')
    if not text:
        flash('Sorry, a comment cannot be empty.', category="error")
    else:
        db.execute(
            '''SELECT id FROM post WHERE id = %s AND board_id = %s''', (post_id, board))
        post_exists = db.fetchone()
        if post_exists:
            db.execute('''
                        INSERT INTO comment (text, author, post_id, board_id) VALUES(%s,%s,%s,%s)
                        ''', (text, current_user.id, post_exists[0], board))
        else:
            flash('Sorry, that post does not exist.', category="error")
    return redirect(url_for("views.show_board", board=board))


@views.route('/like-post/<board>', methods=['POST'])
@login_required
def like(board):
    post_id = request.form['postid']
    db = get_db()

    db.execute(
        '''SELECT id FROM post WHERE id = %s AND board_id = %s''', (post_id, board))
    post_exists = db.fetchone()

    db.execute(
        '''SELECT count(*) FROM likes WHERE author = %s AND post_id = %s AND board_id = %s
        ''', (current_user.id, post_id, board))
    like_count_user = db.fetchone()

    if not post_exists:
        flash('Sorry, that post does not exist.', category="error")
    elif like_count_user[0] > 0:
        db.execute('''
                   DELETE FROM likes WHERE author = %s AND post_id = %s AND board_id = %s
                   ''', (current_user.id, post_id, board))
        db.execute('''
                   SELECT count(*) FROM likes WHERE post_id = %s AND board_id = %s
                   ''', (post_id, board))
        like_count = db.fetchone()
        total_like_count = like_count[0]
        user_liked = "far fa-thumbs-up"
    else:
        db.execute('''
                   INSERT INTO likes (author, post_id, board_id) VALUES(%s,%s,%s)
                    ''', (current_user.id, post_id, board))
        db.execute('''
                   SELECT count(*) FROM likes WHERE post_id = %s AND board_id = %s
                   ''', (post_id, board))
        like_count = db.fetchone()
        total_like_count = like_count[0]
        user_liked = "fas fa-thumbs-up"

    return jsonify({"post_likes": total_like_count, "user_liked": user_liked})
