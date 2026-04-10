import random
import streamlit as st
from questions import QUESTIONS
from db import (
    init_db,
    save_attempt,
    get_all_attempts,
    get_topic_summary,
    get_total_attempts,
    get_average_score,
    get_weakest_topic,
    get_best_topic
)
from evaluator import evaluate_sql_answer

st.set_page_config(page_title="AI SQL Interview Coach", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 16px;
    border-radius: 16px;
}

.stButton > button {
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.12);
}

.stTextArea textarea {
    border-radius: 14px;
}

.stSelectbox > div > div {
    border-radius: 12px;
}

.hero-box {
    padding: 24px 28px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(37,99,235,0.16), rgba(15,23,42,0.4));
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 24px;
}

.section-card {
    padding: 22px;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 18px;
}

.question-card {
    padding: 24px;
    border-radius: 18px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.08);
    margin-top: 8px;
    margin-bottom: 18px;
}

.feedback-card {
    padding: 22px;
    border-radius: 18px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 18px;
}

.small-label {
    font-size: 0.92rem;
    opacity: 0.8;
    margin-bottom: 4px;
}

.big-number {
    font-size: 1.05rem;
    font-weight: 700;
}

.badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 14px 0 8px 0;
}

.badge {
    display: inline-block;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(59,130,246,0.16);
    border: 1px solid rgba(96,165,250,0.18);
    font-size: 0.92rem;
}

.verdict-banner {
    padding: 16px 18px;
    border-radius: 16px;
    color: white;
    font-weight: 700;
    margin-bottom: 18px;
}

hr.soft {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 18px 0;
}
</style>
""", unsafe_allow_html=True)

init_db()

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "latest_feedback" not in st.session_state:
    st.session_state.latest_feedback = None

if "last_submitted_sql" not in st.session_state:
    st.session_state.last_submitted_sql = ""

if "recommended_question" not in st.session_state:
    st.session_state.recommended_question = None

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Practice"

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "Easy"

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "Filtering"

if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = "Easy"

if "mock_mode" not in st.session_state:
    st.session_state.mock_mode = False

if "mock_questions" not in st.session_state:
    st.session_state.mock_questions = []

if "mock_index" not in st.session_state:
    st.session_state.mock_index = 0

if "mock_score" not in st.session_state:
    st.session_state.mock_score = []

if "mock_results" not in st.session_state:
    st.session_state.mock_results = []

if "mock_completed" not in st.session_state:
    st.session_state.mock_completed = False


def get_verdict_color(verdict):
    if verdict == "Correct":
        return "#16a34a"
    if verdict == "Partially Correct":
        return "#ca8a04"
    return "#dc2626"


def get_level(avg_score):
    if avg_score >= 8:
        return "Advanced"
    if avg_score >= 5:
        return "Intermediate"
    return "Beginner"


def get_next_adaptive_difficulty(score, current_difficulty):
    if current_difficulty == "Easy" and score >= 8:
        return "Medium"
    if current_difficulty == "Medium" and score <= 4:
        return "Easy"
    return current_difficulty


def recommend_next_question():
    weakest_topic = get_weakest_topic()
    difficulty_to_use = st.session_state.current_difficulty

    if weakest_topic:
        candidates = [
            q for q in QUESTIONS
            if q["topic"] == weakest_topic and q["difficulty"] == difficulty_to_use
        ]
        if candidates:
            return random.choice(candidates)

    topic_candidates = [
        q for q in QUESTIONS
        if q["topic"] == st.session_state.selected_topic and q["difficulty"] == difficulty_to_use
    ]
    if topic_candidates:
        return random.choice(topic_candidates)

    fallback_candidates = [
        q for q in QUESTIONS
        if q["difficulty"] == difficulty_to_use
    ]
    if fallback_candidates:
        return random.choice(fallback_candidates)

    return random.choice(QUESTIONS)


def start_mock_interview():
    sample_size = min(5, len(QUESTIONS))
    st.session_state.mock_mode = True
    st.session_state.mock_questions = random.sample(QUESTIONS, sample_size)
    st.session_state.mock_index = 0
    st.session_state.mock_score = []
    st.session_state.mock_results = []
    st.session_state.mock_completed = False
    st.session_state.current_question = None
    st.session_state.latest_feedback = None
    st.session_state.last_submitted_sql = ""


def exit_mock_interview():
    st.session_state.mock_mode = False
    st.session_state.mock_questions = []
    st.session_state.mock_index = 0
    st.session_state.mock_score = []
    st.session_state.mock_results = []
    st.session_state.mock_completed = False


st.markdown("""
<div class="hero-box">
    <h1 style="margin-bottom: 8px;">AI SQL Interview Coach</h1>
    <div style="font-size: 1.05rem; opacity: 0.9;">
        Practice SQL interview questions, get structured feedback, improve weak areas,
        adapt difficulty dynamically, and simulate mock interviews.
    </div>
</div>
""", unsafe_allow_html=True)

tabs = ["Practice", "Feedback", "Progress"]

active_tab = st.radio(
    "",
    tabs,
    index=tabs.index(st.session_state.active_tab),
    horizontal=True
)

tab1 = active_tab == "Practice"
tab2 = active_tab == "Feedback"
tab3 = active_tab == "Progress"

if tab1:
    st.session_state.active_tab = "Practice"
    st.subheader("Practice SQL")

    if not st.session_state.mock_mode:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)

        top_col1, top_col2 = st.columns([3, 1])

        with top_col1:
            st.write("Choose a topic and difficulty, or start a mock interview.")

        with top_col2:
            if st.button("Start Mock Interview"):
                start_mock_interview()
                st.rerun()

        col1, col2 = st.columns(2)

        with col1:
            topic_options = [
                "Filtering",
                "Ordering",
                "Joins",
                "Group By",
                "Subqueries",
                "Case Based",
                "Window Functions",
                "Business SQL"
            ]
            default_topic_index = topic_options.index(st.session_state.selected_topic) if st.session_state.selected_topic in topic_options else 0
            selected_topic = st.selectbox("Select topic", topic_options, index=default_topic_index)
            st.session_state.selected_topic = selected_topic

        with col2:
            difficulty_options = ["Easy", "Medium"]
            default_difficulty_index = difficulty_options.index(st.session_state.selected_difficulty) if st.session_state.selected_difficulty in difficulty_options else 0
            selected_difficulty = st.selectbox("Select difficulty", difficulty_options, index=default_difficulty_index)
            st.session_state.selected_difficulty = selected_difficulty

        st.info(f"Adaptive Engine Suggestion: {st.session_state.current_difficulty}")

        if st.button("Generate Question"):
            filtered_questions = [
                q for q in QUESTIONS
                if q["topic"] == st.session_state.selected_topic
                and q["difficulty"] == st.session_state.selected_difficulty
            ]

            if filtered_questions:
                st.session_state.current_question = random.choice(filtered_questions)
                st.session_state.latest_feedback = None
                st.session_state.last_submitted_sql = ""
                st.session_state.recommended_question = None
            else:
                st.warning(
                    f"No {st.session_state.selected_difficulty} questions available for {st.session_state.selected_topic}."
                )

        st.markdown('</div>', unsafe_allow_html=True)

        if not st.session_state.current_question:
            st.info("Click 'Generate Question' to start practicing.")

        if st.session_state.current_question:
            q = st.session_state.current_question

            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            st.markdown(f"## {q['title']}")
            st.write(q["prompt"])

            st.markdown(
                f"""
                <div class="badge-row">
                    <span class="badge">Topic: {q['topic']}</span>
                    <span class="badge">Difficulty: {q['difficulty']}</span>
                    <span class="badge">Expected: {", ".join(q["expected_concepts"])}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            user_sql = st.text_area(
                "Write your SQL answer below:",
                value=st.session_state.last_submitted_sql,
                height=220,
                placeholder="SELECT ... FROM ... WHERE ..."
            )

            if st.button("Submit Answer"):
                if user_sql.strip():
                    st.session_state.last_submitted_sql = user_sql

                    with st.spinner("Evaluating your SQL answer..."):
                        feedback = evaluate_sql_answer(
                            question_prompt=q["prompt"],
                            expected_concepts=q["expected_concepts"],
                            user_sql=user_sql,
                            topic=q["topic"],
                            difficulty=q["difficulty"]
                        )

                    score = feedback["score"]

                    st.session_state.current_difficulty = get_next_adaptive_difficulty(
                        score=score,
                        current_difficulty=q["difficulty"]
                    )

                    if score >= 6:
                        st.session_state.streak += 1
                    else:
                        st.session_state.streak = 0

                    st.session_state.latest_feedback = feedback
                    st.session_state.recommended_question = recommend_next_question()
                    st.session_state.active_tab = "Feedback"

                    save_attempt(
                        question_id=q["id"],
                        topic=q["topic"],
                        difficulty=q["difficulty"],
                        user_sql=user_sql,
                        verdict=feedback["verdict"],
                        score=int(feedback["score"]),
                        weaknesses=", ".join(feedback["mistakes"])
                    )

                    st.rerun()
                else:
                    st.warning("Please enter your SQL answer before submitting.")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Mock Interview Mode")
        st.warning("You are in mock interview mode. Feedback is hidden until the end.")

        if not st.session_state.mock_completed and st.session_state.mock_questions:
            q = st.session_state.mock_questions[st.session_state.mock_index]

            total_questions = len(st.session_state.mock_questions)
            st.progress((st.session_state.mock_index + 1) / total_questions)
            st.caption(f"Question {st.session_state.mock_index + 1} of {total_questions}")

            st.markdown(f"### {q['title']}")
            st.write(q["prompt"])
            st.markdown(
                f"""
                <div class="badge-row">
                    <span class="badge">Topic: {q['topic']}</span>
                    <span class="badge">Difficulty: {q['difficulty']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            mock_key = f"mock_answer_{st.session_state.mock_index}"
            user_sql = st.text_area(
                "Your Answer",
                key=mock_key,
                height=220,
                placeholder="Write your SQL query here..."
            )

            col_a, col_b = st.columns([1, 1])

            with col_a:
                if st.button("Submit and Continue"):
                    if user_sql.strip():
                        feedback = evaluate_sql_answer(
                            question_prompt=q["prompt"],
                            expected_concepts=q["expected_concepts"],
                            user_sql=user_sql,
                            topic=q["topic"],
                            difficulty=q["difficulty"]
                        )

                        st.session_state.mock_score.append(feedback["score"])
                        st.session_state.mock_results.append(
                            {
                                "title": q["title"],
                                "topic": q["topic"],
                                "difficulty": q["difficulty"],
                                "score": feedback["score"],
                                "verdict": feedback["verdict"],
                                "improved_query": feedback["improved_query"],
                                "explanation": feedback["explanation"]
                            }
                        )

                        save_attempt(
                            question_id=q["id"],
                            topic=q["topic"],
                            difficulty=q["difficulty"],
                            user_sql=user_sql,
                            verdict=feedback["verdict"],
                            score=int(feedback["score"]),
                            weaknesses=", ".join(feedback["mistakes"])
                        )

                        if feedback["score"] >= 6:
                            st.session_state.streak += 1
                        else:
                            st.session_state.streak = 0

                        if st.session_state.mock_index < len(st.session_state.mock_questions) - 1:
                            st.session_state.mock_index += 1
                        else:
                            st.session_state.mock_completed = True

                        st.rerun()
                    else:
                        st.warning("Please enter your SQL answer before continuing.")

            with col_b:
                if st.button("Exit Mock Interview"):
                    exit_mock_interview()
                    st.rerun()

        elif st.session_state.mock_completed:
            st.subheader("Mock Interview Result")

            avg_mock_score = round(sum(st.session_state.mock_score) / len(st.session_state.mock_score), 2) if st.session_state.mock_score else 0

            result_col1, result_col2, result_col3 = st.columns(3)

            with result_col1:
                st.metric("Final Score", avg_mock_score)

            with result_col2:
                st.metric("Questions Completed", len(st.session_state.mock_score))

            with result_col3:
                if avg_mock_score >= 8:
                    st.metric("Verdict", "Excellent")
                elif avg_mock_score >= 6:
                    st.metric("Verdict", "Good")
                else:
                    st.metric("Verdict", "Needs Practice")

            if avg_mock_score >= 8:
                st.success("Excellent - Strong SQL interview performance.")
            elif avg_mock_score >= 6:
                st.info("Good - Solid fundamentals, with some areas to improve.")
            else:
                st.error("Needs more practice before a live SQL interview.")

            st.write("### Question-wise Performance")
            st.table([
                {
                    "Question": result["title"],
                    "Topic": result["topic"],
                    "Difficulty": result["difficulty"],
                    "Verdict": result["verdict"],
                    "Score": result["score"]
                }
                for result in st.session_state.mock_results
            ])

            with st.expander("Review Suggested Solutions"):
                for i, result in enumerate(st.session_state.mock_results, start=1):
                    st.write(f"**{i}. {result['title']}**")
                    st.write(f"Topic: {result['topic']} | Difficulty: {result['difficulty']}")
                    st.write(f"Verdict: {result['verdict']} | Score: {result['score']}")
                    st.code(result["improved_query"], language="sql")
                    st.write(result["explanation"])
                    st.markdown("---")

            bottom_col1, bottom_col2 = st.columns(2)

            with bottom_col1:
                if st.button("Restart Mock Interview"):
                    start_mock_interview()
                    st.rerun()

            with bottom_col2:
                if st.button("Exit Mock Interview"):
                    exit_mock_interview()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if tab2:
    st.session_state.active_tab = "Feedback"
    st.subheader("Feedback")

    if st.session_state.latest_feedback:
        feedback = st.session_state.latest_feedback
        verdict_color = get_verdict_color(feedback["verdict"])

        st.markdown(
            f"""
            <div class="verdict-banner" style="background-color:{verdict_color};">
                Verdict: {feedback['verdict']} | Score: {feedback['score']} / 10
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
        st.write("### Mistakes")
        for mistake in feedback["mistakes"]:
            st.write(f"- {mistake}")

        st.markdown('<hr class="soft">', unsafe_allow_html=True)

        st.write("### Improved Query")
        st.code(feedback["improved_query"], language="sql")

        st.markdown('<hr class="soft">', unsafe_allow_html=True)

        st.write("### Explanation")
        st.write(feedback["explanation"])

        st.markdown('<hr class="soft">', unsafe_allow_html=True)

        st.write("### Next Recommendation")
        st.info(feedback["next_recommendation"])

        st.write("### Adaptive Learning Update")
        if st.session_state.current_difficulty == "Medium":
            st.success("You are doing well. The coach has increased your recommended difficulty to Medium.")
        else:
            st.info(f"Recommended difficulty remains: {st.session_state.current_difficulty}")

        if st.session_state.recommended_question:
            rq = st.session_state.recommended_question

            st.write("### Recommended Next Question")
            st.markdown(
                f"""
                <div class="badge-row">
                    <span class="badge">{rq['title']}</span>
                    <span class="badge">Topic: {rq['topic']}</span>
                    <span class="badge">Difficulty: {rq['difficulty']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write(rq["prompt"])

            if st.button("Start This Question"):
                st.session_state.current_question = rq
                st.session_state.latest_feedback = None
                st.session_state.last_submitted_sql = ""
                st.session_state.selected_topic = rq["topic"]
                st.session_state.selected_difficulty = rq["difficulty"]
                st.session_state.active_tab = "Practice"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No feedback yet. Submit an answer in the Practice tab.")

if tab3:
    st.session_state.active_tab = "Progress"
    st.subheader("Progress Dashboard")

    total_attempts = get_total_attempts()
    avg_score = get_average_score()
    weakest_topic = get_weakest_topic()
    best_topic = get_best_topic()
    attempts = get_all_attempts()
    summary = get_topic_summary()
    level = get_level(avg_score)

    progress_percent = min(100, total_attempts * 10)
    st.progress(progress_percent)
    st.caption(f"Learning Progress: {progress_percent}%")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Attempts", total_attempts)

    with col2:
        st.metric("Average Score", avg_score)

    with col3:
        st.metric("Weakest Topic", weakest_topic if weakest_topic else "N/A")

    with col4:
        st.metric("Best Topic", best_topic if best_topic else "N/A")

    with col5:
        st.metric("Current Streak", st.session_state.streak)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write(f"### Current Level: {level}")
    st.info(f"Adaptive Engine Difficulty: {st.session_state.current_difficulty}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write("### Topic Performance")
    if summary:
        st.table([
            {
                "Topic": row[0],
                "Attempts": row[1],
                "Average Score": row[2]
            }
            for row in summary
        ])
    else:
        st.info("No attempts yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write("### Recent Attempts")
    if attempts:
        st.table([
            {
                "Question ID": row[1],
                "Topic": row[2],
                "Difficulty": row[3],
                "Verdict": row[5],
                "Score": row[6],
                "Created At": row[8]
            }
            for row in attempts[:8]
        ])
    else:
        st.info("No attempts recorded yet.")
    st.markdown('</div>', unsafe_allow_html=True)
