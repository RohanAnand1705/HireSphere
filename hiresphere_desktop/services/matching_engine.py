"""Transparent, deterministic resume-to-job matching."""
import re

def tokens(value):
    return {x.lower() for x in re.findall(r"[a-zA-Z+#.]{2,}", value or "")}

def score_resume(resume, job):
    profile = resume or {}
    required = tokens(job.get("required_skills", ""))
    applicant = tokens(" ".join([profile.get("skills", ""), profile.get("projects", ""), profile.get("experience", ""), profile.get("education", ""), profile.get("certifications", "")]))
    matched = sorted(required & applicant)
    missing = sorted(required - applicant)
    skill = len(matched) / max(len(required), 1)
    project = 1.0 if tokens(job.get("title", "")) & tokens(profile.get("projects", "")) else min(.8, len(tokens(profile.get("projects", "")) & required) / max(len(required), 1))
    experience = 1.0 if profile.get("experience", "").strip() else 0.35
    education = 1.0 if profile.get("education", "").strip() else 0.35
    certs = 1.0 if profile.get("certifications", "").strip() else 0.35
    pct = round(100 * (.40*skill + .25*project + .15*experience + .10*education + .10*certs))
    return {"score": pct, "matching": matched, "missing": missing, "explanation": f"Skills {skill:.0%} (40%), project relevance {project:.0%} (25%), experience {experience:.0%} (15%), education {education:.0%} (10%), certifications {certs:.0%} (10%)."}
