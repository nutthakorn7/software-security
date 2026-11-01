"""The start page, the deferred clock, and resuming a quiz.

Measured on the live DB before this existed (MFU software-security, assessments
2–4): 17 of 92 submitted attempts were incomplete, and every one was submitted
615–9,733 s after started_at — all time-ups, none an instant failure. The clock
started at code redemption and nothing said so. Students read a question, left
or pressed Back, typed the code again later, and were told their quiz was over;
they reported it as "the quiz errors as soon as I open it".

So: redeeming a code shows a start page and the clock starts on Start; the
question page says you can't go back and how to get back in; and running out of
time is explained instead of announced. None of it loosens an anti-copy
invariant — the cursor is still advance-only, `correct` still never reaches the
page, and there is still one attempt per student.
"""

import os
import random
import re
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import assessment as A  # noqa: E402
import db as D  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = "2026-08-15T08:00:00"
INVITE = "LETMEIN"
STEMS = ["STEM-ALPHA", "STEM-BRAVO", "STEM-CHARLIE", "STEM-DELTA"]


def _csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, "no CSRF token in the rendered form"
    return m.group(1)


# ── model ──────────────────────────────────────────────────────────────────

@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:", check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    for f in ("schema.sql", "schema_assess.sql", "schema_submit.sql"):
        with open(os.path.join(HERE, f), encoding="utf-8") as fh:
            c.executescript(fh.read())
    c.execute("INSERT INTO teachers (id, username, password_hash, created_at)"
              " VALUES (1,'t','x',?)", (T0,))
    c.commit()
    yield c
    c.close()


def _publish(conn, **kw):
    qs = [{"stem": s, "options": ["a", "b", "c", "d"], "correct": 1} for s in STEMS]
    return A.publish(conn, teacher_id=1, title="W1 quiz", now=T0, questions=qs, **kw)


def _redeem(conn, aid, now, sid="65310001"):
    code = A.issue_codes(conn, aid, [sid], T0)[sid]
    return A.redeem(conn, code, now, rng=random.Random(1)), code


def test_redeeming_a_code_does_not_start_the_clock(conn):
    aid = _publish(conn, time_limit_sec=600)
    att, _ = _redeem(conn, aid, "2026-08-15T08:00:00")
    assert A.awaiting_start(att)
    # An hour on the start page costs nothing: the old clock would be 50
    # minutes past the limit here.
    assert A.time_left(conn, att, "2026-08-15T09:00:00") == 600
    assert not A.expired(conn, att, "2026-08-15T09:00:00")


def test_the_clock_runs_from_start(conn):
    aid = _publish(conn, time_limit_sec=600)
    att, _ = _redeem(conn, aid, "2026-08-15T08:00:00")
    att = A.start(conn, att, "2026-08-15T09:00:00")
    assert not A.awaiting_start(att)
    assert A.time_left(conn, att, "2026-08-15T09:05:00") == pytest.approx(300)
    assert not A.expired(conn, att, "2026-08-15T09:09:59")
    assert A.expired(conn, att, "2026-08-15T09:10:01")


def test_pressing_start_twice_never_resets_the_clock(conn):
    aid = _publish(conn, time_limit_sec=600)
    att, _ = _redeem(conn, aid, "2026-08-15T08:00:00")
    first = A.start(conn, att, "2026-08-15T09:00:00")
    # Back to the start page and Start again, from a stale row and a fresh one.
    A.start(conn, att, "2026-08-15T09:08:00")
    again = A.start(conn, A.get_attempt(conn, att["id"]), "2026-08-15T09:08:00")
    assert again["started_at"] == first["started_at"] == "2026-08-15T09:00:00"
    assert A.time_left(conn, again, "2026-08-15T09:08:00") == pytest.approx(120)


def test_no_question_is_shown_or_recorded_before_start(conn):
    aid = _publish(conn, time_limit_sec=600)
    att, _ = _redeem(conn, aid, "2026-08-15T08:00:00")
    # NotStarted, not None: None means "finished", and callers submit those.
    with pytest.raises(A.NotStarted):
        A.question_for_student(conn, att, now="2026-08-15T08:00:00")
    qid = conn.execute("SELECT id FROM assessment_questions WHERE assessment_id = ?"
                       " ORDER BY position", (aid,)).fetchone()["id"]
    with pytest.raises(A.StaleAnswer):      # recoverable — the route must not submit
        A.answer(conn, att, qid, choice=1, now="2026-08-15T08:00:00")
    att = A.get_attempt(conn, att["id"])
    assert att["cursor"] == 0 and att["submitted_at"] is None
    assert conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 0


def test_start_rechecks_the_window(conn):
    """Without this, a code redeemed before closes_at could be started the next
    day, after everyone else had compared answers."""
    aid = _publish(conn, time_limit_sec=600, closes_at="2026-08-15T09:10:00")
    att, _ = _redeem(conn, aid, "2026-08-15T09:05:00")
    with pytest.raises(A.AttemptError, match="has closed"):
        A.start(conn, att, "2026-08-15T09:11:00")
    assert A.awaiting_start(A.get_attempt(conn, att["id"]))


def test_start_refuses_a_submitted_attempt(conn):
    aid = _publish(conn)
    att, _ = _redeem(conn, aid, T0)
    att = A.submit(conn, A.start(conn, att, T0), T0)
    with pytest.raises(A.AttemptError, match="already submitted"):
        A.start(conn, att, T0)


def test_re_entering_the_code_before_start_returns_the_same_unstarted_attempt(conn):
    aid = _publish(conn, time_limit_sec=600)
    att, code = _redeem(conn, aid, "2026-08-15T08:00:00")
    again = A.redeem(conn, code, "2026-08-15T08:30:00")
    assert again["id"] == att["id"] and A.awaiting_start(again)


def test_re_entering_the_code_mid_quiz_keeps_the_cursor_and_the_clock(conn):
    aid = _publish(conn, time_limit_sec=600)
    att, code = _redeem(conn, aid, "2026-08-15T08:00:00")
    att = A.start(conn, att, "2026-08-15T08:01:00")
    q = A.question_for_student(conn, att, now="2026-08-15T08:02:00")
    A.answer(conn, att, q["question_id"], choice=1, now="2026-08-15T08:02:00")

    again = A.redeem(conn, code, "2026-08-15T08:04:00")
    assert again["id"] == att["id"]
    assert again["cursor"] == 1
    assert again["started_at"] == "2026-08-15T08:01:00", "re-entry must not restart the clock"
    assert not A.awaiting_start(again)
    assert A.question_for_student(conn, again, now="2026-08-15T08:04:00")["index"] == 2


def test_migration_leaves_existing_attempts_running_and_survives_a_restart(tmp_path):
    """Rows written before the column existed get NULL — the clock runs from
    started_at, exactly as before. And migrate() runs on every boot, so a second
    boot must not start the clock of a student sitting on the start page."""
    d = D.connect(str(tmp_path / "old.db"))
    D.init_db(d)
    d.execute("ALTER TABLE attempts DROP COLUMN awaiting_start")
    d.execute("INSERT INTO teachers (id, username, password_hash, created_at)"
              " VALUES (1,'t','x',?)", (T0,))
    d.commit()
    aid = _publish(d, time_limit_sec=600)
    code = A.issue_codes(d, aid, ["old"], T0)["old"]
    # The old redeem(): no awaiting_start column, clock running from started_at.
    d.execute("INSERT INTO attempts (assessment_id, student_id, code, order_json,"
              " options_json, cursor, started_at) VALUES (?,?,?,?,?,0,?)",
              (aid, "old", code, "[0, 1, 2, 3]", "{}", "2026-08-15T08:00:00"))
    d.commit()

    D.migrate(d)                                   # the new image's first boot
    old = d.execute("SELECT * FROM attempts WHERE student_id = 'old'").fetchone()
    assert old["awaiting_start"] is None
    assert not A.awaiting_start(old)
    assert A.time_left(d, old, "2026-08-15T08:05:00") == pytest.approx(300)
    assert A.question_for_student(d, old, now="2026-08-15T08:05:00")["index"] == 1

    new, _ = _redeem(d, aid, "2026-08-15T08:06:00", sid="new")
    D.migrate(d)                                   # a restart
    assert A.awaiting_start(A.get_attempt(d, new["id"]))


# ── routes ─────────────────────────────────────────────────────────────────

@pytest.fixture
def appmod(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setenv("INVITE_CODE", INVITE)
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    import importlib
    import app as _a
    importlib.reload(_a)
    _a.app.config["TESTING"] = True
    return _a


@pytest.fixture
def clock(appmod):
    """The routes read the time through config["NOW"]; a dict lets a test move it."""
    t = {"now": "2026-08-15T09:00:00"}
    appmod.app.config["NOW"] = lambda: t["now"]
    return t


@pytest.fixture
def quiz(appmod, clock):
    conn = appmod.get_db()
    conn.execute("INSERT INTO teachers (id, username, password_hash, created_at)"
                 " VALUES (1,'t','x',?)", (T0,))
    conn.commit()
    aid = _publish(conn, time_limit_sec=600)
    codes = A.issue_codes(conn, aid, ["65310001"], T0)
    return aid, codes["65310001"]


@pytest.fixture
def client(appmod):
    return appmod.app.test_client()


def _enter(client, code):
    html = client.get("/quiz").get_data(as_text=True)
    return client.post("/quiz", data={"csrf_token": _csrf(html), "code": code})


def _press_start(client):
    page = client.get("/quiz/start").get_data(as_text=True)
    return client.post("/quiz/start", data={"csrf_token": _csrf(page)})


def _answer_open_question(client):
    page = client.get("/quiz/take").get_data(as_text=True)
    qid = re.search(r'name="question_id" value="(\d+)"', page).group(1)
    return client.post("/quiz/take", data={"csrf_token": _csrf(page),
                                           "question_id": qid, "choice": "1"})


def test_a_redeemed_code_lands_on_the_start_page_not_a_question(client, quiz):
    _, code = quiz
    r = _enter(client, code)
    assert r.status_code == 302
    r = client.get("/quiz/take")
    assert r.status_code == 302 and "/quiz/start" in r.headers["Location"]

    r = client.get("/quiz/start")
    page = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "4 questions" in page and "one at a time" in page
    assert "10 minutes" in page
    assert "cannot go back" in page
    assert "Back button" in page
    assert "same code" in page
    assert "keeps running" in page
    assert "Start the quiz" in page
    # The rules, and nothing else: a question on this page could be read while
    # the clock is stopped.
    assert 'name="question_id"' not in page and 'name="choice"' not in page
    assert not any(s in page for s in STEMS)
    assert r.headers["Cache-Control"] == "no-store"


def test_the_clock_starts_when_start_is_pressed(client, clock, quiz):
    _, code = quiz
    clock["now"] = "2026-08-15T08:00:00"
    _enter(client, code)
    clock["now"] = "2026-08-15T09:00:00"       # an hour later: the old clock was long gone
    assert "/quiz/start" in client.get("/quiz/take").headers["Location"]
    assert "Start the quiz" in client.get("/quiz/start").get_data(as_text=True)

    r = _press_start(client)
    assert r.status_code == 302 and "/quiz/take" in r.headers["Location"]
    clock["now"] = "2026-08-15T09:05:00"
    page = client.get("/quiz/take").get_data(as_text=True)
    assert "Question 1 of 4" in page and "5m 0s left" in page


def test_start_is_a_post_with_csrf(client, quiz, appmod):
    aid, code = quiz
    _enter(client, code)
    assert client.post("/quiz/start", data={"csrf_token": "wrong"}).status_code == 400
    att = appmod.get_db().execute("SELECT * FROM attempts WHERE assessment_id = ?",
                                  (aid,)).fetchone()
    assert A.awaiting_start(att)


def test_an_answer_posted_before_start_is_dropped_not_submitted(client, quiz, appmod):
    aid, code = quiz
    _enter(client, code)
    page = client.get("/quiz/start").get_data(as_text=True)
    conn = appmod.get_db()
    qid = conn.execute("SELECT id FROM assessment_questions WHERE assessment_id = ?"
                       " ORDER BY position", (aid,)).fetchone()["id"]
    r = client.post("/quiz/take", data={"csrf_token": _csrf(page),
                                        "question_id": qid, "choice": "1"})
    assert r.status_code == 302
    att = conn.execute("SELECT * FROM attempts WHERE assessment_id = ?", (aid,)).fetchone()
    assert att["submitted_at"] is None and A.awaiting_start(att)
    assert conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 0


def test_back_to_the_start_page_after_starting_goes_to_the_open_question(client, clock, quiz):
    _, code = quiz
    _enter(client, code)
    _press_start(client)
    _answer_open_question(client)
    r = client.get("/quiz/start")
    assert r.status_code == 302 and "/quiz/take" in r.headers["Location"]
    assert "Question 2 of 4" in client.get("/quiz/take").get_data(as_text=True)


def test_re_entering_the_code_before_start_shows_the_start_page_again(client, quiz):
    _, code = quiz
    _enter(client, code)
    with client.session_transaction() as s:
        s.clear()                                # closed the browser
    _enter(client, code)
    assert "/quiz/start" in client.get("/quiz/take").headers["Location"]


def test_re_entering_the_code_mid_quiz_resumes_on_the_open_question(client, clock, quiz):
    _, code = quiz
    _enter(client, code)
    _press_start(client)
    _answer_open_question(client)
    with client.session_transaction() as s:
        s.clear()                                # phone died, new browser
    clock["now"] = "2026-08-15T09:04:00"
    _enter(client, code)
    r = client.get("/quiz/take")
    page = r.get_data(as_text=True)
    assert r.status_code == 200, "a started quiz resumes straight onto its question"
    assert "Question 2 of 4" in page
    assert "6m 0s left" in page, "the clock kept running from Start, it did not restart"


def test_the_question_page_says_you_cant_go_back_and_guards_the_back_button(client, quiz):
    _, code = quiz
    _enter(client, code)
    _press_start(client)
    r = client.get("/quiz/take")
    page = r.get_data(as_text=True)
    assert "You can't go back" in page and "re-enter" in page
    assert re.search(r'<script src="/static/quiz_take\.js\?v=', page)
    assert re.search(r'<p[^>]*id="quiz-back-warning"[^>]*\bhidden\b', page)
    assert r.headers["Cache-Control"] == "no-store"
    # Without it, Chrome restores the last page's ticked radio into the newly
    # fetched open question after Back — a pre-filled answer to a question the
    # student never read, one click from being recorded.
    assert re.search(r'<form[^>]*action="/quiz/take"[^>]*autocomplete="off"', page)
    js = client.get("/static/quiz_take.js").get_data(as_text=True)
    assert "pushState" in js and "popstate" in js and "persisted" in js
    assert "quiz-back-warning" in js


def test_running_out_of_time_is_explained_on_re_entry(client, clock, quiz):
    """The reported case: answer one, leave, come back long after, type the
    code again. This path used to say "Submitted. Thank you." and nothing else."""
    _, code = quiz
    _enter(client, code)
    _press_start(client)                         # 09:00 UTC = 16:00 in Thailand
    _answer_open_question(client)
    with client.session_transaction() as s:
        s.clear()
    clock["now"] = "2026-08-15T09:40:00"
    _enter(client, code)
    page = client.get("/quiz/take").get_data(as_text=True)
    assert "Your time ran out" in page
    assert "10 minutes" in page
    assert "16:00" in page and "16:10" in page and "Thailand time" in page
    assert "kept running" in page
    assert "1 of 4" in page
    assert "cannot take this quiz again" in page
    assert "Thank you" not in page

    # and the code is spent after that, with the existing plain message
    with client.session_transaction() as s:
        s.clear()
    page = _enter(client, code).get_data(as_text=True)
    assert "already submitted" in page


def test_running_out_of_time_is_explained_on_a_page_left_open(client, clock, quiz):
    """The other path: the question page stayed open, the student came back and
    pressed Next. It used to show only "Time is up — your quiz was submitted."""
    _, code = quiz
    _enter(client, code)
    _press_start(client)
    page = client.get("/quiz/take").get_data(as_text=True)
    qid = re.search(r'name="question_id" value="(\d+)"', page).group(1)
    clock["now"] = "2026-08-15T09:30:00"
    done = client.post("/quiz/take", data={"csrf_token": _csrf(page),
                                           "question_id": qid, "choice": "1"})
    body = done.get_data(as_text=True)
    assert "Your time ran out" in body and "0 of 4" in body
    assert "cannot take this quiz again" in body


def test_finishing_in_time_still_just_says_thank_you(client, quiz):
    _, code = quiz
    _enter(client, code)
    _press_start(client)
    for _ in range(4):
        _answer_open_question(client)
    page = client.get("/quiz/take").get_data(as_text=True)
    assert "Thank you" in page and "time ran out" not in page.lower()


def test_a_stale_post_after_finishing_does_not_claim_time_ran_out(client, clock, quiz):
    """A second tab, or Back-and-resend, after the last answer. The attempt is
    already submitted, so answer() refuses it as terminal — and that branch
    used to say "Time is up" to a student who had finished everything in time."""
    _, code = quiz
    _enter(client, code)
    _press_start(client)
    page = client.get("/quiz/take").get_data(as_text=True)
    stale = {"csrf_token": _csrf(page),
             "question_id": re.search(r'name="question_id" value="(\d+)"', page).group(1),
             "choice": "1"}
    for _ in range(4):
        _answer_open_question(client)
    assert "Thank you" in client.get("/quiz/take").get_data(as_text=True)  # submitted
    body = client.post("/quiz/take", data=stale).get_data(as_text=True)
    assert "Thank you" in body
    assert "time ran out" not in body.lower() and "time is up" not in body.lower()


def test_start_after_the_window_closed_is_refused_on_the_start_page(client, clock, appmod):
    conn = appmod.get_db()
    conn.execute("INSERT INTO teachers (id, username, password_hash, created_at)"
                 " VALUES (1,'t','x',?)", (T0,))
    conn.commit()
    aid = _publish(conn, time_limit_sec=600, closes_at="2026-08-15T09:10:00")
    code = A.issue_codes(conn, aid, ["65310001"], T0)["65310001"]
    clock["now"] = "2026-08-15T09:05:00"
    _enter(client, code)
    page = client.get("/quiz/start").get_data(as_text=True)
    clock["now"] = "2026-08-15T09:11:00"
    r = client.post("/quiz/start", data={"csrf_token": _csrf(page)})
    body = r.get_data(as_text=True)
    assert r.status_code == 200 and "has closed" in body
    assert "Start the quiz" not in body
    assert "/quiz/start" in client.get("/quiz/take").headers["Location"], (
        "an unstarted attempt is never submitted or shown a question")
