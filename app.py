from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Secret key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "ecolife-secret-key-2026"
)

# Session security
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "database.db"
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# ADMIN LOGIN DETAILS
# =========================================================

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "ecolife123"
)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    conn = get_db()

    # -----------------------------------------------------
    # QUIZ RESULTS
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # DAILY CHALLENGES
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            challenge TEXT NOT NULL,
            completed INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # ADMIN USERS
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # CREATE DEFAULT ADMIN
    # -----------------------------------------------------

    existing_admin = conn.execute(
        """
        SELECT *
        FROM admin_users
        WHERE username = ?
        """,
        (ADMIN_USERNAME,)
    ).fetchone()

    if not existing_admin:

        conn.execute(
            """
            INSERT INTO admin_users
            (username, password)
            VALUES (?, ?)
            """,
            (
                ADMIN_USERNAME,
                ADMIN_PASSWORD
            )
        )

    conn.commit()
    conn.close()


# =========================================================
# IMPORTANT:
# INITIALIZE DATABASE WHEN FLASK/GUNICORN STARTS
# =========================================================

init_db()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# QUIZ
# =========================================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    score = None
    submitted = False
    participant_name = ""

    correct_answers = {
        "q1": "recycle",
        "q2": "cloth",
        "q3": "water",
        "q4": "trees",
        "q5": "led"
    }

    if request.method == "POST":

        participant_name = request.form.get(
            "name",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDATE NAME
        # -------------------------------------------------

        if not participant_name:

            flash(
                "🌱 Please enter your name before submitting the quiz."
            )

            return redirect(
                url_for("quiz")
            )

        # -------------------------------------------------
        # CALCULATE SCORE
        # -------------------------------------------------

        score = 0

        for question, correct_answer in correct_answers.items():

            user_answer = request.form.get(
                question
            )

            if user_answer == correct_answer:

                score += 1

        total = len(correct_answers)

        percentage = round(
            (score / total) * 100,
            2
        )

        # -------------------------------------------------
        # SAVE RESULT
        # -------------------------------------------------

        try:

            conn = get_db()

            conn.execute(
                """
                INSERT INTO quiz_results
                (
                    name,
                    score,
                    total,
                    percentage,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    participant_name,
                    score,
                    total,
                    percentage,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

            conn.commit()
            conn.close()

            submitted = True

            flash(
                "🌱 Quiz submitted successfully!"
            )

        except Exception as e:

            print(
                "QUIZ DATABASE ERROR:",
                e
            )

            flash(
                "❌ Unable to save quiz result. Please try again."
            )

    return render_template(
        "quiz.html",
        score=score,
        submitted=submitted,
        participant_name=participant_name
    )


# =========================================================
# ECO TIPS
# =========================================================

@app.route("/tips")
def tips():

    return render_template(
        "tips.html"
    )


# =========================================================
# DAILY CHALLENGE
# =========================================================

@app.route("/challenge", methods=["GET", "POST"])
def challenge():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        challenge_name = request.form.get(
            "challenge",
            ""
        ).strip()

        completed = request.form.get(
            "completed",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDATE NAME
        # -------------------------------------------------

        if not name:

            flash(
                "🌱 Please enter your name."
            )

            return redirect(
                url_for("challenge")
            )

        # -------------------------------------------------
        # VALIDATE CHALLENGE
        # -------------------------------------------------

        if not challenge_name:

            flash(
                "🌱 Please select today's eco challenge."
            )

            return redirect(
                url_for("challenge")
            )

        # -------------------------------------------------
        # VALIDATE COMPLETION
        # -------------------------------------------------

        if completed == "":

            flash(
                "🌱 Please tell us whether you completed it."
            )

            return redirect(
                url_for("challenge")
            )

        # -------------------------------------------------
        # CONVERT YES / NO TO 1 / 0
        # -------------------------------------------------

        if completed.lower() in [
            "yes",
            "1",
            "true",
            "completed"
        ]:

            completed_value = 1

        else:

            completed_value = 0

        # -------------------------------------------------
        # SAVE CHALLENGE
        # -------------------------------------------------

        try:

            conn = get_db()

            conn.execute(
                """
                INSERT INTO challenges
                (
                    name,
                    challenge,
                    completed,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    challenge_name,
                    completed_value,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

            conn.commit()
            conn.close()

            flash(
                "🌱 Your eco challenge has been saved successfully!"
            )

        except Exception as e:

            print(
                "CHALLENGE DATABASE ERROR:",
                e
            )

            flash(
                "❌ Unable to save challenge. Please try again."
            )

        return redirect(
            url_for("challenge")
        )

    return render_template(
        "challenge.html"
    )


# =========================================================
# FEEDBACK
# =========================================================

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        rating = request.form.get(
            "rating",
            ""
        ).strip()

        comment = request.form.get(
            "comment",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDATE RATING
        # -------------------------------------------------

        if not rating:

            flash(
                "⭐ Please select a rating."
            )

            return redirect(
                url_for("feedback")
            )

        try:

            rating_value = int(
                rating
            )

        except ValueError:

            flash(
                "⭐ Invalid rating."
            )

            return redirect(
                url_for("feedback")
            )

        # -------------------------------------------------
        # VALIDATE RATING RANGE
        # -------------------------------------------------

        if rating_value < 1 or rating_value > 5:

            flash(
                "⭐ Rating must be between 1 and 5."
            )

            return redirect(
                url_for("feedback")
            )

        # -------------------------------------------------
        # SAVE FEEDBACK
        # -------------------------------------------------

        try:

            conn = get_db()

            conn.execute(
                """
                INSERT INTO feedback
                (
                    name,
                    rating,
                    comment,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    rating_value,
                    comment,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

            conn.commit()
            conn.close()

            flash(
                "💚 Thank you for your feedback!"
            )

        except Exception as e:

            print(
                "FEEDBACK DATABASE ERROR:",
                e
            )

            flash(
                "❌ Unable to save feedback. Please try again."
            )

        return redirect(
            url_for("feedback")
        )

    return render_template(
        "feedback.html"
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================
#
# BOTH URLs WORK:
#
# /admin/login
# /admin_login
#
# This fixes the 404 you previously saw on Render.
# =========================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
@app.route(
    "/admin_login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        try:

            conn = get_db()

            admin = conn.execute(
                """
                SELECT *
                FROM admin_users
                WHERE username = ?
                AND password = ?
                """,
                (
                    username,
                    password
                )
            ).fetchone()

            conn.close()

        except Exception as e:

            print(
                "ADMIN LOGIN DATABASE ERROR:",
                e
            )

            flash(
                "❌ Database error. Please try again."
            )

            return render_template(
                "admin_login.html"
            )

        # -------------------------------------------------
        # LOGIN SUCCESS
        # -------------------------------------------------

        if admin:

            session["admin_logged_in"] = True

            session["admin_username"] = username

            return redirect(
                url_for("admin")
            )

        # -------------------------------------------------
        # LOGIN FAILED
        # -------------------------------------------------

        flash(
            "❌ Invalid admin username or password."
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    # -----------------------------------------------------
    # CHECK ADMIN LOGIN
    # -----------------------------------------------------

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    try:

        conn = get_db()

        # -------------------------------------------------
        # PARTICIPANT COUNT
        # -------------------------------------------------

        participant_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM quiz_results
            """
        ).fetchone()[0]

        # -------------------------------------------------
        # AVERAGE QUIZ SCORE
        # -------------------------------------------------

        average_score = conn.execute(
            """
            SELECT AVG(percentage)
            FROM quiz_results
            """
        ).fetchone()[0]

        if average_score is None:

            average_score = 0

        else:

            average_score = round(
                average_score,
                2
            )

        # -------------------------------------------------
        # AVERAGE RATING
        # -------------------------------------------------

        average_rating = conn.execute(
            """
            SELECT AVG(rating)
            FROM feedback
            """
        ).fetchone()[0]

        if average_rating is None:

            average_rating = 0

        else:

            average_rating = round(
                average_rating,
                2
            )

        # -------------------------------------------------
        # CHALLENGE COUNT
        # -------------------------------------------------

        challenge_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM challenges
            """
        ).fetchone()[0]

        # -------------------------------------------------
        # QUIZ PARTICIPANTS
        # -------------------------------------------------

        participants = conn.execute(
            """
            SELECT *
            FROM quiz_results
            ORDER BY id DESC
            """
        ).fetchall()

        # -------------------------------------------------
        # FEEDBACK
        # -------------------------------------------------

        feedback_list = conn.execute(
            """
            SELECT *
            FROM feedback
            ORDER BY id DESC
            """
        ).fetchall()

        # -------------------------------------------------
        # CHALLENGES
        # -------------------------------------------------

        challenges = conn.execute(
            """
            SELECT *
            FROM challenges
            ORDER BY id DESC
            """
        ).fetchall()

        conn.close()

    except Exception as e:

        print(
            "ADMIN DASHBOARD DATABASE ERROR:",
            e
        )

        flash(
            "❌ Unable to load admin dashboard."
        )

        return redirect(
            url_for("index")
        )

    return render_template(
        "admin.html",

        participant_count=participant_count,

        average_score=average_score,

        average_rating=average_rating,

        challenge_count=challenge_count,

        participants=participants,

        feedback_list=feedback_list,

        challenges=challenges
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    session.pop(
        "admin_username",
        None
    )

    flash(
        "You have been logged out."
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# HEALTH CHECK
# =========================================================
#
# Useful for checking whether Render is running Flask.
#
# Open:
# https://YOUR-APP.onrender.com/health
# =========================================================

@app.route("/health")
def health():

    return {
        "status": "OK",
        "application": "EcoLife"
    }, 200


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoLife - 404</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>

    <body style="
        text-align:center;
        margin-top:100px;
        font-family:Arial,sans-serif;
        padding:20px;
    ">

        <h1>404 - Page Not Found</h1>

        <p>
            The page you are looking for does not exist.
        </p>

        <p>
            <a href="/">
                🌱 Go Home
            </a>
        </p>

        <p>
            <a href="/admin/login">
                🔐 Admin Login
            </a>
        </p>

    </body>
    </html>
    """, 404


# =========================================================
# 500 ERROR
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):

    print(
        "INTERNAL SERVER ERROR:",
        error
    )

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoLife - Server Error</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>

    <body style="
        text-align:center;
        margin-top:100px;
        font-family:Arial,sans-serif;
        padding:20px;
    ">

        <h1>🌱 EcoLife</h1>

        <h2>Something went wrong</h2>

        <p>
            The server encountered an error.
        </p>

        <p>
            Please try again.
        </p>

        <p>
            <a href="/">
                🏠 Go Home
            </a>
        </p>

    </body>
    </html>
    """, 500


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=False
    )