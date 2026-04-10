QUESTIONS = [

# ================= BASIC FILTERING =================

{"id": 1, "topic": "Filtering", "difficulty": "Easy", "title": "Employees above salary",
 "prompt": "Find employees with salary greater than 50000.",
 "expected_concepts": ["SELECT", "WHERE"]},

{"id": 2, "topic": "Filtering", "difficulty": "Easy", "title": "Employees in department",
 "prompt": "Find employees in department_id 50.",
 "expected_concepts": ["SELECT", "WHERE"]},

{"id": 3, "topic": "Filtering", "difficulty": "Easy", "title": "Orders above amount",
 "prompt": "Find orders where amount is greater than 500.",
 "expected_concepts": ["SELECT", "WHERE"]},

{"id": 4, "topic": "Filtering", "difficulty": "Medium", "title": "Date filter",
 "prompt": "Find customers who joined after 2023-01-01.",
 "expected_concepts": ["SELECT", "WHERE"]},

{"id": 5, "topic": "Filtering", "difficulty": "Medium", "title": "Range filter",
 "prompt": "Find products priced between 100 and 500.",
 "expected_concepts": ["SELECT", "WHERE"]},

# ================= ORDERING =================

{"id": 6, "topic": "Ordering", "difficulty": "Easy", "title": "Sort salary",
 "prompt": "List employees ordered by salary descending.",
 "expected_concepts": ["ORDER BY"]},

{"id": 7, "topic": "Ordering", "difficulty": "Easy", "title": "Latest orders",
 "prompt": "Show orders sorted by order date descending.",
 "expected_concepts": ["ORDER BY"]},

{"id": 8, "topic": "Ordering", "difficulty": "Medium", "title": "Top 3 salaries",
 "prompt": "Find top 3 highest paid employees.",
 "expected_concepts": ["ORDER BY"]},

{"id": 9, "topic": "Ordering", "difficulty": "Medium", "title": "Top customers",
 "prompt": "Find top 5 customers by total spend.",
 "expected_concepts": ["GROUP BY", "SUM", "ORDER BY"]},

# ================= JOINS =================

{"id": 10, "topic": "Joins", "difficulty": "Easy", "title": "Customer orders",
 "prompt": "Display customer names with their orders.",
 "expected_concepts": ["INNER JOIN"]},

{"id": 11, "topic": "Joins", "difficulty": "Easy", "title": "Orders with product",
 "prompt": "Show order ID with product name.",
 "expected_concepts": ["INNER JOIN"]},

{"id": 12, "topic": "Joins", "difficulty": "Medium", "title": "Customers without orders",
 "prompt": "Find customers who have not placed any orders.",
 "expected_concepts": ["LEFT JOIN", "NULL filter"]},

{"id": 13, "topic": "Joins", "difficulty": "Medium", "title": "Products never ordered",
 "prompt": "Find products never ordered.",
 "expected_concepts": ["LEFT JOIN", "NULL filter"]},

{"id": 14, "topic": "Joins", "difficulty": "Medium", "title": "Employees and department",
 "prompt": "Display employee name with department name.",
 "expected_concepts": ["INNER JOIN"]},

{"id": 15, "topic": "Joins", "difficulty": "Medium", "title": "Multi-table join",
 "prompt": "Display employees with department and location.",
 "expected_concepts": ["JOIN"]},

# ================= GROUP BY =================

{"id": 16, "topic": "Group By", "difficulty": "Easy", "title": "Orders per customer",
 "prompt": "Count number of orders per customer.",
 "expected_concepts": ["GROUP BY", "COUNT"]},

{"id": 17, "topic": "Group By", "difficulty": "Easy", "title": "Customer orders >5",
 "prompt": "Find customers with more than 5 orders.",
 "expected_concepts": ["GROUP BY", "COUNT", "HAVING"]},

{"id": 18, "topic": "Group By", "difficulty": "Medium", "title": "Avg salary per dept",
 "prompt": "Find average salary per department.",
 "expected_concepts": ["GROUP BY", "AVG"]},

{"id": 19, "topic": "Group By", "difficulty": "Medium", "title": "Top selling product",
 "prompt": "Identify the most selling product.",
 "expected_concepts": ["GROUP BY", "SUM", "ORDER BY"]},

{"id": 20, "topic": "Group By", "difficulty": "Medium", "title": "Departments >10 employees",
 "prompt": "Find departments with more than 10 employees.",
 "expected_concepts": ["GROUP BY", "COUNT", "HAVING"]},

{"id": 21, "topic": "Group By", "difficulty": "Medium", "title": "Monthly sales",
 "prompt": "Calculate total sales per month.",
 "expected_concepts": ["GROUP BY", "SUM"]},

# ================= SUBQUERIES =================

{"id": 22, "topic": "Subqueries", "difficulty": "Easy", "title": "Above avg salary",
 "prompt": "Find employees whose salary is above average.",
 "expected_concepts": ["SUBQUERY", "AVG"]},

{"id": 23, "topic": "Subqueries", "difficulty": "Easy", "title": "Max salary employee",
 "prompt": "Find employee with highest salary.",
 "expected_concepts": ["SUBQUERY", "MAX"]},

{"id": 24, "topic": "Subqueries", "difficulty": "Medium", "title": "Dept avg salary",
 "prompt": "Find employees whose salary is above department average.",
 "expected_concepts": ["CORRELATED SUBQUERY", "AVG"]},

{"id": 25, "topic": "Subqueries", "difficulty": "Medium", "title": "Second highest salary",
 "prompt": "Find second highest salary.",
 "expected_concepts": ["SUBQUERY"]},

{"id": 26, "topic": "Subqueries", "difficulty": "Medium", "title": "Customers no orders",
 "prompt": "Find customers not in orders table.",
 "expected_concepts": ["SUBQUERY", "NOT IN or NOT EXISTS"]},

{"id": 27, "topic": "Subqueries", "difficulty": "Medium", "title": "Orders above customer avg",
 "prompt": "Find orders greater than customer's average order.",
 "expected_concepts": ["CORRELATED SUBQUERY", "AVG"]},

# ================= CASE =================

{"id": 28, "topic": "Case Based", "difficulty": "Easy", "title": "Triangle classification",
 "prompt": "Classify triangles as Equilateral, Isosceles, Scalene, or Not a Triangle.",
 "expected_concepts": ["CASE WHEN"]},

{"id": 29, "topic": "Case Based", "difficulty": "Easy", "title": "Salary bands",
 "prompt": "Classify employees into Low, Medium, High salary.",
 "expected_concepts": ["CASE WHEN"]},

{"id": 30, "topic": "Case Based", "difficulty": "Medium", "title": "Commission flag",
 "prompt": "Label employees as Commissioned or Not.",
 "expected_concepts": ["CASE WHEN"]},

# ================= WINDOW FUNCTIONS =================

{"id": 31, "topic": "Window Functions", "difficulty": "Medium", "title": "Salary rank",
 "prompt": "Rank employees by salary.",
 "expected_concepts": ["WINDOW FUNCTION", "ORDER BY"]},

{"id": 32, "topic": "Window Functions", "difficulty": "Medium", "title": "Dept rank",
 "prompt": "Rank employees within department.",
 "expected_concepts": ["WINDOW FUNCTION", "PARTITION BY"]},

{"id": 33, "topic": "Window Functions", "difficulty": "Medium", "title": "Running total",
 "prompt": "Calculate running total of sales.",
 "expected_concepts": ["WINDOW FUNCTION", "SUM"]},

# ================= BUSINESS SQL =================

{"id": 34, "topic": "Business SQL", "difficulty": "Easy", "title": "Application status",
 "prompt": "Count applications by status.",
 "expected_concepts": ["GROUP BY", "COUNT"]},

{"id": 35, "topic": "Business SQL", "difficulty": "Medium", "title": "Most active customer",
 "prompt": "Find customer with highest number of orders.",
 "expected_concepts": ["GROUP BY", "COUNT", "ORDER BY"]},

{"id": 36, "topic": "Business SQL", "difficulty": "Medium", "title": "Revenue by category",
 "prompt": "Calculate revenue by product category.",
 "expected_concepts": ["JOIN", "GROUP BY", "SUM"]},

{"id": 37, "topic": "Business SQL", "difficulty": "Medium", "title": "Repeat customers",
 "prompt": "Find customers with more than one order.",
 "expected_concepts": ["GROUP BY", "COUNT", "HAVING"]},

{"id": 38, "topic": "Business SQL", "difficulty": "Medium", "title": "Headcount",
 "prompt": "Calculate employees per department.",
 "expected_concepts": ["GROUP BY", "COUNT"]},

{"id": 39, "topic": "Business SQL", "difficulty": "Medium", "title": "Manager team size",
 "prompt": "Find number of employees per manager.",
 "expected_concepts": ["GROUP BY", "COUNT"]},

{"id": 40, "topic": "Business SQL", "difficulty": "Medium", "title": "Top department",
 "prompt": "Find department with highest avg salary.",
 "expected_concepts": ["GROUP BY", "AVG", "ORDER BY"]},

]