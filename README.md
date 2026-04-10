# AI SQL Interview Coach

An AI-powered SQL interview practice app built with Streamlit.

It helps users practice SQL questions by topic and difficulty, receive structured feedback, track weak areas, and improve through adaptive learning and mock interview simulation.

## Features

- Practice SQL questions across multiple topics
- Filter by Easy and Medium difficulty
- Rule-based SQL evaluation with feedback
- Improved query suggestions
- Adaptive difficulty progression
- Recommended next question
- Progress dashboard with streak and level tracking
- Mock interview mode with final score and review

## Topics Covered

- Filtering
- Ordering
- Joins
- Group By
- Subqueries
- Case Based Questions
- Window Functions
- Business SQL

## Files

- `app.py` — main Streamlit app
- `questions.py` — SQL question bank
- `evaluator.py` — evaluation engine
- `db.py` — SQLite database logic
- `requirements.txt` — dependencies

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
