"""PDF text extraction and conservative resume section identification."""
import re
from pathlib import Path

SKILLS = {"python","java","javascript","typescript","sql","sqlite","react","node","django","flask","fastapi","machine learning","deep learning","data analysis","aws","azure","docker","git","html","css","c++","communication","leadership","excel","power bi","tensorflow","pytorch"}

def parse_pdf(path):
    import pymupdf
    doc = pymupdf.open(path)
    text = "\n".join(page.get_text() for page in doc).strip()
    if not text:
        raise ValueError("No selectable text found in this PDF. Scanned PDFs need OCR before they can be analyzed.")
    lower = text.lower()
    found = sorted(skill for skill in SKILLS if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", lower))
    def section(*heads):
        lines = text.splitlines()
        start = next((i for i,line in enumerate(lines) if any(h in line.lower() for h in heads)), None)
        if start is None: return ""
        out=[]
        for line in lines[start+1:]:
            if re.search(r"^(education|experience|projects|skills|certifications|work history)\s*:?$", line.strip(), re.I): break
            if line.strip(): out.append(line.strip())
        return " ".join(out[:12])
    edu=section("education"); exp=section("experience", "work history"); projects=section("projects"); cert=section("certifications")
    completeness = round(100 * sum(bool(x) for x in (found,edu,exp,projects,cert))/5)
    return {"text":text,"skills":", ".join(found),"education":edu,"experience":exp,"projects":projects,"certifications":cert,"score":completeness,"filename":Path(path).name}
