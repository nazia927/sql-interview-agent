import re


def evaluate_sql_answer(question_prompt, expected_concepts, user_sql, topic, difficulty):
    sql = normalize_sql(user_sql)
    prompt = question_prompt.lower().strip()
    expected = [c.lower().strip() for c in expected_concepts]

    concept_checks = build_concept_checks(sql)
    matched_count = 0
    missing_concepts = []

    for concept in expected:
        if concept_matches(concept, concept_checks):
            matched_count += 1
        else:
            missing_concepts.append(concept)

    base_score = score_from_match_ratio(matched_count, len(expected), sql)
    verdict = verdict_from_score(base_score)
    mistakes = build_mistakes(sql, expected, missing_concepts, prompt, topic)
    improved_query = build_improved_query(topic, prompt)
    explanation = build_explanation(topic, matched_count, len(expected), verdict, missing_concepts)
    next_recommendation = build_next_recommendation(topic, difficulty, missing_concepts)

    return {
        "verdict": verdict,
        "score": base_score,
        "mistakes": mistakes,
        "improved_query": improved_query,
        "explanation": explanation,
        "weakness_topic": topic,
        "next_recommendation": next_recommendation
    }


def normalize_sql(user_sql):
    return re.sub(r"\s+", " ", user_sql.lower().strip())


def build_concept_checks(sql):
    return {
        "select": "select" in sql,
        "from": "from" in sql,
        "where": " where " in f" {sql} ",
        "order by": "order by" in sql,
        "group by": "group by" in sql,
        "having": "having" in sql,
        "inner join": "inner join" in sql or (" join " in f" {sql} " and "left join" not in sql and "right join" not in sql and "full join" not in sql),
        "left join": "left join" in sql,
        "join": " join " in f" {sql} ",
        "distinct": "distinct" in sql,
        "count": "count(" in sql,
        "sum": "sum(" in sql,
        "avg": "avg(" in sql,
        "max": "max(" in sql,
        "min": "min(" in sql,
        "case when": "case when" in sql or ("case" in sql and "when" in sql),
        "subquery": sql.count("select") >= 2,
        "correlated subquery": sql.count("select") >= 2,
        "not in or not exists": "not in" in sql or "not exists" in sql,
        "null filter": "is null" in sql or "is not null" in sql,
        "window function": any(fn in sql for fn in [" over(", " over (", "rank()", "dense_rank()", "row_number()", "lag(", "lead("]),
        "partition by": "partition by" in sql,
        "rank": "rank()" in sql or "dense_rank()" in sql or "row_number()" in sql,
        "lag": "lag(" in sql,
        "between": " between " in f" {sql} ",
        "like": " like " in f" {sql} ",
        "in": " in " in f" {sql} ",
        "limit": "limit " in sql,
        "top": re.search(r"\btop\s+\d+", sql) is not None
    }


def concept_matches(concept, checks):
    mapping = {
        "select": checks["select"],
        "where": checks["where"],
        "order by": checks["order by"],
        "group by": checks["group by"],
        "having": checks["having"],
        "inner join": checks["inner join"],
        "left join": checks["left join"],
        "join": checks["join"],
        "distinct": checks["distinct"],
        "count": checks["count"],
        "sum": checks["sum"],
        "avg": checks["avg"],
        "max": checks["max"],
        "min": checks["min"],
        "case when": checks["case when"],
        "subquery": checks["subquery"],
        "correlated subquery": checks["correlated subquery"],
        "not in or not exists": checks["not in or not exists"],
        "null filter": checks["null filter"],
        "window function": checks["window function"],
        "partition by": checks["partition by"],
    }

    return mapping.get(concept, False)


def score_from_match_ratio(matched_count, total_expected, sql):
    if "select" not in sql:
        return 1

    if total_expected == 0:
        return 5

    ratio = matched_count / total_expected

    if ratio == 1:
        return 9
    if ratio >= 0.8:
        return 8
    if ratio >= 0.6:
        return 7
    if ratio >= 0.5:
        return 6
    if ratio >= 0.3:
        return 4
    return 2


def verdict_from_score(score):
    if score >= 8:
        return "Correct"
    if score >= 5:
        return "Partially Correct"
    return "Incorrect"


def build_mistakes(sql, expected, missing_concepts, prompt, topic):
    mistakes = []

    if "select" not in sql:
        mistakes.append("Your answer does not include a SELECT statement.")
    if "from" not in sql and topic not in ["Case Based"]:
        mistakes.append("Your answer does not include a FROM clause.")

    for concept in missing_concepts:
        mistakes.append(f"Missing or incorrect use of: {concept.upper()}.")

    if topic == "Filtering":
        if "where" not in sql:
            mistakes.append("Filtering questions usually require a WHERE clause.")
        if "between" in prompt and "between" not in sql and ">= " not in sql and "<=" not in sql:
            mistakes.append("This question likely needs a range condition using BETWEEN or comparison operators.")
        if "starts with" in prompt and "like" not in sql:
            mistakes.append("This question likely needs LIKE for pattern matching.")

    if topic == "Ordering":
        if "order by" not in sql:
            mistakes.append("Ordering questions usually require ORDER BY.")
        if ("top" in prompt or "highest" in prompt or "latest" in prompt) and ("limit" not in sql and "top" not in sql and "fetch first" not in sql and "rownum" not in sql):
            mistakes.append("This question likely needs a row limiting clause such as LIMIT or TOP.")

    if topic == "Joins":
        if "join" not in sql:
            mistakes.append("Join questions usually require at least one JOIN.")
        if "without" in prompt or "not assigned" in prompt or "never" in prompt:
            if "left join" not in sql and "not exists" not in sql and "not in" not in sql:
                mistakes.append("This question likely needs LEFT JOIN with NULL filtering or a NOT EXISTS/NOT IN approach.")

    if topic == "Group By":
        if "group by" not in sql:
            mistakes.append("Aggregation questions usually require GROUP BY.")
        if ("more than" in prompt or "greater than" in prompt) and ("having" not in sql):
            mistakes.append("This grouped filter likely needs a HAVING clause.")

    if topic == "Subqueries":
        if sql.count("select") < 2:
            mistakes.append("Subquery questions usually require a nested SELECT.")
        if "department average" in prompt and sql.count("select") < 2:
            mistakes.append("This looks like a correlated subquery problem.")

    if topic == "Case Based":
        if "case" not in sql or "when" not in sql:
            mistakes.append("Case-based questions usually require CASE WHEN logic.")

    if topic == "Window Functions":
        if "over" not in sql:
            mistakes.append("Window function questions usually require an OVER clause.")
        if "within each department" in prompt and "partition by" not in sql:
            mistakes.append("This question likely needs PARTITION BY.")
        if "rank" in prompt and not any(x in sql for x in ["rank()", "dense_rank()", "row_number()"]):
            mistakes.append("This question likely needs RANK, DENSE_RANK, or ROW_NUMBER.")
        if "previous" in prompt and "lag(" not in sql:
            mistakes.append("This question likely needs LAG().")
        if "running total" in prompt and ("sum(" not in sql or "over" not in sql):
            mistakes.append("This question likely needs SUM() OVER(...) for a running total.")

    if not mistakes:
        mistakes.append("Good job. Your answer includes the main expected SQL logic.")

    return dedupe_preserve_order(mistakes)


def build_explanation(topic, matched_count, total_expected, verdict, missing_concepts):
    if total_expected == 0:
        return f"This evaluation is based on the expected SQL approach for {topic}. Your query was assessed for overall structure and logic."

    if verdict == "Correct":
        return (
            f"Your query matches the expected SQL approach for {topic}. "
            f"It satisfied {matched_count} out of {total_expected} expected concepts."
        )

    if verdict == "Partially Correct":
        return (
            f"Your query shows the right direction for {topic}, but it is incomplete. "
            f"It matched {matched_count} out of {total_expected} expected concepts. "
            f"The main gaps are: {', '.join(missing_concepts)}."
        )

    return (
        f"Your query does not yet match the expected structure for {topic}. "
        f"It matched only {matched_count} out of {total_expected} expected concepts. "
        f"Focus on: {', '.join(missing_concepts)}."
    )


def build_next_recommendation(topic, difficulty, missing_concepts):
    if missing_concepts:
        return f"Practice more {difficulty} {topic} questions focusing on {', '.join(missing_concepts[:2])}."
    return f"Try another {difficulty} {topic} question or move to a harder difficulty."


def dedupe_preserve_order(items):
    seen = set()
    output = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def build_improved_query(topic, prompt):
    if "customers with more than 5 orders" in prompt or "count the number of customers who placed more than 5 orders" in prompt:
        return """SELECT cust_id
FROM orders
GROUP BY cust_id
HAVING COUNT(*) > 5;"""

    if "count how many customers have placed more than 5 orders" in prompt:
        return """SELECT COUNT(*) AS customer_count
FROM (
    SELECT cust_id
    FROM orders
    GROUP BY cust_id
    HAVING COUNT(*) > 5
) t;"""

    if "identify the most selling product" in prompt or "top selling product" in prompt:
        return """SELECT product_id, SUM(quantity) AS total_quantity
FROM order_items
GROUP BY product_id
ORDER BY total_quantity DESC
LIMIT 1;"""

    if "find employees whose salary is above average" in prompt or "salary is above average" in prompt:
        return """SELECT employee_name, salary
FROM employees
WHERE salary > (
    SELECT AVG(salary)
    FROM employees
);"""

    if "salary is above department average" in prompt or "greater than the average salary of their own department" in prompt:
        return """SELECT e.employee_name, e.salary, e.department_id
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
);"""

    if "second highest salary" in prompt:
        return """SELECT MAX(salary) AS second_highest_salary
FROM employees
WHERE salary < (
    SELECT MAX(salary)
    FROM employees
);"""

    if "find customers not in orders table" in prompt or "customers who do not appear in the orders table" in prompt:
        return """SELECT customer_name
FROM customers
WHERE cust_id NOT IN (
    SELECT cust_id
    FROM orders
);"""

    if "display customer names with their orders" in prompt:
        return """SELECT c.customer_name, o.order_id
FROM customers c
INNER JOIN orders o
    ON c.cust_id = o.cust_id;"""

    if "customers who have not placed any orders" in prompt or "customers without orders" in prompt:
        return """SELECT c.customer_name
FROM customers c
LEFT JOIN orders o
    ON c.cust_id = o.cust_id
WHERE o.order_id IS NULL;"""

    if "products never ordered" in prompt:
        return """SELECT p.product_name
FROM products p
LEFT JOIN order_items oi
    ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;"""

    if "employee name with department name" in prompt or "employee's first_name, last_name, and department_name" in prompt:
        return """SELECT e.first_name, e.last_name, d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;"""

    if "count number of orders per customer" in prompt:
        return """SELECT cust_id, COUNT(*) AS total_orders
FROM orders
GROUP BY cust_id;"""

    if "average salary per department" in prompt:
        return """SELECT department_id, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;"""

    if "departments with more than 10 employees" in prompt:
        return """SELECT department_id, COUNT(*) AS employee_count
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 10;"""

    if "calculate total sales per month" in prompt:
        return """SELECT DATE_TRUNC('month', order_date) AS month, SUM(amount) AS total_sales
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;"""

    if "classify triangles" in prompt:
        return """SELECT A, B, C,
CASE
    WHEN A + B <= C OR A + C <= B OR B + C <= A THEN 'Not A Triangle'
    WHEN A = B AND B = C THEN 'Equilateral'
    WHEN A = B OR B = C OR A = C THEN 'Isosceles'
    ELSE 'Scalene'
END AS triangle_type
FROM TRIANGLES;"""

    if "classify employees into low, medium, high salary" in prompt:
        return """SELECT employee_name, salary,
CASE
    WHEN salary < 4000 THEN 'Low'
    WHEN salary BETWEEN 4000 AND 9000 THEN 'Medium'
    ELSE 'High'
END AS salary_band
FROM employees;"""

    if "label employees as commissioned or not" in prompt:
        return """SELECT employee_name,
CASE
    WHEN commission_pct IS NOT NULL THEN 'Commissioned'
    ELSE 'Not Commissioned'
END AS commission_label
FROM employees;"""

    if "rank employees by salary" in prompt:
        return """SELECT employee_name, salary,
RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;"""

    if "rank employees within department" in prompt:
        return """SELECT employee_name, department_id, salary,
RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_salary_rank
FROM employees;"""

    if "calculate running total of sales" in prompt:
        return """SELECT order_date, amount,
SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders;"""

    if "count applications by status" in prompt:
        return """SELECT status, COUNT(*) AS total_applications
FROM applications
GROUP BY status;"""

    if "find customer with highest number of orders" in prompt:
        return """SELECT cust_id, COUNT(*) AS total_orders
FROM orders
GROUP BY cust_id
ORDER BY total_orders DESC
LIMIT 1;"""

    if "calculate revenue by product category" in prompt:
        return """SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
INNER JOIN products p
    ON oi.product_id = p.product_id
INNER JOIN categories c
    ON p.category_id = c.category_id
GROUP BY c.category_name;"""

    if "find customers with more than one order" in prompt:
        return """SELECT cust_id, COUNT(*) AS total_orders
FROM orders
GROUP BY cust_id
HAVING COUNT(*) > 1;"""

    if "calculate employees per department" in prompt:
        return """SELECT department_id, COUNT(*) AS headcount
FROM employees
GROUP BY department_id;"""

    if "find number of employees per manager" in prompt:
        return """SELECT manager_id, COUNT(*) AS team_size
FROM employees
GROUP BY manager_id;"""

    if "find department with highest avg salary" in prompt:
        return """SELECT department_id, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
ORDER BY avg_salary DESC
LIMIT 1;"""

    if "employees with salary greater than 50000" in prompt:
        return """SELECT first_name, last_name, salary
FROM employees
WHERE salary > 50000
ORDER BY salary DESC;"""

    if "find all employees hired after 2020-01-01" in prompt:
        return """SELECT *
FROM employees
WHERE hire_date > '2020-01-01';"""

    if "list all employees who belong to department_id 50" in prompt:
        return """SELECT *
FROM employees
WHERE department_id = 50;"""

    if "employees whose commission_pct is not null" in prompt:
        return """SELECT *
FROM employees
WHERE commission_pct IS NOT NULL;"""

    if "salary is between 4000 and 9000" in prompt:
        return """SELECT *
FROM employees
WHERE salary BETWEEN 4000 AND 9000;"""

    if "last_name starts with 's'" in prompt:
        return """SELECT *
FROM employees
WHERE last_name LIKE 'S%';"""

    if "department_id 30, 50, or 90" in prompt:
        return """SELECT *
FROM employees
WHERE department_id IN (30, 50, 90);"""

    if "list employees ordered by salary descending" in prompt:
        return """SELECT *
FROM employees
ORDER BY salary DESC;"""

    if "show orders sorted by order date descending" in prompt:
        return """SELECT *
FROM orders
ORDER BY order_date DESC;"""

    if "find top 3 highest paid employees" in prompt or "display the top 5 highest paid employees" in prompt:
        return """SELECT *
FROM employees
ORDER BY salary DESC
LIMIT 3;"""

    if "top 5 customers by total spend" in prompt:
        return """SELECT cust_id, SUM(amount) AS total_spend
FROM orders
GROUP BY cust_id
ORDER BY total_spend DESC
LIMIT 5;"""

    return """SELECT *
FROM table_name;"""