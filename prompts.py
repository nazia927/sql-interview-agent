def build_evaluation_prompt(question_prompt, expected_concepts, user_sql):
    return f"""
You are an expert SQL interviewer.

Evaluate the candidate's SQL answer based on the interview question.

Interview Question:
{question_prompt}

Expected Concepts:
{", ".join(expected_concepts)}

Candidate SQL Answer:
{user_sql}

Evaluation Rules:
- Focus mainly on logical correctness.
- Do not heavily penalize small syntax issues like missing semicolons.
- Reward partially correct reasoning.
- Be clear and concise.
- If the answer is wrong, explain exactly what is missing or incorrect.
- Return only valid JSON.
- Do not include markdown fences.

Return JSON in this exact format:
{{
  "verdict": "Correct or Partially Correct or Incorrect",
  "score": 0,
  "mistakes": ["mistake 1", "mistake 2"],
  "improved_query": "correct SQL here",
  "explanation": "short explanation",
  "weakness_topic": "topic name",
  "next_recommendation": "what to practice next"
}}
"""