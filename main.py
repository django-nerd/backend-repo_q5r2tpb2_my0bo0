import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone

from database import create_document
from schemas import ContactInquiry

app = FastAPI(title="Fashion Designer Portfolio API", version="1.0.0")

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL")
backend_url = os.getenv("BACKEND_URL")

allowed_origins: List[str] = [
    origin for origin in [
        frontend_url,
        backend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000",
    ] if origin
]

# Fallback to wildcard if nothing provided (keeps dev smooth)
if not allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "backend",
    }


@app.get("/")
def root():
    return {"message": "Fashion Designer Portfolio Backend", "status": "ok"}


@app.get("/test")
def test_database():
    """Simple DB ping using helper module."""
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        from database import db
        import os as _os
        resp["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
        resp["database_name"] = _os.getenv("DATABASE_NAME") or "❌ Not Set"
        if db is not None:
            try:
                resp["collections"] = db.list_collection_names()[:10]
                resp["database"] = "✅ Connected & Working"
                resp["connection_status"] = "Connected"
            except Exception as e:
                resp["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            resp["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        resp["database"] = f"❌ Error: {str(e)[:80]}"
    return resp


@app.post("/contact")
def submit_contact(inquiry: ContactInquiry):
    try:
        payload = inquiry.model_dump()
        payload["received_at"] = datetime.now(timezone.utc)
        doc_id = create_document("contactinquiry", payload)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save inquiry: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
