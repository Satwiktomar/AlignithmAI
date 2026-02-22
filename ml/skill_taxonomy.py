SKILL_TAXONOMY = {
    "Python": ["python", "py", "python3", "python 3"],
    "JavaScript": ["javascript", "js", "java script", "ecmascript", "es6", "es2015"],
    "TypeScript": ["typescript", "ts", "type script"],
    "Java": ["java", "java ee", "java se"],
    "C++": ["c++", "cpp", "c plus plus"],
    "C#": ["c#", "csharp", "c sharp", ".net c#"],
    "Go": ["go", "golang", "go lang"],
    "Rust": ["rust", "rust lang"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],
    "Ruby": ["ruby", "ruby on rails", "rails"],
    "PHP": ["php"],
    "Scala": ["scala"],
    "R": ["r", "r language", "r programming"],
    "Machine Learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "Deep Learning": ["deep learning", "dl", "neural networks", "neural nets"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "Hugging Face": ["hugging face", "huggingface", "transformers library"],
    "NLP": ["nlp", "natural language processing", "text processing"],
    "Computer Vision": ["computer vision", "cv", "image processing"],
    "LLM": ["llm", "large language models", "gpt", "llms"],
    "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "LangChain": ["langchain", "lang chain"],
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"],
    "Flask": ["flask"],
    "React": ["react", "reactjs", "react.js", "react js"],
    "Next.js": ["next.js", "nextjs", "next js"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Express": ["express", "expressjs", "express.js"],
    "Vue.js": ["vue", "vuejs", "vue.js"],
    "Streamlit": ["streamlit"],
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "SQLite": ["sqlite"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    "Cassandra": ["cassandra", "apache cassandra"],
    "AWS": ["aws", "amazon web services", "amazon aws"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Azure": ["azure", "microsoft azure"],
    "Docker": ["docker", "dockerfile", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "Terraform": ["terraform"],
    "Git": ["git", "github", "gitlab"],
    "SQL": ["sql", "structured query language"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Spark": ["apache spark", "spark", "pyspark"],
    "Airflow": ["airflow", "apache airflow"],
    "REST API": ["rest api", "restful api", "rest apis", "restful"],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "micro services", "microservice"],
    "Agile": ["agile", "scrum", "kanban"],
}

_alias_to_canonical: dict[str, str] = {}
for canonical, aliases in SKILL_TAXONOMY.items():
    for alias in aliases:
        _alias_to_canonical[alias.lower()] = canonical
    _alias_to_canonical[canonical.lower()] = canonical


def normalize_skill(skill: str) -> str:
    return _alias_to_canonical.get(skill.strip().lower(), skill.strip())


def normalize_skills(skills: list[str]) -> list[str]:
    seen = set()
    result = []
    for s in skills:
        norm = normalize_skill(s)
        if norm.lower() not in seen:
            seen.add(norm.lower())
            result.append(norm)
    return result


def find_skill_overlap(resume_skills: list[str], jd_skills: list[str]) -> dict:
    norm_resume = {normalize_skill(s).lower() for s in resume_skills}
    norm_jd = {normalize_skill(s).lower() for s in jd_skills}

    matched_norm = norm_resume & norm_jd
    missing_norm = norm_jd - norm_resume

    matched_display = [s for s in jd_skills if normalize_skill(s).lower() in matched_norm]
    missing_display = [s for s in jd_skills if normalize_skill(s).lower() in missing_norm]

    coverage = (len(matched_norm) / len(norm_jd) * 100) if norm_jd else 0

    return {
        "matched": matched_display,
        "missing": missing_display,
        "coverage_pct": round(coverage, 1),
        "matched_count": len(matched_norm),
        "total_jd_skills": len(norm_jd),
    }
