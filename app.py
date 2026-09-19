import re
import streamlit as st

st.set_page_config(page_title="AI Resume Reviewer", page_icon="📄", layout="wide")

ROLE_SKILLS = {
    "Data Scientist": ["python","sql","machine learning","pandas","numpy","scikit-learn","statistics","power bi","tableau"],
    "Software Developer": ["python","java","c++","javascript","html","css","git","sql","api","react"],
    "Electrical Engineer": ["matlab","simulink","plc","scada","autocad","power systems","power electronics","ev","solar","python"],
    "AI/ML Engineer": ["python","machine learning","deep learning","tensorflow","pytorch","nlp","pandas","numpy","scikit-learn","sql"],
}
SECTIONS = {
    "Contact information": r"(email|e-mail|phone|\+?\d[\d\s-]{8,})",
    "Education": r"\b(education|academic|degree|b\.?e\.?|b\.?tech|bachelor|university|college)\b",
    "Skills": r"\b(skills|technical skills|technologies|competencies)\b",
    "Projects": r"\b(projects|project experience)\b",
    "Experience": r"\b(experience|work experience|employment|internship)\b",
    "Certifications": r"\b(certifications?|certificates?)\b",
    "Achievements": r"\b(achievements?|awards?)\b",
}
ACTIONS = ["developed","built","designed","implemented","created","automated","analyzed","optimized","managed","led","improved","tested"]

def review(text, role):
    low = text.lower()
    present = [n for n,p in SECTIONS.items() if re.search(p, text, re.I)]
    skills = []
    for vals in ROLE_SKILLS.values():
        for s in vals:
            if s in low and s not in skills: skills.append(s)
    target = ROLE_SKILLS[role]
    matched = [s for s in target if s in low]
    nums = re.findall(r"\b\d+(?:\.\d+)?%?\b", text)
    actions = [w for w in ACTIONS if re.search(rf"\b{re.escape(w)}\b", low)]
    words = re.findall(r"\b[\w+#.-]+\b", text)
    score = min(100,
        round(len(present)/len(SECTIONS)*40) +
        min(25, round(len(matched)/max(1,len(target))*25)) +
        (15 if len(nums)>=5 else 10 if len(nums)>=2 else 4) +
        (10 if len(actions)>=5 else 6 if len(actions)>=2 else 2) +
        (10 if 300<=len(words)<=900 else 7 if 180<=len(words)<=1100 else 4)
    )
    tips=[]
    missing=[n for n in SECTIONS if n not in present]
    missskills=[s for s in target if s not in low]
    if missing: tips.append("Add relevant missing sections: "+", ".join(missing)+".")
    if missskills: tips.append("Consider relevant "+role+" skills only if you genuinely have them: "+", ".join(missskills[:6])+".")
    if len(nums)<5: tips.append("Add measurable results where truthful: %, time saved, cost, accuracy, scale, users, etc.")
    if len(actions)<5: tips.append("Use strong action verbs such as developed, designed, automated, analyzed, optimized, and implemented.")
    if not tips: tips.append("Structure is solid; tailor keywords and measurable achievements to each job description.")
    return score, len(words), present, skills, matched, missskills, tips

st.title("📄 AI Resume Reviewer")
st.caption("AI-style resume analysis and improvement suggestions")

with st.sidebar:
    role=st.selectbox("Target role", list(ROLE_SKILLS))
    st.info("Portfolio prototype: resume text is analyzed locally; no external AI API is required.")

upload=st.file_uploader("Upload resume (.txt)", type=["txt"])
text=st.text_area("Or paste resume text", height=280)
if upload:
    text=upload.read().decode("utf-8", errors="ignore")

if st.button("🔍 Review Resume", type="primary"):
    if not text.strip():
        st.warning("Upload or paste a resume first.")
    else:
        score, wc, sections, skills, matched, missing_skills, tips=review(text, role)
        a,b,c=st.columns(3)
        a.metric("Overall Score", f"{score}/100")
        b.metric("Word Count", wc)
        c.metric("Role Skills Matched", f"{len(matched)}/{len(ROLE_SKILLS[role])}")
        st.progress(score/100)
        x,y=st.columns(2)
        with x:
            st.subheader("✅ Detected")
            st.write("**Sections:** "+(", ".join(sections) if sections else "None"))
            st.write("**Skills:** "+(", ".join(skills) if skills else "None"))
        with y:
            st.subheader("⚠️ Recommended")
            st.write("**Skills to consider:** "+(", ".join(missing_skills[:8]) if missing_skills else "Good coverage"))
        st.subheader("💡 Improvement Suggestions")
        for tip in tips: st.write("• "+tip)
        st.subheader("📌 Next Step")
        st.write("Tailor the resume to the specific job description and keep every claim truthful.")
