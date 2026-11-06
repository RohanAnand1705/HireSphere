# HireSphere AI

HireSphere AI is a native Python desktop app for applicant career development and recruiter hiring workflows. The product name includes “AI”; resume matching and mock interview feedback are deterministic, offline heuristics and are clearly presented as such. Core functionality does not use an external AI service or require internet access after dependencies are installed.

## Features

- Applicant and recruiter registration and login with bcrypt password hashing.
- Applicant dashboard, job search, saved jobs, applications, status tracking, resume analysis, career guidance, and interview practice.
- Recruiter dashboard, job creation/editing/closing, application review, candidate profiles, transparent match scoring, shortlisting, interview scheduling, and hiring charts.
- SQLite persistence with foreign keys and unique application-per-job constraints.
- PyMuPDF PDF text extraction with a clear message for image-only/scanned PDFs.
- Offline rule-based mock interview questions for Technical, HR, and Behavioral categories, with three difficulty choices, keyword coverage scoring, feedback, and a saved answer history.

## Technology and architecture

- Python 3.11+, Tkinter, and CustomTkinter.
- SQLite3 for local persistence.
- PyMuPDF for selectable PDF text extraction.
- Matplotlib for recruiter hiring funnel charts.
- bcrypt for password hashing. Pillow is installed by CustomTkinter as a transitive dependency.

`main.py` owns the GUI and navigation. `database.py` initializes the schema and provides SQLite connections. `services/` contains authentication, job and application operations, PDF parsing, matching, and interview evaluation. `tests/` contains standard-library `unittest` workflows.

## Requirements and installation

Install Python 3.11 or newer. Tkinter must be included with that Python installation (on Windows, use the standard python.org installer with Tcl/Tk selected).

### Windows PowerShell

```powershell
cd hiresphere_desktop
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### macOS or Linux

```bash
cd hiresphere_desktop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

No demo account is created. Register an applicant or recruiter account from the login screen.

## Applicant workflow

1. Register with the Applicant portal selected.
2. Upload a PDF in Resume Analyzer. The extracted text and detected sections are stored locally. A completeness score measures whether recognizable skills, education, experience, projects, and certification sections are present; it is not an employment assessment.
3. Browse jobs, search by title/company and location, then apply. Duplicate applications are prevented by the database.
4. Follow recruiter status changes in My Applications and see scheduled interviews in Interviews.
5. Use Career Guidance with a target role to compare saved resume skills with requirements in open job listings.
6. Use Mock Interview for offline rule-based practice. Scores reflect keyword coverage and should be treated as practice feedback.

## Recruiter workflow

1. Register with the Recruiter portal selected. Company name initially uses the account name and can be edited in Company Profile.
2. Post a job; it becomes visible to applicants. Edit or close it from Manage Jobs.
3. Review applications in Applications or Candidate Screening. Candidate profile shows the score breakdown, detected skills, and resume information. Match scores never automatically reject candidates.
4. Update an application status or schedule an interview. Applicants see those updates in their portal.
5. View scheduled interview details and update status/notes. Analytics shows the application status funnel.

## Database and local files

The app creates `hiresphere.db` beside `main.py` on first run. It stores users, applicant profiles, companies, resumes, jobs, applications, saved jobs, interviews, and interview practice results. Keep this file to retain local data. The app includes a small schema migration for the interview status column. No existing database is seeded or overwritten at startup.

PDF extraction reads selectable text only. Scanned image PDFs require OCR outside this app; the app reports when no selectable text is available.

## Tests

Run the isolated backend workflow and extraction checks with:

```bash
python -m unittest discover -s tests -v
```

Tests use temporary SQLite databases and do not modify the app database.

## Troubleshooting

- **Tk cannot find `init.tcl`:** repair or reinstall Python with Tcl/Tk support, then rerun `python main.py`.
- **CustomTkinter or Matplotlib import errors:** activate the project environment and rerun `python -m pip install -r requirements.txt`.
- **Resume reports no text:** the PDF may be a scan or image-only file. Use a text-based PDF.
- **Application already exists:** each applicant can apply once to a given opening.

## GitHub collaboration

Initialize or clone the repository before editing, commit focused changes with descriptive messages, and open a pull request for review. Do not commit `.venv/`, `.env`, Python cache files, or `*.db`; `.gitignore` excludes them. Keep the SQLite database backed up locally if its records matter. Do not push credentials or applicant data.

## Team

Add project contributors here before submission:

- Name: ____________________ | Role: ____________________
- Name: ____________________ | Role: ____________________
- Name: ____________________ | Role: ____________________
