from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# =========================================================
# FLASK SECRET KEY
# =========================================================

app.secret_key = "ecolife-secret-key-2026"


# =========================================================
# DATABASE
# =========================================================

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# ADMIN LOGIN DETAILS
# CHANGE THESE IF YOU WANT
# =========================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ecolife123"


# =========================================================
# DATABASE TABLES
# =========================================================

def init_db():

    conn = get_db()

    # -----------------------------------------------------
    # Quiz Results
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
    # Daily Challenges
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
    # Feedback
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
    # Admin Users
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Add default admin if it does not already exist
    existing_admin = conn.execute(
        "SELECT * FROM admin_users WHERE username = ?",
        (ADMIN_USERNAME,)
    ).fetchone()

    if not existing_admin:
        conn.execute(
            """
            INSERT INTO admin_users (username, password)
            VALUES (?, ?)
            """,
            (ADMIN_USERNAME, ADMIN_PASSWORD)
        )

    conn.commit()
    conn.close()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# QUIZ PAGE
# =========================================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    score = None
    submitted = False
    participant_name = ""

    # Correct answers
    correct_answers = {
        "q1": "recycle",
        "q2": "cloth",
        "q3": "water",
        "q4": "trees",
        "q5": "led"
    }

    if request.method == "POST":

        participant_name = request.form.get(
            "name", ""
        ).strip()

        # Validate name
        if not participant_name:
            flash("🌱 Please enter your name before submitting the quiz.")
            return redirect(url_for("quiz"))

        score = 0

        # Check answers
        for question, correct_answer in correct_answers.items():

            user_answer = request.form.get(question)

            if user_answer == correct_answer:
                score += 1

        total = len(correct_answers)

        percentage = round(
            (score / total) * 100,
            2
        )

        # -------------------------------------------------
        # SAVE QUIZ RESULT
        # -------------------------------------------------

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
    return render_template("tips.html")


# =========================================================
# DAILY CHALLENGE
# =========================================================

@app.route("/challenge", methods=["GET", "POST"])
def challenge():

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        challenge_name = request.form.get(
            "challenge", ""
        ).strip()

        completed = request.form.get(
            "completed", ""
        ).strip()

        # Validate name
        if not name:
            flash("🌱 Please enter your name.")
            return redirect(url_for("challenge"))

        # Validate challenge
        if not challenge_name:
            flash("🌱 Please select today's eco challenge.")
            return redirect(url_for("challenge"))

        # Validate completion
        if completed == "":
            flash("🌱 Please tell us whether you completed it.")
            return redirect(url_for("challenge"))

        # Convert Yes/No to 1/0
        if completed.lower() in [
            "yes",
            "1",
            "true",
            "completed"
        ]:
            completed_value = 1
        else:
            completed_value = 0

        # Save challenge
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

        return redirect(url_for("challenge"))

    return render_template("challenge.html")


# =========================================================
# FEEDBACK
# =========================================================

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        rating = request.form.get(
            "rating", ""
        ).strip()

        comment = request.form.get(
            "comment", ""
        ).strip()

        # Validate rating
        if not rating:
            flash("⭐ Please select a rating.")
            return redirect(url_for("feedback"))

        try:
            rating_value = int(rating)
        except ValueError:
            flash("⭐ Invalid rating.")
            return redirect(url_for("feedback"))

        # Validate rating range
        if rating_value < 1 or rating_value > 5:
            flash("⭐ Rating must be between 1 and 5.")
            return redirect(url_for("feedback"))

        # Save feedback
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

        return redirect(url_for("feedback"))

    return render_template("feedback.html")


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        ).strip()

        conn = get_db()

        admin = conn.execute(
            """
            SELECT *
            FROM admin_users
            WHERE username = ?
            AND password = ?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if admin:

            session["admin_logged_in"] = True
            session["admin_username"] = username

            return redirect(
                url_for("admin")
            )

        flash("❌ Invalid admin username or password.")

    return render_template("admin_login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    # Check login
    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = get_db()

    # -----------------------------------------------------
    # PARTICIPANT COUNT
    # -----------------------------------------------------

    participant_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM quiz_results
        """
    ).fetchone()[0]

    # -----------------------------------------------------
    # AVERAGE QUIZ SCORE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # AVERAGE RATING
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CHALLENGE COUNT
    # -----------------------------------------------------

    challenge_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM challenges
        """
    ).fetchone()[0]

    # -----------------------------------------------------
    # QUIZ PARTICIPANTS
    # -----------------------------------------------------

    participants = conn.execute(
        """
        SELECT *
        FROM quiz_results
        ORDER BY id DESC
        """
    ).fetchall()

    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    feedback_list = conn.execute(
        """
        SELECT *
        FROM feedback
        ORDER BY id DESC
        """
    ).fetchall()

    # -----------------------------------------------------
    # CHALLENGES
    # -----------------------------------------------------

    challenges = conn.execute(
        """
        SELECT *
        FROM challenges
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

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

    return redirect(
        url_for("index")
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <div style="
        text-align:center;
        margin-top:100px;
        font-family:Arial;
    ">
        <h1>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <a href="/">Go Home</a>
    </div>
    """, 404


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )