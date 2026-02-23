"""
HS Tutor — AI-Powered High School Tutor
Streamlit Cloud compatible | Google Sheets storage | Gmail SMTP reporting
"""

import streamlit as st
from openai import OpenAI
import json
import time
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

TEACHING_CORE = """
PERSONALITY & TONE — this is how you communicate in every message:

You have the energy of a favorite teacher — warm, encouraging, occasionally playful,
and genuinely excited about your subject. You use emojis naturally and sparingly
(not in every sentence, but where they add warmth: "Nice try on the spelling — Jerusalem 😊"
or "You've got this 💪"). You celebrate effort as much as correctness. A wrong answer
is always met with "close!", "interesting thought!", or "nice try — here's a nudge:"
before redirecting — never just "that's wrong." When the student makes a small mistake
like a spelling error or near-miss, acknowledge it with light humor before moving on.
Keep your tone conversational — like texting a really smart friend who knows the subject
inside out. Never be stiff, robotic, or overly formal. Short punchy sentences beat long
paragraphs. Use phrases like "let's", "think about it this way", "you've got this",
"ooh, close!", "yes — exactly!", and "now here's the fun part:" naturally.

TEACHING PHILOSOPHY — follow this in every response:

1. SOCRATIC FIRST: Never give answers immediately. Always ask a leading question first.
   Example: Instead of solving, ask "What do you think the first step should be here?"
   Only move to explanation after the student attempts or explicitly asks for help.

2. 3-STRIKE HINT SYSTEM (moderate — use judgment on difficulty):
   - Strike 1 (wrong answer or "try again"): Give a targeted hint only. Point to the specific
     step or concept they're missing WITHOUT solving it. Ask them to try again.
   - Strike 2 (still wrong): Show ONLY the first step. Ask them to complete the rest.
   - Strike 3 (still wrong): Show the full worked solution, but note it for the session summary
     as "needed full walkthrough on [topic]." For harder concepts, you may show more
     at strike 2 — use your judgment based on difficulty level.
   - NEVER re-solve a problem just because the student says "try again" or "show me again."
     Instead say: "Let's try it together — what's the first thing you'd do?"

3. WORKED EXAMPLE → STUDENT PRACTICE: Always show one clear example first, then
   immediately give a similar problem for the student to try independently.

4. VOCABULARY & NOTATION: Gently correct informal language and reinforce proper terminology.
   Example: If student writes "the number next to x," say "that's called the coefficient — good instinct!"
   Never shame, always reframe as a learning moment.

5. SPECIFIC ENCOURAGEMENT: Praise the specific thing they did right, never generic praise.
   Good: "Nice — you remembered to do the same operation on both sides."
   Bad: "Great job!" or "Correct!"
   When wrong: "You've got the right idea, but check your arithmetic on step 2" not just "That's wrong."

6. PACING AWARENESS — AUTOMATIC PROGRESSION (non-negotiable):
   - 3 correct in a row → automatically move to the next difficulty level. Do NOT ask
     permission. Simply say "You've got that down — let's level up!" and give a harder
     problem. If the student says "no," "same," or tries to stay at the easy level, hold
     firm kindly: "I know it feels comfortable, but the best way to grow is to push a
     little further. Let's try one harder problem — you might surprise yourself!"
   - 5 correct in a row at the same level → move up two difficulty levels.
   - NEVER let the student stay at the same difficulty indefinitely by saying "same" or "no."
     Acknowledge their hesitation warmly but always progress after 3 correct answers.
   - 3 wrong in a row → slow down, try a completely different explanation approach
     (new analogy, simpler example, break into smaller steps), and note the struggle topic
     in your response so it appears in the session summary.
   - DIFFICULTY LADDER for Math: one-step equations → two-step equations → equations with
     variables on both sides → equations with fractions → word problems.
     Apply the same ladder logic to all subjects: simple recall → application → analysis.

7. SESSION WRAP-UP: When the student says "done," "bye," "end session," or similar,
   give a warm 2-sentence summary: what they worked on today and one specific thing to
   review next time. Example: "Today you tackled two-step equations and showed real
   improvement by the end. Next session, let's revisit division of negatives — that tripped
   you up a couple of times."

8. REAL-WORLD CONNECTIONS — always include after teaching any concept:
   After explaining a concept or confirming a correct answer, always add a brief
   "Real World Snap" — a 2-3 sentence real-world application of that exact concept.
   Format it naturally, not as a separate section. Examples:
   - Math (variables/equations): "By the way — this is exactly how a store calculates
     a sale price. If the original price is x and the discount is 20%, the equation
     is: sale price = x - 0.20x. Retailers use this hundreds of times a day."
   - History (Imperialism): "This is still playing out today — China's Belt and Road
     Initiative, where they build infrastructure in developing countries in exchange
     for economic influence, is a modern form of the same imperial strategy."
   - Physics (Newton's 3rd Law): "This is literally why rockets work in space — the
     engine pushes gas backward, and the equal opposite reaction pushes the rocket forward."
   - Geography (push/pull factors): "Right now, push factors like drought and gang
     violence in Central America are driving migration to the US — the same concept
     you just learned, happening live."
   - Spanish (subjunctive mood): "Spanish speakers use this every time they express
     doubt or emotion — you'll hear it constantly in telenovelas and everyday conversation."
   - English (metaphor): "Advertisers use metaphors constantly — 'Red Bull gives you
     wings' is a metaphor designed to make you feel the product transforms you."
   Keep it brief, vivid, and relevant to a 9th grader's world.

9. SUBJECT GUARDRAIL: If asked about anything outside your subject, politely decline and
   redirect. Say: "I'm your [Subject] tutor — I can only help with [subject] topics!
   Switch to the right subject in the sidebar."
"""

SUBJECTS = {
    "📐 Math": (
        "You are an experienced, warm high school Math teacher tutoring a 9th grade freshman one-on-one. "
        "You cover Algebra 1 and Geometry. You teach the way the best classroom teachers do — "
        "you ask questions before giving answers, celebrate specific successes, and never let a student "
        "passively watch you solve problems. Your goal is genuine understanding, not just correct answers.\n\n"
        + TEACHING_CORE +
        "\nSUBJECT GUARDRAIL: If the student asks about anything unrelated to Math, say: "
        "'I'm your Math tutor — I can only help with math topics! Switch to the right subject in the sidebar.'"
    ),
    "🌍 Human Geography": (
        "You are an experienced, engaging AP Human Geography teacher tutoring a 9th grade freshman one-on-one. "
        "You cover population, migration, culture, political geography, agriculture, industry, and urban geography. "
        "You connect abstract concepts to real-world examples the student can relate to, and you always ask "
        "what they already know before explaining — building on prior knowledge like a great teacher does.\n\n"
        + TEACHING_CORE +
        "\nSUBJECT GUARDRAIL: If the student asks about anything unrelated to Human Geography, say: "
        "'I'm your Human Geography tutor — please switch subjects in the sidebar for other topics!'"
    ),
    "🔭 Conceptual Physics": (
        "You are an enthusiastic Conceptual Physics teacher tutoring a 9th grade freshman one-on-one. "
        "You build intuitive understanding without heavy math — covering motion, forces, energy, waves, "
        "electricity, and magnetism. You love using everyday analogies and thought experiments, and you "
        "always ask 'what do YOU think happens?' before explaining. You make physics feel exciting, not scary.\n\n"
        + TEACHING_CORE +
        "\nSUBJECT GUARDRAIL: If the student asks about anything unrelated to Physics, say: "
        "'I'm your Physics tutor — I can only help with physics topics! Switch subjects in the sidebar.'"
    ),
    "📜 History": (
        "You are a passionate History teacher tutoring a 9th grade freshman one-on-one. "
        "You cover World History and US History, including events, causes and effects, key figures, "
        "essay writing, and DBQs. You use storytelling to make history come alive, and you always connect "
        "the past to the present. You ask the student for their interpretation before offering yours — "
        "teaching them to think historically, not just memorize facts.\n\n"
        + TEACHING_CORE +
        "\nSUBJECT GUARDRAIL: If the student asks about anything unrelated to History, say: "
        "'I'm your History tutor — I can only help with history topics! Switch subjects in the sidebar.'"
    ),
    "🇪🇸 Spanish": (
        "You are a patient, encouraging Spanish teacher tutoring a 9th grade freshman one-on-one. "
        "You cover vocabulary, grammar, verb conjugations, reading comprehension, and conversation. "
        "You gently correct mistakes by modeling the correct form, never just saying 'wrong.' "
        "You occasionally reply partly in Spanish with translations in parentheses to build immersion. "
        "You use mnemonics and patterns to make vocabulary and conjugations stick.\n\n"
        + TEACHING_CORE +
        "\nSUBJECT GUARDRAIL: If the student asks about anything unrelated to Spanish, say: "
        "'I'm your Spanish tutor — I can only help with Spanish! Switch subjects in the sidebar.'"
    ),
    "✍️ English": (
        "You are a thoughtful, encouraging English teacher tutoring a 9th grade freshman one-on-one. "
        "You cover reading comprehension, literary analysis, essay writing, grammar, and vocabulary. "
        "When reviewing writing, you give specific line-level feedback, not vague suggestions. "
        "You teach students to find meaning in texts by asking questions like 'why do you think the "
        "author chose that word?' before explaining. You guide them through the writing process step by step.\n\n"
        + TEACHING_CORE +
        "\nSUBJECT GUARDRAIL: If the student asks about anything unrelated to English/Literature, say: "
        "'I'm your English tutor — I can only help with English topics! Switch subjects in the sidebar.'"
    ),
}

SUBJECT_NAMES = {k: k.split(" ", 1)[1] for k in SUBJECTS}

QUIZ_PROMPT = (
    "Based on our conversation so far, generate exactly 3 multiple-choice quiz questions to test the student's "
    "understanding of what we discussed. The 3 questions must follow this exact structure:\n"
    "  Q1: A straightforward recall or concept question based on what was covered.\n"
    "  Q2: An application question — the student must apply the concept to a new example.\n"
    "  Q3: A real-world application question — present a realistic scenario from everyday life, "
    "current events, or something a 9th grader would relate to, and ask them to apply what they learned.\n\n"
    "Format your response as valid JSON only, like this:\n"
    '{"questions": [{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A", "explanation": "..."}]}\n'
    "Make all questions appropriate for a 9th grader. Only output the JSON, nothing else."
)

PARENT_PASSWORD = "parentview2024"  # Can be overridden via st.secrets

# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE SHEETS HELPERS
# ─────────────────────────────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_gsheet_client():
    """Create authenticated gspread client from Streamlit secrets."""
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets connection failed: {e}")
        return None


def get_or_create_worksheet(client, spreadsheet_id, title, headers):
    """Get worksheet by title, creating it with headers if it doesn't exist."""
    try:
        sh = client.open_by_key(spreadsheet_id)
        try:
            ws = sh.worksheet(title)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=title, rows=1000, cols=20)
            ws.append_row(headers)
        return ws
    except Exception as e:
        st.error(f"Worksheet error ({title}): {e}")
        return None


def save_session_to_sheets(session_data: dict):
    """Append a completed session row to the Sessions sheet."""
    client = get_gsheet_client()
    if not client:
        return False
    spreadsheet_id = st.secrets.get("spreadsheet_id", "")
    if not spreadsheet_id:
        return False

    headers = [
        "Date", "Subject", "Duration (min)", "Messages",
        "Avg Confidence", "Topics Covered", "Quiz Score",
        "Homework Items", "Off-Topic Attempts", "Session ID"
    ]
    ws = get_or_create_worksheet(client, spreadsheet_id, "Sessions", headers)
    if not ws:
        return False

    ws.append_row([
        session_data.get("date", ""),
        session_data.get("subject", ""),
        session_data.get("duration_min", 0),
        session_data.get("message_count", 0),
        session_data.get("avg_confidence", "N/A"),
        session_data.get("topics", ""),
        session_data.get("quiz_score", "N/A"),
        session_data.get("homework_done", 0),
        session_data.get("off_topic_attempts", 0),
        session_data.get("session_id", ""),
    ])
    return True


def load_all_sessions():
    """Load all session rows from Google Sheets."""
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame()
    spreadsheet_id = st.secrets.get("spreadsheet_id", "")
    if not spreadsheet_id:
        return pd.DataFrame()
    try:
        sh = client.open_by_key(spreadsheet_id)
        ws = sh.worksheet("Sessions")
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()


def load_streaks():
    """Load streak data from Sheets."""
    client = get_gsheet_client()
    if not client:
        return {}
    spreadsheet_id = st.secrets.get("spreadsheet_id", "")
    if not spreadsheet_id:
        return {}
    try:
        sh = client.open_by_key(spreadsheet_id)
        try:
            ws = sh.worksheet("Streaks")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Streaks", rows=10, cols=5)
            ws.append_row(["last_study_date", "current_streak", "longest_streak"])
            ws.append_row([str(date.today()), 1, 1])
        records = ws.get_all_records()
        return records[0] if records else {}
    except Exception:
        return {}


def save_streaks(streak_data: dict):
    """Update streak row in Sheets."""
    client = get_gsheet_client()
    if not client:
        return
    spreadsheet_id = st.secrets.get("spreadsheet_id", "")
    if not spreadsheet_id:
        return
    try:
        sh = client.open_by_key(spreadsheet_id)
        ws = sh.worksheet("Streaks")
        ws.delete_rows(2)
        ws.append_row([
            streak_data.get("last_study_date", str(date.today())),
            streak_data.get("current_streak", 1),
            streak_data.get("longest_streak", 1),
        ])
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# EMAIL HELPER
# ─────────────────────────────────────────────────────────────────────────────

def send_session_email(session_data: dict, summary_text: str):
    """Send session report email via Gmail SMTP."""
    try:
        gmail_user = st.secrets.get("gmail_user", "")
        gmail_password = st.secrets.get("gmail_app_password", "")
        parent_email = st.secrets.get("parent_email", gmail_user)

        if not gmail_user or not gmail_password:
            return False, "Gmail credentials not configured in secrets."

        subject_line = (
            f"📚 Tutor Session Report — {session_data.get('subject', '')} | "
            f"{session_data.get('date', '')}"
        )

        html_body = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
        <h2 style="color: #2C3E50;">🎓 HS Tutor — Session Report</h2>
        <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
            <tr style="background:#F2F3F4;">
                <td style="padding:8px; font-weight:bold;">Date</td>
                <td style="padding:8px;">{session_data.get('date','')}</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:bold;">Subject</td>
                <td style="padding:8px;">{session_data.get('subject','')}</td>
            </tr>
            <tr style="background:#F2F3F4;">
                <td style="padding:8px; font-weight:bold;">Duration</td>
                <td style="padding:8px;">{session_data.get('duration_min', 0)} minutes</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:bold;">Messages Exchanged</td>
                <td style="padding:8px;">{session_data.get('message_count', 0)}</td>
            </tr>
            <tr style="background:#F2F3F4;">
                <td style="padding:8px; font-weight:bold;">Avg. Confidence</td>
                <td style="padding:8px;">{session_data.get('avg_confidence', 'N/A')} / 5</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:bold;">Quiz Score</td>
                <td style="padding:8px;">{session_data.get('quiz_score', 'Not taken')}</td>
            </tr>
            <tr style="background:#F2F3F4;">
                <td style="padding:8px; font-weight:bold;">Off-Topic Attempts</td>
                <td style="padding:8px;">{session_data.get('off_topic_attempts', 0)}</td>
            </tr>
        </table>
        <h3 style="color: #2C3E50;">AI Session Summary</h3>
        <div style="background:#F9F9F9; padding:15px; border-left:4px solid #3498DB; border-radius:4px;">
            {summary_text.replace(chr(10), '<br>')}
        </div>
        <p style="color:#888; font-size:0.8rem; margin-top:30px;">
            Sent by HS Tutor App • {session_data.get('date','')}
        </p>
        </body></html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject_line
        msg["From"] = gmail_user
        msg["To"] = parent_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, parent_email, msg.as_string())

        return True, "Email sent!"
    except Exception as e:
        return False, str(e)


# ─────────────────────────────────────────────────────────────────────────────
# STREAK LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def update_streak():
    """Update daily study streak."""
    streaks = load_streaks()
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    last_date = streaks.get("last_study_date", "")
    current = int(streaks.get("current_streak", 0))
    longest = int(streaks.get("longest_streak", 0))

    if last_date == today:
        return current, longest  # Already counted today
    elif last_date == yesterday:
        current += 1
    else:
        current = 1  # Streak broken

    longest = max(longest, current)
    save_streaks({"last_study_date": today, "current_streak": current, "longest_streak": longest})
    return current, longest


# ─────────────────────────────────────────────────────────────────────────────
# SESSION SUMMARY VIA AI
# ─────────────────────────────────────────────────────────────────────────────

def generate_session_summary(messages: list, subject: str, api_key: str) -> str:
    """Ask GPT-4o to summarize the session for parents."""
    if not messages or not api_key:
        return "No session data available."
    try:
        client = OpenAI(api_key=api_key)
        convo = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages[-30:]])
        prompt = (
            f"You are reviewing a tutoring session for a 9th grade student in {subject}.\n\n"
            f"CONVERSATION:\n{convo}\n\n"
            "Write a concise parent-friendly summary (4-6 sentences) covering:\n"
            "1. What topics were studied\n"
            "2. How well the student seemed to understand the material\n"
            "3. Any areas that need more practice\n"
            "4. Whether the student stayed on topic\n"
            "5. One specific recommendation for the student to follow up on\n"
            "Write in a warm, informative tone for parents."
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Summary unavailable: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def generate_quiz(messages: list, subject: str, api_key: str):
    """Generate a 3-question quiz based on session content."""
    try:
        client = OpenAI(api_key=api_key)
        convo = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages[-20:]])
        prompt = (
            f"Subject: {subject}\n\nSession so far:\n{convo}\n\n{QUIZ_PROMPT}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: STUDENT VIEW
# ─────────────────────────────────────────────────────────────────────────────

def student_view(api_key: str):
    # ── Init session state ────────────────────────────────────────────────────
    defaults = {
        "all_messages": {s: [] for s in SUBJECTS},
        "session_start": {s: None for s in SUBJECTS},
        "confidence_scores": {s: [] for s in SUBJECTS},
        "off_topic_counts": {s: 0 for s in SUBJECTS},
        "quiz_triggered": {s: False for s in SUBJECTS},
        "quiz_data": {s: None for s in SUBJECTS},
        "quiz_answers": {s: {} for s in SUBJECTS},
        "quiz_submitted": {s: False for s in SUBJECTS},
        "homework": [],
        "session_ended": {s: False for s in SUBJECTS},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🎓 HS Tutor")
        st.caption("Your AI-powered study companion")
        st.divider()

        st.markdown("**📚 Choose Subject**")
        selected = st.radio("Subject", list(SUBJECTS.keys()), label_visibility="collapsed")
        subj_name = SUBJECT_NAMES[selected]
        st.divider()

        # Timer display
        start = st.session_state.session_start.get(selected)
        if start:
            elapsed = int((time.time() - start) / 60)
            st.metric("⏱ Session Time", f"{elapsed} min")

            # Subject balance warning
            all_times = {}
            for s in SUBJECTS:
                s_start = st.session_state.session_start.get(s)
                if s_start:
                    all_times[s] = int((time.time() - s_start) / 60)
            if all_times:
                max_subj = max(all_times, key=all_times.get)
                max_time = all_times[max_subj]
                if max_time > 40 and len(all_times) < 3:
                    st.warning(f"⚖️ You've spent {max_time} min on {SUBJECT_NAMES[max_subj]}. Consider switching subjects!")
        else:
            st.caption("⏱ Timer starts when you send your first message.")

        # Streak display
        streaks = load_streaks()
        current_streak = int(streaks.get("current_streak", 0))
        if current_streak > 0:
            st.metric("🔥 Study Streak", f"{current_streak} day{'s' if current_streak != 1 else ''}")

        st.divider()

        # Homework checklist
        st.markdown("**📋 Homework Checklist**")
        new_hw = st.text_input("Add item", placeholder="e.g. Ch.3 problems 1-10", key="hw_input")
        if st.button("➕ Add", use_container_width=True) and new_hw.strip():
            st.session_state.homework.append({"task": new_hw.strip(), "done": False})
            st.rerun()

        completed = 0
        for i, item in enumerate(st.session_state.homework):
            checked = st.checkbox(item["task"], value=item["done"], key=f"hw_{i}")
            st.session_state.homework[i]["done"] = checked
            if checked:
                completed += 1
        if st.session_state.homework:
            st.caption(f"✅ {completed}/{len(st.session_state.homework)} done")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.all_messages[selected] = []
                st.session_state.session_start[selected] = None
                st.session_state.confidence_scores[selected] = []
                st.session_state.quiz_triggered[selected] = False
                st.session_state.quiz_data[selected] = None
                st.session_state.quiz_submitted[selected] = False
                st.rerun()
        with col2:
            if st.button("📊 End Session", use_container_width=True):
                st.session_state.session_ended[selected] = True
                st.rerun()

    # ── Main chat area ────────────────────────────────────────────────────────
    messages = st.session_state.all_messages[selected]
    conf_scores = st.session_state.confidence_scores[selected]

    st.markdown(f"## {selected}")
    st.caption(f"AI-powered {subj_name} tutor • Questions must be about {subj_name} only")

    # ── Session End / Report ──────────────────────────────────────────────────
    if st.session_state.session_ended.get(selected) and messages:
        st.success("✅ Session ended! Generating your report...")

        start_time = st.session_state.session_start.get(selected, time.time())
        duration = max(1, int((time.time() - start_time) / 60))
        avg_conf = round(sum(conf_scores) / len(conf_scores), 1) if conf_scores else "N/A"
        quiz_score = "Not taken"
        if st.session_state.quiz_submitted.get(selected) and st.session_state.quiz_data.get(selected):
            qdata = st.session_state.quiz_data[selected].get("questions", [])
            answers = st.session_state.quiz_answers.get(selected, {})
            correct = sum(1 for i, q in enumerate(qdata) if answers.get(i, "").startswith(q.get("answer", "")))
            quiz_score = f"{correct}/{len(qdata)}"
        hw_done = sum(1 for h in st.session_state.homework if h["done"])

        session_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "subject": subj_name,
            "duration_min": duration,
            "message_count": len(messages),
            "avg_confidence": avg_conf,
            "topics": subj_name,
            "quiz_score": quiz_score,
            "homework_done": hw_done,
            "off_topic_attempts": st.session_state.off_topic_counts.get(selected, 0),
            "session_id": f"{selected[:3]}-{int(time.time())}",
        }

        with st.spinner("Generating AI summary..."):
            summary = generate_session_summary(messages, subj_name, api_key)

        with st.expander("📄 Session Report", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("⏱ Duration", f"{duration} min")
            col2.metric("💬 Messages", len(messages))
            col3.metric("⭐ Avg Confidence", f"{avg_conf}/5" if avg_conf != "N/A" else "N/A")
            col4.metric("🧩 Quiz Score", quiz_score)
            st.markdown("**AI Summary for Parents:**")
            st.info(summary)

        # Save to Sheets
        with st.spinner("Saving to Google Sheets..."):
            saved = save_session_to_sheets(session_data)
            if saved:
                st.success("✅ Session saved to Google Sheets!")
                update_streak()
            else:
                st.warning("⚠️ Could not save to Google Sheets. Check your secrets configuration.")

        # Send email
        with st.spinner("Sending email to parents..."):
            ok, msg = send_session_email(session_data, summary)
            if ok:
                st.success("📧 Report emailed to parents!")
            else:
                st.warning(f"⚠️ Email not sent: {msg}")

        if st.button("🔄 Start New Session"):
            st.session_state.session_ended[selected] = False
            st.session_state.all_messages[selected] = []
            st.session_state.session_start[selected] = None
            st.session_state.confidence_scores[selected] = []
            st.session_state.quiz_triggered[selected] = False
            st.session_state.quiz_data[selected] = None
            st.session_state.quiz_submitted[selected] = False
            st.rerun()
        return

    # ── Quiz Mode ─────────────────────────────────────────────────────────────
    start_time = st.session_state.session_start.get(selected)
    if (start_time and
            not st.session_state.quiz_triggered[selected] and
            len(messages) >= 4 and
            (time.time() - start_time) >= 20 * 60):
        st.session_state.quiz_triggered[selected] = True
        st.info("⏰ You've been studying for 20+ minutes! Time for a quick knowledge check.")

    if st.session_state.quiz_triggered[selected] and not st.session_state.quiz_submitted[selected]:
        with st.expander("🧩 Knowledge Check Quiz", expanded=st.session_state.quiz_data[selected] is None):
            if st.session_state.quiz_data[selected] is None:
                if st.button("📝 Generate Quiz Now", use_container_width=True):
                    with st.spinner("Generating quiz based on your session..."):
                        qdata = generate_quiz(messages, subj_name, api_key)
                        st.session_state.quiz_data[selected] = qdata
                    st.rerun()
            else:
                qdata = st.session_state.quiz_data[selected]
                if qdata and "questions" in qdata:
                    st.markdown("**Answer all questions then submit:**")
                    for i, q in enumerate(qdata["questions"]):
                        st.markdown(f"**Q{i+1}: {q['question']}**")
                        choice = st.radio(
                            f"q{i}",
                            q["options"],
                            key=f"quiz_{selected}_{i}",
                            label_visibility="collapsed"
                        )
                        st.session_state.quiz_answers[selected][i] = choice

                    if st.button("✅ Submit Quiz", use_container_width=True):
                        st.session_state.quiz_submitted[selected] = True
                        st.rerun()

    if st.session_state.quiz_submitted.get(selected) and st.session_state.quiz_data.get(selected):
        with st.expander("🎯 Quiz Results", expanded=True):
            qdata = st.session_state.quiz_data[selected].get("questions", [])
            answers = st.session_state.quiz_answers.get(selected, {})
            correct = 0
            for i, q in enumerate(qdata):
                user_ans = answers.get(i, "")
                is_correct = user_ans.startswith(q.get("answer", ""))
                if is_correct:
                    correct += 1
                    st.success(f"Q{i+1}: ✅ Correct! — {q.get('explanation','')}")
                else:
                    st.error(f"Q{i+1}: ❌ Answer was **{q.get('answer','')}** — {q.get('explanation','')}")
            st.metric("Your Score", f"{correct}/{len(qdata)}")

    # ── Welcome message ───────────────────────────────────────────────────────
    if not messages:
        with st.chat_message("assistant"):
            st.markdown(
                f"Hi! 👋 I'm your **{subj_name} tutor**. "
                f"I can only help with {subj_name} topics — so let's keep our focus there!\n\n"
                "What would you like to work on today?"
            )

    # ── Chat history ──────────────────────────────────────────────────────────
    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Show confidence rating widget after each assistant message
            if msg["role"] == "assistant":
                conf_key = f"conf_{selected}_{i}"
                if conf_key not in st.session_state:
                    st.session_state[conf_key] = None
                rating = st.session_state[conf_key]
                if rating is None:
                    cols = st.columns([1, 1, 1, 1, 1, 4])
                    labels = ["😕 1", "🙁 2", "😐 3", "🙂 4", "😄 5"]
                    for j, (col, label) in enumerate(zip(cols[:5], labels)):
                        if col.button(label, key=f"btn_{conf_key}_{j}"):
                            st.session_state[conf_key] = j + 1
                            st.session_state.confidence_scores[selected].append(j + 1)
                            st.rerun()
                    cols[5].caption("How well did you understand this?")
                else:
                    st.caption(f"You rated this: {'⭐' * rating}")

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input(f"Ask a {subj_name} question...")

    if user_input:
        if not api_key:
            st.error("⚠️ Enter your OpenAI API key in the sidebar.")
            st.stop()

        # Start timer on first message
        if st.session_state.session_start[selected] is None:
            st.session_state.session_start[selected] = time.time()

        messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client = OpenAI(api_key=api_key)
        api_messages = [{"role": "system", "content": SUBJECTS[selected]}] + \
                       [{"role": m["role"], "content": m["content"]} for m in messages]

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1024,
                    messages=api_messages,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                messages.append({"role": "assistant", "content": full_response})

                # Detect off-topic deflection in response
                if "switch" in full_response.lower() and "subject" in full_response.lower():
                    st.session_state.off_topic_counts[selected] = (
                        st.session_state.off_topic_counts.get(selected, 0) + 1
                    )

                st.rerun()
            except Exception as e:
                err = str(e)
                if "auth" in err.lower() or "api key" in err.lower():
                    placeholder.error("❌ Invalid API key.")
                elif "rate" in err.lower():
                    placeholder.error("⏳ Rate limit hit. Try again in a moment.")
                else:
                    placeholder.error(f"Error: {err}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PARENT DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def parent_dashboard():
    st.markdown("## 👨‍👩‍👦 Parent Dashboard")

    if "parent_authenticated" not in st.session_state:
        st.session_state.parent_authenticated = False

    if not st.session_state.parent_authenticated:
        st.markdown("Enter the parent password to view session reports and progress.")
        pwd = st.text_input("Password", type="password")
        parent_pwd = st.secrets.get("parent_password", PARENT_PASSWORD)
        if st.button("🔓 Unlock Dashboard"):
            if pwd == parent_pwd:
                st.session_state.parent_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        return

    st.success("✅ Welcome, Parent!")
    if st.button("🔒 Lock Dashboard"):
        st.session_state.parent_authenticated = False
        st.rerun()

    st.divider()

    df = load_all_sessions()
    if df.empty:
        st.info("No session data yet. Sessions will appear here after your son completes a study session.")
        return

    # Clean numeric columns
    for col in ["Duration (min)", "Messages", "Avg Confidence"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Summary metrics ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📅 Total Sessions", len(df))
    total_min = int(df["Duration (min)"].sum()) if "Duration (min)" in df.columns else 0
    col2.metric("⏱ Total Study Time", f"{total_min} min")
    avg_conf = round(df["Avg Confidence"].mean(), 1) if "Avg Confidence" in df.columns else "N/A"
    col3.metric("⭐ Avg Confidence", f"{avg_conf}/5")
    streaks = load_streaks()
    col4.metric("🔥 Current Streak", f"{streaks.get('current_streak', 0)} days")

    st.divider()

    # ── Subject breakdown ─────────────────────────────────────────────────────
    st.markdown("### 📚 Time Per Subject")
    if "Subject" in df.columns and "Duration (min)" in df.columns:
        subj_time = df.groupby("Subject")["Duration (min)"].sum().reset_index()
        subj_time.columns = ["Subject", "Total Minutes"]
        st.bar_chart(subj_time.set_index("Subject"))

        # Balance warning
        if len(subj_time) > 1:
            max_time = subj_time["Total Minutes"].max()
            min_time = subj_time["Total Minutes"].min()
            if max_time > min_time * 3:
                top = subj_time.loc[subj_time["Total Minutes"].idxmax(), "Subject"]
                bottom = subj_time.loc[subj_time["Total Minutes"].idxmin(), "Subject"]
                st.warning(f"⚖️ Subject imbalance detected: much more time on {top} than {bottom}.")

    # ── Weekly study trend ────────────────────────────────────────────────────
    st.markdown("### 📈 Weekly Study Trend")
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Week"] = df["Date_parsed"].dt.to_period("W").astype(str)
        weekly = df.groupby("Week")["Duration (min)"].sum().reset_index()
        weekly.columns = ["Week", "Minutes"]
        st.line_chart(weekly.set_index("Week"))

    st.divider()

    # ── Session log ───────────────────────────────────────────────────────────
    st.markdown("### 📋 Session Log")
    display_cols = [c for c in ["Date", "Subject", "Duration (min)", "Messages",
                                 "Avg Confidence", "Quiz Score", "Off-Topic Attempts"] if c in df.columns]
    st.dataframe(df[display_cols].sort_values("Date", ascending=False), use_container_width=True)

    # ── Off-topic attempts ────────────────────────────────────────────────────
    if "Off-Topic Attempts" in df.columns:
        total_offtopic = int(pd.to_numeric(df["Off-Topic Attempts"], errors="coerce").sum())
        if total_offtopic > 5:
            st.warning(
                f"⚠️ {total_offtopic} total off-topic attempts detected across all sessions. "
                "The guardrails are working, but you may want to have a conversation about focus."
            )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="HS Tutor 🎓", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebarContent"] { padding-top: 1.5rem; }
    .stMetric { background: #F8F9FA; border-radius: 8px; padding: 8px; }
</style>
""", unsafe_allow_html=True)

# ── API Key (from secrets or manual entry) ────────────────────────────────────
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    with st.sidebar:
        api_key = st.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")

# ── Top-level navigation ──────────────────────────────────────────────────────
tab_student, tab_parent = st.tabs(["📚 Student Tutor", "👨‍👩‍👦 Parent Dashboard"])

with tab_student:
    student_view(api_key)

with tab_parent:
    parent_dashboard()
