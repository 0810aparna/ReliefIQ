from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import districts, prediction, optimization

app = FastAPI(title="ReliefIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; tighten before real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(districts.router)
app.include_router(prediction.router)
app.include_router(optimization.router)


@app.get("/health")
def health():
    return {"status": "ok"}