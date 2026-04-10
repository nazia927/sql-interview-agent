import sqlite3

DB_NAME = "attempts.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            topic TEXT,
            difficulty TEXT,
            user_sql TEXT,
            verdict TEXT,
            score INTEGER,
            weaknesses TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_attempt(question_id, topic, difficulty, user_sql, verdict, score, weaknesses):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attempts (question_id, topic, difficulty, user_sql, verdict, score, weaknesses)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (question_id, topic, difficulty, user_sql, verdict, score, weaknesses))

    conn.commit()
    conn.close()


def get_all_attempts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question_id, topic, difficulty, user_sql, verdict, score, weaknesses, created_at
        FROM attempts
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_topic_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, COUNT(*) as attempts, ROUND(AVG(score), 2) as avg_score
        FROM attempts
        GROUP BY topic
        ORDER BY avg_score ASC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_weakest_topic():
    summary = get_topic_summary()
    if summary:
        return summary[0][0]
    return None


def get_total_attempts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM attempts")
    total = cursor.fetchone()[0]

    conn.close()
    return total


def get_average_score():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT AVG(score) FROM attempts")
    result = cursor.fetchone()[0]

    conn.close()
    return round(result, 2) if result is not None else 0


def get_best_topic():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, ROUND(AVG(score), 2) as avg_score
        FROM attempts
        GROUP BY topic
        ORDER BY avg_score DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None