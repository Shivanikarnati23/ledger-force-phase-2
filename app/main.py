from fastapi import FastAPI
from app.routers import employees

app = FastAPI(title="Ledger Force API")

# Include the employee and team management router
app.include_router(employees.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Ledger Force API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}