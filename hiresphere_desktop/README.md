# HireSphere AI

Native Python desktop application for recruitment and career development. The interface is built with CustomTkinter (with a standard Tkinter fallback), and all account, job, resume, application and interview data is stored locally in SQLite.

## Run

Requires Python 3.11 or newer. In a terminal:

```powershell
cd hiresphere_desktop
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

On macOS or Linux, activate with `source .venv/bin/activate`. `python main.py` creates the database on first launch. The local database is `hiresphere.db`.

## Demo accounts

The app creates these accounts on startup; choose the matching portal on the sign-in screen:

| Portal | Email | Password |
| --- | --- | --- |
| Applicant | applicant@hiresphere.demo | demo1234 |
| Recruiter | recruiter@hiresphere.demo | demo1234 |

Register your own account for a separate profile. Passwords use bcrypt hashes.

## Features

- Applicant and recruiter portals with role checked sign-in.
- Recruiter job creation and closing, applicant job search and applications, and persistent application status changes.
- PDF text extraction with PyMuPDF, identifiable resume sections, extracted skill tags, and a section completeness score. Image-only scans need OCR and are reported as such.
- Deterministic resume/job score with the requested 40/25/15/10/10 weights and visible matching and missing skills. AI scores never automatically reject anyone.
- Candidate resume review, shortlist/status workflow, and interview scheduling.
- Career guidance based on saved resume skills and skills in live openings.
- Mock interview demo question sets. Gemini feedback is enabled only with a `GEMINI_API_KEY`; without it, the UI explicitly says evaluation is unavailable. Copy `.env.example` to `.env` and add your key to enable.
- Recruiter hiring funnel chart and light/dark appearance setting.

Resume extraction and Gemini calls run off the UI thread. SQLite is local to this installation; use the same project directory to retain its database.

## Notes

The matching score is a transparent heuristic, not a hiring decision. PDF section identification is intentionally conservative and depends on readable text and common section headings. Interview questions in demo mode are predefined and are not represented as AI generated.
