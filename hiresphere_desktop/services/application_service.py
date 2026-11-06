from database import connect
from services.matching_engine import score_resume

def apply(user_id,job_id):
    with connect() as c:
        r=c.execute('SELECT * FROM Resumes WHERE user_id=? ORDER BY created_at DESC LIMIT 1',(user_id,)).fetchone()
        j=c.execute('SELECT * FROM Jobs WHERE id=?',(job_id,)).fetchone()
        if not j: raise ValueError('This job is no longer available.')
        match=score_resume(dict(r) if r else {},dict(j))
        c.execute('INSERT INTO Applications(job_id,applicant_id,resume_id,match_score,matching_skills,missing_skills) VALUES(?,?,?,?,?,?)',(job_id,user_id,r['id'] if r else None,match['score'],', '.join(match['matching']),', '.join(match['missing'])))
    return match
