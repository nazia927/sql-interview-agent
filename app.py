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

st.set_page_config(page_title="AI SQL Interview Coach", layout="wide")

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


st.title("AI SQL Interview Coach")
st.caption("Practice SQL interview questions, get feedback, track weak areas, improve with adaptive difficulty, and simulate mock interviews.")

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

        if not st.session_state.current_question:
            st.info("Click 'Generate Question' to start practicing.")

        if st.session_state.current_question:
            q = st.session_state.current_question

            st.markdown(f"### {q['title']}")
            st.write(q["prompt"])
            st.write(f"**Topic:** {q['topic']}")
            st.write(f"**Difficulty:** {q['difficulty']}")
            st.write("**Expected Concepts:** " + ", ".join(q["expected_concepts"]))

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

    else:
        st.subheader("Mock Interview Mode")
        st.warning("You are in mock interview mode. Feedback is hidden until the end.")

        if not st.session_state.mock_completed and st.session_state.mock_questions:
            q = st.session_state.mock_questions[st.session_state.mock_index]

            total_questions = len(st.session_state.mock_questions)
            st.progress((st.session_state.mock_index + 1) / total_questions)
            st.caption(f"Question {st.session_state.mock_index + 1} of {total_questions}")

            st.markdown(f"### {q['title']}")
            st.write(q["prompt"])
            st.write(f"**Topic:** {q['topic']}")
            st.write(f"**Difficulty:** {q['difficulty']}")

            mock_key = f"mock_answer_{st.session_state.mock_index}"
            user_sql = st.text_area(
                "Your Answer",
                key=mock_key,
                height=220,
                placeholder="Write your SQL query here..."
            )

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

if tab2:
    st.session_state.active_tab = "Feedback"
    st.subheader("Feedback")

    if st.session_state.latest_feedback:
        feedback = st.session_state.latest_feedback
        verdict_color = get_verdict_color(feedback["verdict"])

        st.markdown(
            f"""
            <div style="
                padding:16px;
                border-radius:12px;
                background-color:{verdict_color};
                color:white;
                font-weight:600;
                margin-bottom:16px;
            ">
                Verdict: {feedback['verdict']} | Score: {feedback['score']} / 10
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("### Mistakes")
        for mistake in feedback["mistakes"]:
            st.write(f"- {mistake}")

        st.write("### Improved Query")
        st.code(feedback["improved_query"], language="sql")

        st.write("### Explanation")
        st.write(feedback["explanation"])

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
                **{rq['title']}**  
                Topic: {rq['topic']}  
                Difficulty: {rq['difficulty']}  

                {rq['prompt']}
                """
            )

            if st.button("Start This Question"):
                st.session_state.current_question = rq
                st.session_state.latest_feedback = None
                st.session_state.last_submitted_sql = ""
                st.session_state.selected_topic = rq["topic"]
                st.session_state.selected_difficulty = rq["difficulty"]
                st.session_state.active_tab = "Practice"
                st.rerun()
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

    st.write(f"### Current Level: {level}")
    st.info(f"Adaptive Engine Difficulty: {st.session_state.current_difficulty}")

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