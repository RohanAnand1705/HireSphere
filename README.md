# HireSphere AI 🚀
### Intelligent Recruitment & Career Development Platform

HireSphere AI is a Python-based desktop application designed to connect job seekers and recruiters through intelligent recruitment tools, resume analysis, candidate matching and career development features.

The application provides two separate portals: an Applicant Portal and a Recruiter Portal.

Built using Python Tkinter (CustomTkinter), SQLite and AI integration capabilities, HireSphere AI aims to simplify recruitment and improve the job-search experience.

---

## 📌 Table of Contents

1. Project Overview
2. Features
3. Technology Stack
4. Project Architecture
5. System Requirements
6. Installation and Setup
7. Running the Application
8. User Guide
9. AI Features
10. Database Structure
11. Environment Configuration
12. Troubleshooting
13. GitHub Collaboration
14. Future Improvements
15. Team Members

---

## 1. Project Overview

Traditional recruitment processes often involve manually reviewing resumes, comparing candidate skills and managing applications.

HireSphere AI aims to simplify these processes through a centralized recruitment platform.

### Applicant Portal
Students and job seekers can:
- Create accounts and manage profiles.
- Upload and analyze resumes.
- Browse available job openings.
- Apply for jobs.
- Track application progress.
- Practice AI-powered mock interviews.
- Receive career guidance and skill recommendations.

### Recruiter Portal
Companies and recruiters can:
- Create recruiter accounts.
- Post and manage job openings.
- View candidate applications.
- Analyze candidate resumes.
- Compare candidate skills with job requirements.
- Shortlist candidates.
- Manage application statuses.
- Organize recruitment activities.

---

## 2. Features

### Authentication
- Applicant and recruiter registration.
- Secure password hashing.
- Role-based login.
- Separate dashboards.
- Logout functionality.

### Resume Analyzer
- Upload PDF resumes.
- Extract text using PyMuPDF.
- Identify skills, education, projects and experience.
- Display extracted resume information.
- Provide resume improvement suggestions.

### Job Management
- Create and publish job openings.
- Browse available jobs.
- Search and filter job listings.
- View job descriptions and requirements.
- Apply for available positions.

### AI Resume Matching
Compare applicant resumes with job requirements.

The initial matching system uses a weighted scoring algorithm:

| Parameter | Weight |
|---|---:|
| Skills Match | 40% |
| Project Relevance | 25% |
| Experience | 15% |
| Education Relevance | 10% |
| Certifications | 10% |

The system displays matching skills, missing skills and an overall match score.

Matching scores are intended to assist recruiters and should not replace human evaluation.

### Application Tracking
Applicants can track their applications through different stages:

- Applied
- Under Review
- Shortlisted
- Interview
- Selected
- Rejected

Recruiters can update application statuses.

### AI Mock Interview
- Select a job role.
- Practice interview questions.
- Submit answers.
- Receive feedback when AI evaluation is configured.
- Review interview performance.

### Career Guidance
- Review existing skills.
- Identify skill gaps.
- Explore recommended skills.
- Receive career improvement suggestions.
- Prepare for target job roles.

### Recruiter Dashboard
- View recruitment statistics.
- Manage job openings.
- Review candidate applications.
- Shortlist candidates.
- Monitor recruitment activities.

---

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core programming language |
| CustomTkinter | Desktop GUI |
| SQLite3 | Database management |
| PyMuPDF | PDF resume extraction |
| Pillow | Image processing |
| Matplotlib | Data visualization |
| Google Gemini API | Optional AI-powered features |
| python-dotenv | Environment variable management |
| bcrypt | Password hashing |

---

## 4. Project Architecture

```text
HireSphere/
│
├── README.md
│
└── hiresphere_desktop/
    │
    ├── main.py
    ├── database.py
    ├── requirements.txt
    ├── .env.example
    ├── README.md
    │
    ├── assets/
    │
    ├── ui/
    │   ├── login.py
    │   ├── register.py
    │   ├── applicant_dashboard.py
    │   ├── recruiter_dashboard.py
    │   ├── job_portal.py
    │   ├── resume_analyzer.py
    │   ├── applications.py
    │   ├── candidate_screening.py
    │   ├── interview.py
    │   ├── career_guidance.py
    │   └── profile.py
    │
    ├── services/
    │   ├── auth_service.py
    │   ├── resume_parser.py
    │   ├── job_service.py
    │   ├── matching_engine.py
    │   └── application_service.py
    │
    ├── models/
    │
    └── utils/
```

The architecture separates GUI components, business logic, database operations and supporting utilities to make the application easier to maintain and extend.

---

## 5. System Requirements

Before installing the application, ensure that you have:

- Windows 10/11, Linux or macOS.
- Python 3.11 or later.
- pip package manager.
- Git.
- Visual Studio Code (recommended).
- Internet connection for installing dependencies and using online AI services.

**Note:** Tkinter requires a working Tcl/Tk installation. On Windows, the standard Python installer normally includes it.

Verify your Python installation:

```bash
python --version
```

Verify pip:

```bash
pip --version
```

Check Tkinter availability:

```bash
python -m tkinter
```

A small test window should appear if Tkinter is installed correctly.

---

## 6. Installation and Setup

### Step 1: Clone the repository

Open your terminal and execute:

```bash
git clone https://github.com/RohanAnand1705/HireSphere.git
```

### Step 2: Navigate to the project

```bash
cd HireSphere/hiresphere_desktop
```

### Step 3: Create a virtual environment

```bash
python -m venv venv
```

### Step 4: Activate the virtual environment

**Windows PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### Step 5: Install dependencies

```bash
python -m pip install --upgrade pip
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### Step 6: Configure environment variables

Copy `.env.example` to a new file named `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Add the required configuration values if you intend to use Gemini-powered features.

Never upload your actual `.env` file or API keys to GitHub.

---

## 7. Running the Application

After completing the installation:

Navigate to the desktop project directory:

```bash
cd HireSphere/hiresphere_desktop
```

Activate the virtual environment if it is not already active.

Start the application:

```bash
python main.py
```

The HireSphere AI desktop application should launch.

The database is initialized by the application according to its database configuration.

---

## 8. User Guide

### Applicant Workflow

1. Launch HireSphere AI.
2. Select the Applicant account type.
3. Register or log in.
4. Complete your applicant profile.
5. Upload a PDF resume.
6. Review extracted resume information.
7. Browse available job openings.
8. Select a suitable job.
9. Submit an application.
10. Track application status through your dashboard.
11. Explore mock interviews and career guidance.

### Recruiter Workflow

1. Launch HireSphere AI.
2. Select the Recruiter account type.
3. Register or log in.
4. Complete company information.
5. Create a job opening.
6. Add job requirements and required skills.
7. Publish the job.
8. Review incoming applications.
9. Analyze candidate resumes and matching scores.
10. Shortlist suitable candidates.
11. Update application statuses and manage interviews.

### Important Workflow

The Applicant and Recruiter portals share the same database.

For example:

- A recruiter creates a Python Developer job.
- The job becomes visible in the Applicant Portal.
- An applicant submits an application.
- The application becomes visible in the Recruiter Portal.
- The recruiter updates the application status.
- The applicant can view the updated status.

---

## 9. AI Features

HireSphere AI uses a combination of resume processing, rule-based matching and optional generative AI integration.

### Resume Parsing

PyMuPDF extracts text from uploaded PDF resumes.

The extracted content is processed to identify relevant information.

### Resume Matching

The initial matching engine compares candidate information with job requirements using a weighted scoring system.

### AI Mock Interview

Google Gemini API can be configured for generating interview questions and evaluating candidate responses.

AI functionality requires a valid API key and successful dependency installation.

If the API is unavailable, the application may provide limited predefined or demo interview functionality, depending on the implemented configuration.

**Important:** Rule-based resume matching and generative AI evaluation are different components. A weighted matching score does not represent a trained machine learning model.

---

## 10. Database Structure

HireSphere AI uses SQLite for persistent local data storage.

The database manages information such as:

| Table | Purpose |
|---|---|
| Users | Applicant and recruiter accounts |
| ApplicantProfiles | Applicant information |
| Companies | Company information |
| Resumes | Uploaded resume details |
| Jobs | Job listings |
| Applications | Job applications |
| SavedJobs | Saved job listings |
| Interviews | Interview information |
| InterviewResults | Interview evaluations |

The database is initialized through the application's database module.

The actual database filename and location are determined by the database configuration.

Do not delete the database if you want to preserve existing application records.

---

## 11. Environment Configuration

Gemini-powered functionality requires an API key.

To configure it:

1. Obtain an API key from Google AI Studio.
2. Create a `.env` file in the location expected by the application.
3. Add the variable names specified in `.env.example`.
4. Restart the application.

Google AI Studio:

https://aistudio.google.com/

Never commit API keys, passwords or other sensitive credentials to GitHub.

---

## 12. Troubleshooting

### Error: No module named 'customtkinter'

Install dependencies:

```bash
pip install -r requirements.txt
```

### Error: Could not open requirements.txt

Ensure that your terminal is inside the `hiresphere_desktop` directory.

```bash
cd hiresphere_desktop
```

### Error: Tcl/Tk runtime missing

Verify Tkinter:

```bash
python -m tkinter
```

If the test fails, repair or reinstall Python with Tcl/Tk support enabled.

### Error: Database or SQLite issues

Check that the application has permission to write to its database directory.

Do not delete an existing database without backing it up.

### Gemini API not working

Check:

- Whether the API key is configured.
- Whether the environment variable name matches `.env.example`.
- Whether the required Gemini package is installed.
- Whether the API key is valid.
- Whether the API service is available.

### Git changes not appearing on GitHub

Check:

```bash
git status
```

Then:

```bash
git add .
git commit -m "Update HireSphere AI"
git push origin main
```

---

## 13. GitHub Collaboration

Repository:

https://github.com/RohanAnand1705/HireSphere

To contribute:

### Clone the repository

```bash
git clone https://github.com/RohanAnand1705/HireSphere.git
```

### Pull the latest changes

Before starting work:

```bash
git pull origin main
```

### Check modified files

```bash
git status
```

### Add changes

```bash
git add .
```

### Commit changes

```bash
git commit -m "Describe your changes"
```

### Push changes

```bash
git push origin main
```

**Collaboration guidelines:**

- Pull the latest changes before starting work.
- Avoid editing the same files simultaneously.
- Use meaningful commit messages.
- Test changes before pushing.
- Never commit `.env`, virtual environments or personal database files.
- Use separate Git branches for larger features where appropriate.

---

## 14. Future Improvements

Potential future enhancements include:

- Advanced semantic resume matching using NLP.
- Voice-based AI mock interviews.
- Automated interview scheduling.
- Advanced recruitment analytics.
- Email notifications.
- More detailed candidate skill analysis.
- Improved resume recommendations.
- Cloud database integration.
- Role-based administrative controls.

---

## 15. Team Members

**Project:** HireSphere AI – Intelligent Recruitment & Career Development Platform

**Department:** Computer Science and Engineering

**Project Type:** Python Tkinter Mini-Project

**Team Members:**

1. [Member 1 Name]
2. [Member 2 Name]
3. [Member 3 Name]

---

## License

This project is developed as an academic mini-project.

All rights reserved by the project team unless otherwise specified.

---

**HireSphere AI – Your Career. Smarter Connections.**
