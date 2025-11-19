import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Developer, SoftwareApp, Review

app = FastAPI(title="DevShowcase API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "DevShowcase API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Helper to convert ObjectId to str in results
class AppOut(BaseModel):
    id: str
    title: str
    description: str
    platform: str
    category: Optional[str] = None
    tags: List[str] = []
    repo_url: Optional[str] = None
    website_url: Optional[str] = None
    image_url: Optional[str] = None
    version: Optional[str] = None
    license: Optional[str] = None
    author_name: str
    author_email: str
    created_at: Optional[str] = None


@app.post("/api/apps", response_model=dict)
def create_app(app_in: SoftwareApp):
    try:
        inserted_id = create_document("softwareapp", app_in)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/apps", response_model=List[AppOut])
def list_apps(q: Optional[str] = None, platform: Optional[str] = None):
    try:
        filter_q = {}
        if platform:
            filter_q["platform"] = platform
        # Simple text match
        if q:
            filter_q["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
            ]
        docs = get_documents("softwareapp", filter_q or {}, limit=None)
        result = []
        for d in docs:
            d_id = str(d.get("_id"))
            result.append(AppOut(
                id=d_id,
                title=d.get("title"),
                description=d.get("description"),
                platform=d.get("platform"),
                category=d.get("category"),
                tags=d.get("tags", []),
                repo_url=d.get("repo_url"),
                website_url=d.get("website_url"),
                image_url=d.get("image_url"),
                version=d.get("version"),
                license=d.get("license"),
                author_name=d.get("author_name"),
                author_email=d.get("author_email"),
                created_at=str(d.get("created_at")) if d.get("created_at") else None,
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ReviewIn(Review):
    pass


class ReviewOut(BaseModel):
    id: str
    app_id: str
    reviewer_name: str
    rating: int
    pros: Optional[str] = None
    cons: Optional[str] = None
    suggestions: Optional[str] = None
    comment: Optional[str] = None
    created_at: Optional[str] = None


@app.post("/api/apps/{app_id}/reviews", response_model=dict)
def create_review(app_id: str, review: ReviewIn):
    try:
        # Ensure app exists
        app_obj = db["softwareapp"].find_one({"_id": ObjectId(app_id)})
        if not app_obj:
            raise HTTPException(status_code=404, detail="App not found")
        data = review.model_dump()
        data["app_id"] = app_id
        inserted_id = create_document("review", data)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/apps/{app_id}/reviews", response_model=List[ReviewOut])
def list_reviews(app_id: str):
    try:
        docs = get_documents("review", {"app_id": app_id})
        out: List[ReviewOut] = []
        for d in docs:
            out.append(ReviewOut(
                id=str(d.get("_id")),
                app_id=d.get("app_id"),
                reviewer_name=d.get("reviewer_name"),
                rating=d.get("rating"),
                pros=d.get("pros"),
                cons=d.get("cons"),
                suggestions=d.get("suggestions"),
                comment=d.get("comment"),
                created_at=str(d.get("created_at")) if d.get("created_at") else None,
            ))
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
