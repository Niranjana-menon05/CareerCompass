import os
import uuid
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify
)
from auth import init_db, login_user, register_user, save_profile, load_profile
from profile_builder import build_profile
from career_matcher import recommend_careers
from career_recovery import analyze_career_gap
from chatbot import get_response

app = Flask(__name__)
app.secret_key = "career-compass-secret-2025"   # change this to anything random

# initialise the SQLite database on startup
init_db()

# ── Helpers ─────────────────────────────────────────────

def logged_in():
    return "username" in session

def get_session_profile():
    """Return profile from session cache, or load from DB."""
    if "profile" in session:
        return session["profile"]
    if logged_in():
        profile = load_profile(session["username"])
        if profile:
            session["profile"] = profile
        return profile
    return None

def get_session_recommendations():
    if "recommendations" in session:
        return session["recommendations"]
    profile = get_session_profile()
    if profile:
        recs = recommend_careers(profile)
        session["recommendations"] = recs
        return recs
    return []


# ── Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if logged_in():
        return redirect(url_for("dashboard"))

    login_error = None
    reg_error = None
    reg_success = None
    active_tab = "login"

    if request.method == "POST":
        form_type = request.form.get("form_type")
        username  = request.form.get("username", "").strip()
        password  = request.form.get("password", "")

        if form_type == "login":
            if login_user(username, password):
                session["username"] = username
                return redirect(url_for("dashboard"))
            else:
                login_error = "Incorrect username or password."

        elif form_type == "register":
            active_tab = "register"
            email = request.form.get("email", "")
            ok, msg = register_user(username, password, email)
            if ok:
                reg_success = msg + " You can now log in."
                active_tab = "login"
            else:
                reg_error = msg

    return render_template(
        "login.html",
        login_error=login_error,
        reg_error=reg_error,
        reg_success=reg_success,
        active_tab=active_tab
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))

    profile         = get_session_profile()
    recommendations = get_session_recommendations()

    return render_template(
        "dashboard.html",
        username=session["username"],
        profile=profile,
        recommendations=recommendations,
        upload_error=session.pop("upload_error", None),
        upload_success=session.pop("upload_success", None),
        gap_result=session.pop("gap_result", None),
    )


@app.route("/upload", methods=["POST"])
def upload():
    if not logged_in():
        return redirect(url_for("login"))

    file = request.files.get("resume")
    if not file or file.filename == "":
        session["upload_error"] = "No file selected. Please choose a PDF."
        return redirect(url_for("dashboard"))

    if not file.filename.lower().endswith(".pdf"):
        session["upload_error"] = "Only PDF files are accepted."
        return redirect(url_for("dashboard"))

    # save with unique filename to avoid collisions between users
    temp_path = f"temp_{uuid.uuid4().hex}.pdf"
    try:
        file.save(temp_path)
        profile = build_profile(temp_path)
    except Exception as e:
        session["upload_error"] = f"Failed to parse resume: {str(e)}"
        return redirect(url_for("dashboard"))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # save to DB and session
    save_profile(session["username"], profile)
    session["profile"] = profile
    session.pop("recommendations", None)   # clear cached recs so they're recomputed
    session["upload_success"] = "Resume analysed successfully!"

    return redirect(url_for("dashboard"))


@app.route("/gap", methods=["POST"])
def gap_analysis():
    if not logged_in():
        return redirect(url_for("login"))

    profile = get_session_profile()
    if not profile:
        session["gap_result"] = {"error": "Please upload your resume first."}
        return redirect(url_for("dashboard") + "#gap")

    target = request.form.get("target_career", "").strip()
    if target == "__custom__":
        target = request.form.get("custom_career", "").strip()

    if not target:
        session["gap_result"] = {"error": "Please select or enter a career."}
        return redirect(url_for("dashboard") + "#gap")

    result = analyze_career_gap(profile, target)
    session["gap_result"] = result
    return redirect(url_for("dashboard") + "#gap")


@app.route("/chat", methods=["POST"])
def chat():
    if not logged_in():
        return jsonify({"reply": "Please log in to use the chatbot."})

    data    = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"reply": "I didn't catch that — could you rephrase?"})

    # pull chat history from session (keep last 20 turns)
    history = session.get("chat_history", [])

    profile         = get_session_profile()
    recommendations = get_session_recommendations()

    reply = get_response(message, history, profile, recommendations)

    # update history
    history.append({"role": "user",      "content": message})
    history.append({"role": "assistant", "content": reply})
    session["chat_history"] = history[-20:]

    return jsonify({"reply": reply})


# ── Run ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🧭  Career Compass is running!")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
