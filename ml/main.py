from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import similarity, ats, taxonomy

app = FastAPI(
    title="RoleFit AI — ML Service",
    description="Embedding-based semantic similarity, ATS scoring, and skill taxonomy normalization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(similarity.router)
app.include_router(ats.router)
app.include_router(taxonomy.router)


@app.get("/")
def root():
    return {"message": "RoleFit ML Service running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
