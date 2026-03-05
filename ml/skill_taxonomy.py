"""
Skill Taxonomy — Canonical skill normalization and alias resolution.

Expanded taxonomy with 150+ skills covering:
  - Programming languages
  - AI/ML frameworks
  - Web frameworks (frontend + backend)
  - Data engineering
  - DevOps & Infrastructure
  - Cloud services
  - Databases
  - Mobile development
  - Soft skills & methodologies
  - Certifications
  - Emerging technologies
"""

SKILL_TAXONOMY = {
    # ── Programming Languages ───────────────────────────────────────────
    "Python": ["python", "py", "python3", "python 3"],
    "JavaScript": ["javascript", "js", "java script", "ecmascript", "es6", "es2015"],
    "TypeScript": ["typescript", "ts", "type script"],
    "Java": ["java", "java ee", "java se", "j2ee"],
    "C++": ["c++", "cpp", "c plus plus"],
    "C#": ["c#", "csharp", "c sharp", ".net c#"],
    "C": ["c language", "ansi c", "c programming"],
    "Go": ["go", "golang", "go lang"],
    "Rust": ["rust", "rust lang", "rustlang"],
    "Kotlin": ["kotlin", "kt"],
    "Swift": ["swift", "swift ui", "swiftlang"],
    "Ruby": ["ruby", "ruby on rails", "rails", "ror"],
    "PHP": ["php", "php8", "laravel php"],
    "Scala": ["scala"],
    "R": ["r", "r language", "r programming", "rstats"],
    "Dart": ["dart", "dart language"],
    "Elixir": ["elixir", "elixir lang"],
    "Lua": ["lua"],
    "Perl": ["perl"],
    "Objective-C": ["objective-c", "objc", "obj-c"],
    "Shell Scripting": ["bash", "shell", "shell scripting", "zsh", "sh"],
    "SQL": ["sql", "structured query language", "t-sql", "plsql", "pl/sql"],

    # ── AI / ML / Data Science ──────────────────────────────────────────
    "Machine Learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "Deep Learning": ["deep learning", "dl", "neural networks", "neural nets"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf", "tf2"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "Hugging Face": ["hugging face", "huggingface", "transformers library"],
    "NLP": ["nlp", "natural language processing", "text processing", "text mining"],
    "Computer Vision": ["computer vision", "cv", "image processing", "image recognition"],
    "LLM": ["llm", "large language models", "gpt", "llms", "large language model"],
    "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "LangChain": ["langchain", "lang chain"],
    "LangGraph": ["langgraph", "lang graph"],
    "Prompt Engineering": ["prompt engineering", "prompt design", "prompt optimization"],
    "MLOps": ["mlops", "ml ops", "machine learning operations"],
    "OpenAI API": ["openai", "openai api", "chatgpt api", "gpt api"],
    "Gemini": ["gemini", "google gemini", "gemini api"],
    "Keras": ["keras"],
    "ONNX": ["onnx"],
    "XGBoost": ["xgboost", "xgb"],
    "LightGBM": ["lightgbm", "lgbm"],
    "Pandas": ["pandas", "pd"],
    "NumPy": ["numpy", "np"],
    "SciPy": ["scipy"],
    "Matplotlib": ["matplotlib", "mpl"],
    "Seaborn": ["seaborn"],
    "Jupyter": ["jupyter", "jupyter notebook", "jupyter lab", "jupyterlab"],
    "Vector Databases": ["vector database", "vector db", "pinecone", "weaviate", "qdrant", "chromadb", "milvus"],
    "Data Visualization": ["data visualization", "data viz", "dashboarding"],
    "Feature Engineering": ["feature engineering", "feature extraction"],

    # ── Web Frameworks (Backend) ────────────────────────────────────────
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django", "django rest framework", "drf"],
    "Flask": ["flask"],
    "Express": ["express", "expressjs", "express.js"],
    "Spring Boot": ["spring boot", "spring", "spring framework", "springboot"],
    "NestJS": ["nestjs", "nest.js", "nest js"],
    "Laravel": ["laravel"],
    "ASP.NET": ["asp.net", "aspnet", ".net core", "dotnet"],
    "Ruby on Rails": ["ruby on rails", "rails", "ror"],
    "Gin": ["gin", "gin-gonic"],
    "Fiber": ["fiber", "gofiber"],

    # ── Web Frameworks (Frontend) ───────────────────────────────────────
    "React": ["react", "reactjs", "react.js", "react js"],
    "Next.js": ["next.js", "nextjs", "next js"],
    "Vue.js": ["vue", "vuejs", "vue.js", "vue3"],
    "Angular": ["angular", "angularjs", "angular.js"],
    "Svelte": ["svelte", "sveltekit"],
    "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
    "Bootstrap": ["bootstrap"],
    "Material UI": ["material ui", "mui", "material design"],
    "Redux": ["redux", "redux toolkit", "rtk"],
    "Streamlit": ["streamlit"],
    "HTML/CSS": ["html", "css", "html5", "css3", "html/css"],

    # ── Databases ───────────────────────────────────────────────────────
    "PostgreSQL": ["postgresql", "postgres", "psql", "pg"],
    "MySQL": ["mysql"],
    "SQLite": ["sqlite", "sqlite3"],
    "MongoDB": ["mongodb", "mongo", "nosql"],
    "Redis": ["redis"],
    "Elasticsearch": ["elasticsearch", "elastic search", "elastic", "opensearch"],
    "Cassandra": ["cassandra", "apache cassandra"],
    "DynamoDB": ["dynamodb", "dynamo db", "aws dynamodb"],
    "Neo4j": ["neo4j", "graph database"],
    "Supabase": ["supabase"],
    "Firebase": ["firebase", "firestore", "firebase realtime"],
    "CockroachDB": ["cockroachdb", "cockroach db"],

    # ── Data Engineering ────────────────────────────────────────────────
    "Spark": ["apache spark", "spark", "pyspark"],
    "Airflow": ["airflow", "apache airflow"],
    "Kafka": ["kafka", "apache kafka", "kafka streams"],
    "dbt": ["dbt", "data build tool"],
    "Snowflake": ["snowflake"],
    "Databricks": ["databricks"],
    "BigQuery": ["bigquery", "google bigquery", "bq"],
    "Redshift": ["redshift", "amazon redshift", "aws redshift"],
    "ETL": ["etl", "elt", "data pipeline", "data pipelines"],
    "Flink": ["flink", "apache flink"],
    "Fivetran": ["fivetran"],
    "Prefect": ["prefect"],
    "Dagster": ["dagster"],
    "Data Warehouse": ["data warehouse", "data warehousing", "dwh"],
    "Data Lake": ["data lake", "data lakehouse", "lakehouse"],

    # ── Cloud Services ──────────────────────────────────────────────────
    "AWS": ["aws", "amazon web services", "amazon aws"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Azure": ["azure", "microsoft azure"],
    "AWS Lambda": ["lambda", "aws lambda", "serverless"],
    "EC2": ["ec2", "aws ec2", "elastic compute"],
    "S3": ["s3", "aws s3", "simple storage service"],
    "CloudFront": ["cloudfront", "aws cloudfront", "cdn"],
    "AWS SageMaker": ["sagemaker", "aws sagemaker"],
    "Azure DevOps": ["azure devops", "ado"],
    "GKE": ["gke", "google kubernetes engine"],
    "EKS": ["eks", "elastic kubernetes service"],
    "Vercel": ["vercel"],
    "Netlify": ["netlify"],
    "Heroku": ["heroku"],
    "Render": ["render"],
    "DigitalOcean": ["digitalocean", "digital ocean"],

    # ── DevOps & Infrastructure ─────────────────────────────────────────
    "Docker": ["docker", "dockerfile", "docker-compose", "docker compose", "containerization"],
    "Kubernetes": ["kubernetes", "k8s", "kubectl"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous deployment", "continuous delivery"],
    "Terraform": ["terraform", "iac", "infrastructure as code"],
    "Git": ["git", "github", "gitlab", "version control"],
    "GitHub Actions": ["github actions", "gh actions"],
    "Jenkins": ["jenkins"],
    "ArgoCD": ["argocd", "argo cd"],
    "Ansible": ["ansible"],
    "Prometheus": ["prometheus"],
    "Grafana": ["grafana"],
    "Nginx": ["nginx"],
    "Linux": ["linux", "ubuntu", "centos", "debian"],
    "Helm": ["helm", "helm charts"],
    "Vault": ["vault", "hashicorp vault"],
    "Istio": ["istio", "service mesh"],
    "Pulumi": ["pulumi"],

    # ── Mobile Development ──────────────────────────────────────────────
    "React Native": ["react native", "reactnative"],
    "Flutter": ["flutter"],
    "SwiftUI": ["swiftui", "swift ui"],
    "Kotlin Android": ["kotlin android", "android kotlin", "jetpack compose"],
    "iOS Development": ["ios", "ios development", "ios dev"],
    "Android Development": ["android", "android development", "android dev"],
    "Expo": ["expo", "expo react native"],

    # ── API & Integration ───────────────────────────────────────────────
    "REST API": ["rest api", "restful api", "rest apis", "restful"],
    "GraphQL": ["graphql", "gql"],
    "gRPC": ["grpc", "g-rpc"],
    "WebSocket": ["websocket", "websockets", "ws"],
    "OAuth": ["oauth", "oauth2", "oauth 2.0"],
    "JWT": ["jwt", "json web token", "json web tokens"],
    "API Design": ["api design", "api architecture"],
    "Microservices": ["microservices", "micro services", "microservice"],
    "Event-Driven Architecture": ["event-driven", "event driven architecture", "eda"],

    # ── Testing & QA ───────────────────────────────────────────────────
    "Unit Testing": ["unit testing", "unit tests"],
    "Jest": ["jest"],
    "Pytest": ["pytest", "py.test"],
    "Playwright": ["playwright"],
    "Cypress": ["cypress"],
    "Selenium": ["selenium"],
    "TDD": ["tdd", "test-driven development", "test driven development"],

    # ── Soft Skills & Methodologies ─────────────────────────────────────
    "Agile": ["agile", "scrum", "kanban", "sprint planning"],
    "Leadership": ["leadership", "team leadership", "technical leadership", "tech lead"],
    "Communication": ["communication", "communication skills", "stakeholder communication"],
    "Problem Solving": ["problem solving", "analytical thinking", "critical thinking"],
    "Project Management": ["project management", "project planning", "program management"],
    "Mentoring": ["mentoring", "coaching", "mentorship"],
    "Cross-Functional": ["cross-functional", "cross functional", "collaboration"],
    "Technical Writing": ["technical writing", "documentation", "tech writing"],

    # ── Certifications ──────────────────────────────────────────────────
    "AWS SAA": ["aws solutions architect", "aws saa", "aws certified solutions architect"],
    "AWS Developer": ["aws certified developer", "aws developer associate"],
    "CKA": ["cka", "certified kubernetes administrator"],
    "CKAD": ["ckad", "certified kubernetes application developer"],
    "PMP": ["pmp", "project management professional"],
    "Scrum Master": ["scrum master", "csm", "certified scrum master", "psm"],
    "Google Cloud Certified": ["google cloud certified", "gcp certified", "google cloud professional"],
    "Azure Certified": ["azure certified", "az-900", "az-104", "az-204"],
    "CompTIA Security+": ["security+", "comptia security", "comptia security+"],

    # ── Emerging Technologies ───────────────────────────────────────────
    "GenAI": ["genai", "generative ai", "generative artificial intelligence"],
    "Agents": ["ai agents", "autonomous agents", "agentic ai"],
    "CrewAI": ["crewai", "crew ai"],
    "Blockchain": ["blockchain", "web3", "smart contracts", "solidity"],
    "Edge Computing": ["edge computing", "edge ai"],
    "IoT": ["iot", "internet of things"],
    "AR/VR": ["ar", "vr", "augmented reality", "virtual reality", "mixed reality", "xr"],
}

# ── Build reverse lookup ────────────────────────────────────────────────

_alias_to_canonical: dict[str, str] = {}
for canonical, aliases in SKILL_TAXONOMY.items():
    for alias in aliases:
        _alias_to_canonical[alias.lower()] = canonical
    _alias_to_canonical[canonical.lower()] = canonical


def normalize_skill(skill: str) -> str:
    """Normalize a skill string to its canonical name."""
    return _alias_to_canonical.get(skill.strip().lower(), skill.strip())


def normalize_skills(skills: list[str]) -> list[str]:
    """Normalize and deduplicate a list of skills."""
    seen = set()
    result = []
    for s in skills:
        norm = normalize_skill(s)
        if norm.lower() not in seen:
            seen.add(norm.lower())
            result.append(norm)
    return result


def find_skill_overlap(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """Find overlap between resume skills and JD skills using normalized names."""
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


def get_taxonomy_stats() -> dict:
    """Return stats about the current taxonomy."""
    total_aliases = sum(len(aliases) for aliases in SKILL_TAXONOMY.items())
    return {
        "total_skills": len(SKILL_TAXONOMY),
        "total_aliases": total_aliases,
        "categories": {
            "programming_languages": sum(1 for k in SKILL_TAXONOMY if k in [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C",
                "Go", "Rust", "Kotlin", "Swift", "Ruby", "PHP", "Scala", "R",
                "Dart", "Elixir", "Lua", "Perl", "Objective-C", "Shell Scripting", "SQL",
            ]),
            "ai_ml": sum(1 for k in SKILL_TAXONOMY if any(
                w in k.lower() for w in ["ml", "learning", "ai", "nlp", "vision", "llm", "rag", "lang", "prompt", "openai", "gemini", "torch", "tensor", "scikit", "hugging", "keras", "onnx", "xgboost", "lightgbm", "pandas", "numpy", "scipy", "matplotlib", "seaborn", "jupyter", "vector", "visualization", "feature"]
            )),
        },
    }
