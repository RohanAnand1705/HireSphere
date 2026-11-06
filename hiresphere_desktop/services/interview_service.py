"""Offline rule based mock interview prompts and answer evaluation."""
import re

BASE_BANK = {
    "Technical": [
        ("How would you diagnose and improve a slow SQL query?", ["explain", "index", "query plan", "filter", "measure"]),
        ("How do you make a software change safe to release?", ["test", "review", "small", "monitor", "rollback"]),
        ("Describe how you would design a reliable API for a client application.", ["validation", "error", "authentication", "status", "documentation"]),
    ],
    "HR": [
        ("What type of team and working environment help you do your best work?", ["communication", "feedback", "collaboration", "goals"]),
        ("What is one strength you would bring to this role?", ["example", "strength", "impact", "learning"]),
        ("Why are you interested in this role and organization?", ["role", "company", "contribute", "growth"]),
    ],
    "Behavioral": [
        ("Tell me about a difficult problem you solved. What was the outcome?", ["situation", "action", "result", "learned"]),
        ("Describe a time you received critical feedback and what you did with it.", ["feedback", "listen", "action", "improved"]),
        ("Tell me about a time you worked through a disagreement with a teammate.", ["understand", "communicate", "resolution", "result"]),
    ],
}

def question_bank(role, category, difficulty):
    prompts = BASE_BANK.get(category)
    if not prompts:
        raise ValueError("Choose Technical, HR, or Behavioral interview type.")
    role = (role or "your target role").strip()
    if category == "Technical" and role.lower() not in ("your target role", "software engineer", "developer"):
        prompts = [(q.replace("SQL query", f"{role} task"), keys) for q, keys in prompts]
    return [{"question": q, "keywords": keys, "difficulty": difficulty} for q, keys in prompts]

def evaluate_answer(question, answer):
    """Score keyword coverage and give transparent, non-generative feedback."""
    if not answer or not answer.strip():
        raise ValueError("Enter an answer before submitting it.")
    lowered = answer.lower()
    keywords = question["keywords"]
    found = [word for word in keywords if re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", lowered)]
    score = round(100 * len(found) / len(keywords))
    strengths = ("Covers: " + ", ".join(found) + ".") if found else "Your response is recorded. Add specific details that address the question."
    suggestions = [word for word in keywords if word not in found]
    improvement = ("Consider adding: " + ", ".join(suggestions[:3]) + ".") if suggestions else "Good coverage. Add a concrete example or measurable outcome to make it stronger."
    if len(answer.split()) < 20:
        improvement += " Expand your answer with context, your actions, and the outcome."
    return {"score": score, "matched_keywords": found, "feedback": strengths + " " + improvement}
