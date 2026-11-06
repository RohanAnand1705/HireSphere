import tempfile
import unittest
from pathlib import Path

import database
from database import connect
from services import application_service, auth_service, job_service, interview_service
from services.matching_engine import score_resume
from main import HireSphere


class HireSphereWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_db = database.DB_PATH
        database.DB_PATH = Path(self.temp.name) / "test.db"
        database.init_db()
        self.applicant = auth_service.register("Test Applicant", "applicant@example.test", "secure-pass-123", "applicant")
        self.recruiter = auth_service.register("Test Company", "recruiter@example.test", "secure-pass-123", "recruiter")

    def tearDown(self):
        database.DB_PATH = self.original_db
        self.temp.cleanup()

    def test_end_to_end_hiring_workflow_and_persistence(self):
        self.assertEqual(auth_service.login("applicant@example.test", "secure-pass-123", "applicant")["id"], self.applicant["id"])
        self.assertEqual(auth_service.login("recruiter@example.test", "secure-pass-123", "recruiter")["id"], self.recruiter["id"])
        with self.assertRaises(ValueError):
            auth_service.login("applicant@example.test", "secure-pass-123", "recruiter")
        with connect() as c:
            stored_hash=c.execute('SELECT password_hash FROM Users WHERE id=?',(self.applicant['id'],)).fetchone()[0]
        self.assertNotEqual(stored_hash,b"secure-pass-123")
        job_service.create_job(self.recruiter["id"], {"title":"Python Analyst", "description":"Analyze data", "required_skills":"Python, SQL", "location":"Remote"})
        job = job_service.jobs("Python", "Remote")[0]
        job_service.create_job(self.recruiter["id"], {"title":"Python Analyst II", "description":"Analyze and report data", "required_skills":"Python, SQL", "location":"Remote"}, job["id"])
        job = job_service.jobs("Python Analyst II", "Remote")[0]
        match = application_service.apply(self.applicant["id"], job["id"])
        self.assertGreaterEqual(match["score"], 0)
        with self.assertRaises(Exception):
            application_service.apply(self.applicant["id"], job["id"])
        with connect() as c:
            app = c.execute("SELECT id,status FROM Applications WHERE job_id=?", (job["id"],)).fetchone()
            self.assertEqual(app["status"], "Applied")
            c.execute("UPDATE Applications SET status='Shortlisted' WHERE id=?", (app["id"],))
            c.execute("INSERT INTO Interviews(application_id,scheduled_at,notes) VALUES(?,?,?)", (app["id"], "2027-01-15 10:30", "Video call"))
            c.execute("UPDATE Interviews SET status='Completed',notes=? WHERE application_id=?",('Interview held',app['id']))
        with connect() as c:
            self.assertEqual(c.execute("SELECT status FROM Applications WHERE id=?", (app["id"],)).fetchone()[0], "Shortlisted")
            interview = c.execute("SELECT scheduled_at,notes,status FROM Interviews WHERE application_id=?", (app["id"],)).fetchone()
            self.assertEqual(tuple(interview), ("2027-01-15 10:30", "Interview held", "Completed"))
            self.assertEqual(c.execute('SELECT status FROM Applications WHERE applicant_id=? AND job_id=?',(self.applicant['id'],job['id'])).fetchone()[0],'Shortlisted')

    def test_interview_status_schema_migration_preserves_existing_rows(self):
        regular_db=database.DB_PATH
        database.DB_PATH=Path(self.temp.name)/'legacy.db'
        with connect() as c:
            c.execute('CREATE TABLE Interviews(id INTEGER PRIMARY KEY, application_id INTEGER, scheduled_at TEXT NOT NULL, interview_type TEXT DEFAULT \'Interview\', notes TEXT DEFAULT \'\', created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
            c.execute("INSERT INTO Interviews(application_id,scheduled_at,notes) VALUES(1,'2027-02-01 09:00','Keep this')")
        database.init_db()
        with connect() as c:
            row=c.execute('SELECT scheduled_at,notes,status FROM Interviews').fetchone()
        database.DB_PATH=regular_db
        self.assertEqual(tuple(row),('2027-02-01 09:00','Keep this','Scheduled'))

    def test_matching_weights_and_explanation(self):
        result = score_resume({"skills":"Python SQL", "projects":"Python reporting project", "experience":"2 years", "education":"BSc", "certifications":""}, {"title":"Data Analyst", "required_skills":"Python SQL Tableau"})
        self.assertEqual(result["matching"], ["python", "sql"])
        self.assertEqual(result["missing"], ["tableau"])
        self.assertEqual(result["breakdown"]["skills"], 27)
        self.assertIn("40%", result["explanation"])

    def test_offline_interview_evaluation(self):
        questions = interview_service.question_bank("Data Analyst", "Technical", "Beginner")
        result = interview_service.evaluate_answer(questions[0], "I explain query plan, add an index, measure and filter carefully.")
        self.assertGreater(result["score"], 0)
        self.assertIn("score", result)
        self.assertIn("Covers", result["feedback"])

    def test_pdf_extraction(self):
        import pymupdf
        from services.resume_parser import parse_pdf
        path = Path(self.temp.name) / "resume.pdf"
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 72), "\n".join(["Skills", "Python, SQL", "Education", "BSc Computer Science", "Experience", "Analyst", "Projects", "Python dashboard"]))
        doc.save(path)
        doc.close()
        result = parse_pdf(path)
        self.assertIn("python", result["skills"].lower())
        self.assertTrue(result["education"])
        self.assertTrue(result["projects"])

    def test_sidebar_routes_resolve_to_handlers(self):
        applicant_routes=['dashboard','find_jobs','saved_jobs','my_applications','resume_analyzer','mock_interview','career_guidance','my_profile','settings']
        recruiter_routes=['dashboard','post_a_job','manage_jobs','applications','candidate_screening','shortlisted_candidates','interviews','analytics','company_profile','settings']
        for route in set(applicant_routes+recruiter_routes):
            self.assertTrue(callable(getattr(HireSphere,'page_'+route,None)),route)


if __name__ == "__main__":
    unittest.main()
