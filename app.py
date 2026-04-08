import os, random
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import pytz
from leetcode_api import pick_daily_questions, PROBLEMS, check_leetcode_solved
import pytz
IST = pytz.timezone("Asia/Kolkata")

def get_ist_now():
    return datetime.now(IST)

def get_ist_date():
    return datetime.now(IST).date()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "codedaily-dev-secret")
db_url = os.environ.get("DATABASE_URL", "sqlite:///codedaily.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config.update(
    SQLALCHEMY_DATABASE_URI=db_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.environ.get("GMAIL_USER"),
    MAIL_PASSWORD=os.environ.get("GMAIL_APP_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.environ.get("GMAIL_USER"),
    # SERVER_NAME removed — it breaks Flask routing and email url_for on Render
)

# Used for building absolute URLs in emails (no url_for needed)
APP_URL = os.environ.get("APP_URL", "https://codedaily-tiw0.onrender.com").rstrip("/")

db = SQLAlchemy(app)
mail = Mail(app)

AWARDS = {
    "first_solve":  {"icon": "🎯", "name": "First Blood",    "desc": "Solved your first problem"},
    "streak_3":     {"icon": "🔥", "name": "On Fire",         "desc": "3-day streak"},
    "streak_7":     {"icon": "⚡", "name": "Week Warrior",     "desc": "7-day streak"},
    "streak_30":    {"icon": "🏆", "name": "Month Master",     "desc": "30-day streak"},
    "all_three":    {"icon": "✅", "name": "Triple Threat",    "desc": "All 3 done in one day"},
    "hard_solver":  {"icon": "💀", "name": "Hard Mode",        "desc": "Solved a Hard problem"},
    "total_10":     {"icon": "🌱", "name": "Warming Up",       "desc": "10 problems solved"},
    "total_50":     {"icon": "🚀", "name": "On a Roll",        "desc": "50 problems solved"},
    "total_100":    {"icon": "💯", "name": "Centurion",        "desc": "100 problems solved"},
    "sql_master":   {"icon": "🗄", "name": "SQL Master",        "desc": "10 SQL problems solved"},
    "js_ninja":     {"icon": "🥷", "name": "JS Ninja",          "desc": "10 JS problems solved"},
    "algo_wizard":  {"icon": "🧙", "name": "Algo Wizard",       "desc": "10 DSA problems solved"},
    "speed_solver": {"icon": "⏱", "name": "Speed Solver",      "desc": "Solved within 5 min of opening"},
    "lc_linked":    {"icon": "🔗", "name": "LeetCoder",         "desc": "Linked your LeetCode account"},
}

class Subscriber(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    difficulty    = db.Column(db.String(10), default="Easy")
    streak        = db.Column(db.Integer, default=0)
    total_done    = db.Column(db.Integer, default=0)
    dsa_total     = db.Column(db.Integer, default=0)
    js_total      = db.Column(db.Integer, default=0)
    sql_total     = db.Column(db.Integer, default=0)
    hard_total    = db.Column(db.Integer, default=0)
    earned_awards = db.Column(db.Text, default="")
    joined_at     = db.Column(db.DateTime, default=get_ist_now) # <-- BELONGS HERE
    active        = db.Column(db.Boolean, default=True)
    lc_username   = db.Column(db.String(100), nullable=True)
    lc_session    = db.Column(db.Text, nullable=True)
    progresses    = db.relationship("DailyProgress", backref="subscriber", lazy=True)

    def awards_list(self):
        return [k for k in (self.earned_awards or "").split(",") if k]
    def has_award(self, k):
        return k in self.awards_list()
    def grant_award(self, k):
        if not self.has_award(k):
            lst = self.awards_list(); lst.append(k); self.earned_awards = ",".join(lst); return True
        return False


class DailyProgress(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey("subscriber.id"), nullable=False)
    date          = db.Column(db.Date, default=get_ist_date) # <-- BELONGS HERE (Ensure joined_at is deleted from this class!)
    difficulty    = db.Column(db.String(10), default="Easy")
    dsa_slug      = db.Column(db.String(200))
    dsa_done      = db.Column(db.Boolean, default=False)
    dsa_done_at   = db.Column(db.DateTime, nullable=True)
    dsa_opened_at = db.Column(db.DateTime, nullable=True)
    dsa_code      = db.Column(db.Text, nullable=True)
    dsa_lang      = db.Column(db.String(20), nullable=True)
    js_slug       = db.Column(db.String(200))
    js_done       = db.Column(db.Boolean, default=False)
    js_done_at    = db.Column(db.DateTime, nullable=True)
    js_opened_at  = db.Column(db.DateTime, nullable=True)
    js_code       = db.Column(db.Text, nullable=True)
    js_lang       = db.Column(db.String(20), nullable=True)
    sql_slug      = db.Column(db.String(200))
    sql_done      = db.Column(db.Boolean, default=False)
    sql_done_at   = db.Column(db.DateTime, nullable=True)
    sql_opened_at = db.Column(db.DateTime, nullable=True)
    sql_code      = db.Column(db.Text, nullable=True)
    sql_lang      = db.Column(db.String(20), nullable=True)
    

    @property
    def all_done(self): return self.dsa_done and self.js_done and self.sql_done
    @property
    def count_done(self): return sum([self.dsa_done, self.js_done, self.sql_done])


def run_migrations():
    """Safely add new columns to existing DB without dropping data."""
    with db.engine.connect() as conn:
        dialect = db.engine.dialect.name

        def column_exists(table, column):
            if dialect == "sqlite":
                result = conn.execute(db.text(f"PRAGMA table_info({table})"))
                return any(row[1] == column for row in result)
            else:
                result = conn.execute(db.text(
                    f"SELECT column_name FROM information_schema.columns "
                    f"WHERE table_name='{table}' AND column_name='{column}'"
                ))
                return result.fetchone() is not None

        ts_type = "DATETIME" if dialect == "sqlite" else "TIMESTAMP"
        migrations = [
            ("subscriber",     "lc_username",   "VARCHAR(100)"),
            ("subscriber",     "lc_session",    "TEXT"),
            ("daily_progress", "dsa_opened_at", ts_type),
            ("daily_progress", "js_opened_at",  ts_type),
            ("daily_progress", "sql_opened_at", ts_type),
        ]
        for table, column, col_type in migrations:
            if not column_exists(table, column):
                try:
                    conn.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()
                    app.logger.info(f"Migration: added {table}.{column}")
                except Exception as e:
                    app.logger.warning(f"Migration skip {table}.{column}: {e}")


def evaluate_awards(sub, q_type=None, prog=None):
    granted = []
    def chk(k, c):
        if c and sub.grant_award(k): granted.append(k)
    chk("first_solve", sub.total_done >= 1)
    chk("streak_3",    sub.streak >= 3)
    chk("streak_7",    sub.streak >= 7)
    chk("streak_30",   sub.streak >= 30)
    chk("all_three",   any(p.all_done for p in sub.progresses))
    chk("hard_solver", sub.hard_total >= 1)
    chk("total_10",    sub.total_done >= 10)
    chk("total_50",    sub.total_done >= 50)
    chk("total_100",   sub.total_done >= 100)
    chk("sql_master",  sub.sql_total >= 10)
    chk("js_ninja",    sub.js_total >= 10)
    chk("algo_wizard", sub.dsa_total >= 10)
    chk("lc_linked",   bool(sub.lc_username))
    if q_type and prog:
        opened_at = getattr(prog, f"{q_type}_opened_at", None)
        if opened_at and (datetime.utcnow() - opened_at).total_seconds() <= 300:
            chk("speed_solver", True)
    return granted


def _update_streak(sub):
    yesterday = date.today() - timedelta(days=1)
    yp = DailyProgress.query.filter_by(subscriber_id=sub.id, date=yesterday).first()
    sub.streak = (sub.streak + 1) if (yp and yp.all_done) else 1


@app.route("/")
def index(): return render_template("index.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    name  = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    diff  = request.form.get("difficulty", "Easy")
    if not name or not email: return jsonify({"error": "Name and email required"}), 400
    if diff not in ("Easy", "Medium", "Hard"): diff = "Easy"
    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        existing.active = True; existing.name = name; existing.difficulty = diff
        db.session.commit(); session["subscriber_id"] = existing.id
        return jsonify({"ok": True})
    sub = Subscriber(name=name, email=email, difficulty=diff)
    db.session.add(sub); db.session.commit()
    session["subscriber_id"] = sub.id
    
    try: 
        _send_welcome_email(sub)
        print(f"✅ SUCCESS: Welcome email sent to {email}", flush=True)
    except Exception as e: 
        print(f"❌ CRITICAL EMAIL ERROR: {str(e)}", flush=True)
        app.logger.warning(f"Welcome email: {e}")


@app.route("/dashboard")
def dashboard():
    sub_id = session.get("subscriber_id")
    if not sub_id: return redirect(url_for("index"))
    sub = Subscriber.query.get_or_404(sub_id)
    seed = int(date.today().strftime("%Y%m%d"))
    questions = pick_daily_questions(sub.difficulty, seed)
    prog = DailyProgress.query.filter_by(subscriber_id=sub_id, date=date.today()).first()
    if not prog:
        prog = DailyProgress(subscriber_id=sub_id, difficulty=sub.difficulty,
            dsa_slug=questions["dsa"]["slug"], js_slug=questions["js"]["slug"], sql_slug=questions["sql"]["slug"])
        db.session.add(prog); db.session.commit()
    history = []
    for i in range(13, -1, -1):
        d = date.today() - timedelta(days=i)
        p = DailyProgress.query.filter_by(subscriber_id=sub_id, date=d).first()
        history.append({"date": d.strftime("%d %b"), "day": d.strftime("%a"),
            "solved": p.count_done if p else 0, "all": p.all_done if p else False})
    earned = [{"key": k, **AWARDS[k]} for k in sub.awards_list() if k in AWARDS]
    return render_template("dashboard.html", sub=sub, questions=questions, progress=prog,
        history=history, awards=earned, all_awards=AWARDS, today=date.today().strftime("%A, %d %B %Y"))


@app.route("/open-problem", methods=["POST"])
def open_problem():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    data = request.get_json(); q_type = data.get("type")
    if q_type not in ("dsa", "js", "sql"): return jsonify({"error": "Invalid"}), 400
    prog = DailyProgress.query.filter_by(subscriber_id=sub_id, date=date.today()).first()
    if prog and not getattr(prog, f"{q_type}_opened_at", None):
        setattr(prog, f"{q_type}_opened_at", datetime.utcnow()); db.session.commit()
    return jsonify({"ok": True})


@app.route("/solve", methods=["POST"])
def solve():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    q_type = data.get("type"); code = data.get("code", "").strip(); lang = data.get("lang", "python")
    if q_type not in ("dsa", "js", "sql"): return jsonify({"error": "Invalid type"}), 400
    if not code: return jsonify({"error": "No code submitted"}), 400
    if len(code) > 50000: return jsonify({"error": "Code is too long"}), 400
    sub = Subscriber.query.get(sub_id)
    prog = DailyProgress.query.filter_by(subscriber_id=sub_id, date=date.today()).first()
    if not prog: return jsonify({"error": "No progress record"}), 400
    setattr(prog, f"{q_type}_code", code); setattr(prog, f"{q_type}_lang", lang)
    new_awards = []
    if not getattr(prog, f"{q_type}_done"):
        setattr(prog, f"{q_type}_done", True); setattr(prog, f"{q_type}_done_at", datetime.utcnow())
        sub.total_done += 1
        if q_type == "dsa": sub.dsa_total += 1
        if q_type == "js":  sub.js_total  += 1
        if q_type == "sql": sub.sql_total  += 1
        if sub.difficulty == "Hard": sub.hard_total += 1
        new_awards = evaluate_awards(sub, q_type=q_type, prog=prog)
        if prog.all_done:
            _update_streak(sub)
            try: _send_completion_email(sub)
            except Exception as e: app.logger.warning(f"Completion email: {e}")
    db.session.commit()
    return jsonify({"ok": True, "count": prog.count_done, "all_done": prog.all_done,
        "streak": sub.streak, "new_awards": [{"key": k, **AWARDS[k]} for k in new_awards if k in AWARDS]})


@app.route("/hint", methods=["POST"])
def get_hint():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = Subscriber.query.get(sub_id) if sub_id else None
    diff = sub.difficulty if sub else "Easy"
    data = request.get_json(); q_type = data.get("type"); hint_idx = int(data.get("hint_idx", 0))
    seed = int(date.today().strftime("%Y%m%d"))
    questions = pick_daily_questions(diff, seed)
    q = questions.get(q_type, {}); hints = q.get("hints", [])
    if hint_idx >= len(hints): return jsonify({"hint": None, "has_more": False})
    return jsonify({"hint": hints[hint_idx], "has_more": hint_idx + 1 < len(hints), "next_idx": hint_idx + 1})


@app.route("/solution", methods=["POST"])
def get_solution():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = Subscriber.query.get(sub_id) if sub_id else None
    diff = sub.difficulty if sub else "Easy"
    data = request.get_json(); q_type = data.get("type"); lang = data.get("lang", "python")
    seed = int(date.today().strftime("%Y%m%d"))
    questions = pick_daily_questions(diff, seed)
    q = questions.get(q_type, {}); solutions = q.get("solutions", {})
    sol = solutions.get(lang, solutions.get("python", "No solution available."))
    return jsonify({"solution": sol, "title": q.get("title", ""), "lang": lang})


@app.route("/update-profile", methods=["POST"])
def update_profile():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = Subscriber.query.get(sub_id); data = request.get_json()
    diff = data.get("difficulty", sub.difficulty)
    if diff in ("Easy", "Medium", "Hard"): sub.difficulty = diff
    db.session.commit()
    return jsonify({"ok": True, "difficulty": sub.difficulty})


@app.route("/link-leetcode", methods=["POST"])
def link_leetcode():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = Subscriber.query.get(sub_id); data = request.get_json()
    username   = (data.get("username") or "").strip()
    lc_session = (data.get("lc_session") or "").strip()
    if not username: return jsonify({"error": "Username required"}), 400
    if not _verify_lc_user(username):
        return jsonify({"error": "Username not found or profile is private. Go to leetcode.com → Profile → make it public."}), 400
    sub.lc_username = username
    if lc_session: sub.lc_session = lc_session
    new_awards = [{"key": "lc_linked", **AWARDS["lc_linked"]}] if sub.grant_award("lc_linked") else []
    db.session.commit()
    return jsonify({"ok": True, "username": username, "new_awards": new_awards,
        "has_session": bool(lc_session)})


@app.route("/unlink-leetcode", methods=["POST"])
def unlink_leetcode():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = Subscriber.query.get(sub_id)
    sub.lc_username = None; sub.lc_session = None
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/sync-leetcode", methods=["POST"])
def sync_leetcode():
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = Subscriber.query.get(sub_id)
    if not sub.lc_username: return jsonify({"error": "No LeetCode account linked"}), 400
    seed = int(date.today().strftime("%Y%m%d"))
    questions = pick_daily_questions(sub.difficulty, seed)
    prog = DailyProgress.query.filter_by(subscriber_id=sub_id, date=date.today()).first()
    if not prog: return jsonify({"error": "No progress record"}), 400
    synced = []; new_awards = []
    for q_type in ("dsa", "js", "sql"):
        if getattr(prog, f"{q_type}_done"): continue
        slug = getattr(prog, f"{q_type}_slug")
        try: solved = check_leetcode_solved(sub.lc_username, slug)
        except Exception as e: app.logger.warning(f"LC sync {slug}: {e}"); solved = False
        if solved:
            setattr(prog, f"{q_type}_done", True); setattr(prog, f"{q_type}_done_at", datetime.utcnow())
            setattr(prog, f"{q_type}_lang", "leetcode")
            sub.total_done += 1
            if q_type == "dsa": sub.dsa_total += 1
            if q_type == "js":  sub.js_total  += 1
            if q_type == "sql": sub.sql_total  += 1
            if sub.difficulty == "Hard": sub.hard_total += 1
            synced.append(q_type); new_awards.extend(evaluate_awards(sub))
    if prog.all_done and synced:
        _update_streak(sub)
        try: _send_completion_email(sub)
        except Exception as e: app.logger.warning(f"Completion email: {e}")
    db.session.commit()
    msg = f"✅ Synced {len(synced)} problem(s) from LeetCode!" if synced else "No new problems found. Solve on LC first, then sync."
    return jsonify({"ok": True, "synced": synced, "count": prog.count_done, "all_done": prog.all_done,
        "streak": sub.streak, "new_awards": [{"key": k, **AWARDS[k]} for k in new_awards if k in AWARDS], "message": msg})


# @app.route("/submit-to-leetcode", methods=["POST"])
# def submit_to_leetcode():
#     """Submit code directly to LeetCode using the user's session cookie."""
#     import requests as req_lib
#     sub_id = session.get("subscriber_id")
#     if not sub_id: return jsonify({"error": "Not logged in"}), 401
#     sub = db.session.get(Subscriber, sub_id)
#     if not sub.lc_username:
#         return jsonify({"error": "Link your LeetCode account first.", "need_link": True}), 400
#     if not sub.lc_session:
#         return jsonify({"error": "Session cookie required to submit to LeetCode. Re-link and paste your LEETCODE_SESSION cookie.", "need_session": True}), 400

#     data = request.get_json()
#     slug        = data.get("slug", "")
#     code        = data.get("code", "").strip()
#     lang        = data.get("lang", "python")
#     question_id = data.get("question_id", "")
#     if not code or not slug: return jsonify({"error": "Missing code or slug"}), 400

#     lang_map = {"python": "python3", "javascript": "javascript", "java": "java", "sql": "mysql", "python3": "python3"}
#     lc_lang = lang_map.get(lang, "python3")

#     # Get CSRF token first
#     try:
#         sess = req_lib.Session()
#         sess.cookies.set("LEETCODE_SESSION", sub.lc_session, domain="leetcode.com")
#         csrf_resp = sess.get("https://leetcode.com/", headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
#         csrf_token = sess.cookies.get("csrftoken", "")

#         resp = sess.post(
#             f"https://leetcode.com/problems/{slug}/submit/",
#             json={"lang": lc_lang, "question_id": str(question_id), "typed_code": code},
#             headers={
#                 "Content-Type": "application/json",
#                 "Referer":      f"https://leetcode.com/problems/{slug}/",
#                 "X-CSRFToken":  csrf_token,
#                 "User-Agent":   "Mozilla/5.0",
#             },
#             timeout=12,
#         )
#         if resp.status_code == 200:
#             result = resp.json()
#             sid = result.get("submission_id")
#             if sid:
#                 return jsonify({"ok": True, "submission_id": sid,
#                     "lc_url": f"https://leetcode.com/submissions/detail/{sid}/"})
#             return jsonify({"error": "Submitted but no ID returned.", "raw": result}), 400
#         elif resp.status_code == 403:
#             return jsonify({"error": "Session expired. Re-link your LeetCode account with a fresh cookie.", "need_session": True}), 403
#         else:
#             return jsonify({"error": f"LeetCode error {resp.status_code}. Session may be expired."}), 400
#     except Exception as e:
#         return jsonify({"error": f"Could not reach LeetCode: {str(e)}"}), 500
@app.route("/submit-to-leetcode", methods=["POST"])
def submit_to_leetcode():
    """Submit code directly to LeetCode using the user's session cookie."""
    import cloudscraper # <-- Changed from requests
    
    sub_id = session.get("subscriber_id")
    if not sub_id: return jsonify({"error": "Not logged in"}), 401
    sub = db.session.get(Subscriber, sub_id)
    
    if not sub.lc_username:
        return jsonify({"error": "Link your LeetCode account first.", "need_link": True}), 400
    if not sub.lc_session:
        return jsonify({"error": "Session cookie required to submit to LeetCode. Re-link and paste your LEETCODE_SESSION cookie.", "need_session": True}), 400

    data = request.get_json()
    slug        = data.get("slug", "")
    code        = data.get("code", "").strip()
    lang        = data.get("lang", "python")
    question_id = data.get("question_id", "")
    if not code or not slug: return jsonify({"error": "Missing code or slug"}), 400

    lang_map = {"python": "python3", "javascript": "javascript", "java": "java", "sql": "mysql", "python3": "python3"}
    lc_lang = lang_map.get(lang, "python3")

    try:
        scraper = cloudscraper.create_scraper()
        scraper.cookies.set("LEETCODE_SESSION", sub.lc_session, domain="leetcode.com")
        
        # Get CSRF token first
        csrf_resp = scraper.get("https://leetcode.com/", timeout=10)
        csrf_token = scraper.cookies.get("csrftoken", "")

        resp = scraper.post(
            f"https://leetcode.com/problems/{slug}/submit/",
            json={"lang": lc_lang, "question_id": str(question_id), "typed_code": code},
            headers={
                "Content-Type": "application/json",
                "Referer":      f"https://leetcode.com/problems/{slug}/",
                "X-CSRFToken":  csrf_token,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            result = resp.json()
            sid = result.get("submission_id")
            if sid:
                return jsonify({"ok": True, "submission_id": sid,
                    "lc_url": f"https://leetcode.com/submissions/detail/{sid}/"})
            return jsonify({"error": "Submitted but no ID returned.", "raw": result}), 400
        elif resp.status_code == 403:
            return jsonify({"error": "Session expired or blocked. Re-link your LeetCode account with a fresh cookie.", "need_session": True}), 403
        else:
            return jsonify({"error": f"LeetCode error {resp.status_code}. Session may be expired."}), 400
    except Exception as e:
        return jsonify({"error": f"Could not reach LeetCode: {str(e)}"}), 500


# @app.route("/unsubscribe/<int:sub_id>")
# def unsubscribe(sub_id):
#     sub = Subscriber.query.get_or_404(sub_id)
#     sub.active = False; db.session.commit()
#     return render_template("unsubscribed.html", name=sub.name)
@app.route("/unsubscribe/<int:sub_id>", methods=["GET", "POST"])
def unsubscribe(sub_id):
    sub = Subscriber.query.get_or_404(sub_id)
    
    if request.method == "POST":
        sub.active = False
        db.session.commit()
        return render_template("unsubscribed.html", name=sub.name, success=True)
        
    return render_template("unsubscribed.html", name=sub.name, success=False)


@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("index"))


@app.route("/admin/send-daily")
def admin_send_daily():
    if request.args.get("token") != os.environ.get("ADMIN_TOKEN", "changeme"):
        return "Unauthorized", 403
    try:
        _send_daily_emails()
        return "✅ Done! Emails sent. Check Render logs for details."
    except Exception as e:
        return f"❌ Error: {e}", 500

@app.route("/admin/test-email")
def admin_test_email():
    """Send a single test email to verify SMTP is working on Render."""
    if request.args.get("token") != os.environ.get("ADMIN_TOKEN", "changeme"):
        return "Unauthorized", 403
    test_to = request.args.get("to", os.environ.get("GMAIL_USER", ""))
    if not test_to:
        return "Pass ?to=youremail@gmail.com", 400
    try:
        mail.send(Message(
            subject="CodeDaily — SMTP Test ✅",
            recipients=[test_to],
            html=f"<h2>SMTP is working!</h2><p>Sent from Render at {datetime.utcnow()} UTC</p>"
                 f"<p>GMAIL_USER = {os.environ.get('GMAIL_USER','NOT SET')}</p>"
                 f"<p>APP_URL = {APP_URL}</p>"
        ))
        return f"✅ Test email sent to {test_to}! Check your inbox."
    except Exception as e:
        return f"❌ SMTP Error: {e}", 500


def _verify_lc_user(username):
    import requests as req_lib
    try:
        resp = req_lib.post("https://leetcode.com/graphql",
            json={"query": "query($u:String!){matchedUser(username:$u){username}}", "variables": {"u": username}},
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"}, timeout=8)
        return resp.json().get("data", {}).get("matchedUser") is not None
    except Exception: return False


def _send_welcome_email(sub):
    seed = int(date.today().strftime("%Y%m%d"))
    questions = pick_daily_questions(sub.difficulty, seed)
    html = render_template("emails/welcome.html", sub=sub, questions=questions,
        dashboard_url=f"{APP_URL}/dashboard",
        unsubscribe_url=f"{APP_URL}/unsubscribe/{sub.id}")
    mail.send(Message("Welcome to CodeDaily!", recipients=[sub.email], html=html))


def _send_daily_emails():
    """APScheduler runs this in a thread — must push its own app context."""
    with app.app_context():
        seed = int(date.today().strftime("%Y%m%d"))
        today_str = date.today().strftime("%A, %d %B %Y")
        subs = Subscriber.query.filter_by(active=True).all()
        app.logger.info(f"[EMAIL] Starting daily send to {len(subs)} subscribers")
        for sub in subs:
            try:
                q = pick_daily_questions(sub.difficulty, seed)
                html = render_template("emails/daily.html", sub=sub, questions=q, today=today_str,
                    dashboard_url=f"{APP_URL}/dashboard",
                    unsubscribe_url=f"{APP_URL}/unsubscribe/{sub.id}")
                mail.send(Message(f"CodeDaily — 3 problems for {date.today().strftime('%d %b')}",
                    recipients=[sub.email], html=html))
                app.logger.info(f"[EMAIL] ✅ Sent to {sub.email}")
            except Exception as e:
                app.logger.error(f"[EMAIL] ❌ Failed {sub.email}: {e}")


def _send_completion_email(sub):
    html = render_template("emails/completed.html", sub=sub, today=date.today().strftime("%A, %d %B"),
        dashboard_url=f"{APP_URL}/dashboard")
    mail.send(Message("All 3 done today! 🎉", recipients=[sub.email], html=html))


def start_scheduler():
    ist = pytz.timezone("Asia/Kolkata")
    s = BackgroundScheduler(timezone=ist)
    s.add_job(func=_send_daily_emails, trigger="cron", hour=8, minute=0)
    s.start()


with app.app_context():
    db.create_all()
    run_migrations()

if __name__ == "__main__":
    start_scheduler()
    app.run(debug=True, use_reloader=False)