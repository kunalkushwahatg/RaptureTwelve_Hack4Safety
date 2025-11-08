"""
FastAPI Application for Missing Persons and Unidentified Bodies System
Provides REST API endpoints for reporting and searching
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
import json
import os
import shutil
from datetime import datetime
import uuid
from pathlib import Path

# Import our modules
from db_helper import DatabaseHelper
from text_embedder import TextEmbedder
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import numpy as np

# Try to import face recognition (optional if not installed)
try:
    from face_embedding import FaceEmbeddingExtractor
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠ Face recognition not available. Install: pip install opencv-python insightface onnxruntime")

from vector_retrieval import VectorRetrieval

# Initialize FastAPI app
app = FastAPI(
    title="Missing Persons & Unidentified Bodies API",
    description="API for reporting unidentified bodies and searching for missing persons",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DB_FILE = 'missing_persons.db'
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
PHOTO_BASE_DIR = "photos"
UIDB_PHOTO_DIR = os.path.join(PHOTO_BASE_DIR, "unidentified_bodies")
MISSING_PHOTO_DIR = os.path.join(PHOTO_BASE_DIR, "missing_persons")

# Initialize services
db_helper = DatabaseHelper()
text_embedder = TextEmbedder()
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
vector_retrieval = VectorRetrieval(host=QDRANT_HOST, port=QDRANT_PORT)

if FACE_RECOGNITION_AVAILABLE:
    face_extractor = FaceEmbeddingExtractor(use_gpu=False)

# Ensure photo directories exist
os.makedirs(UIDB_PHOTO_DIR, exist_ok=True)
os.makedirs(MISSING_PHOTO_DIR, exist_ok=True)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UnidentifiedBodyReport(BaseModel):
    """Model for unidentified body report"""
    police_station: str
    found_date: str
    postmortem_date: Optional[str] = None
    estimated_age: Optional[int] = None
    gender: str
    height_cm: Optional[int] = None
    build: Optional[str] = None
    complexion: Optional[str] = None
    face_shape: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinguishing_marks: Optional[str] = None
    distinctive_features: Optional[str] = None
    clothing_description: Optional[str] = None
    jewelry_description: Optional[str] = None
    person_description: Optional[str] = None
    found_latitude: Optional[float] = None
    found_longitude: Optional[float] = None
    found_address: Optional[str] = None
    cause_of_death: Optional[str] = None
    estimated_death_time: Optional[str] = None
    dna_sample_collected: bool = False
    dental_records_available: bool = False
    fingerprints_collected: bool = False


class SearchRequest(BaseModel):
    """Model for missing person search request"""
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[int] = None
    build: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinguishing_marks: Optional[str] = None
    last_seen_clothing: Optional[str] = None
    person_description: Optional[str] = None
    search_text: Optional[str] = None  # Custom search text
    top_n: int = Field(default=10, le=50)
    face_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    text_weight: float = Field(default=0.4, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Model for search result"""
    pid: str
    combined_score: float
    face_score: float
    text_score: float
    details: dict


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Save uploaded file to destination"""
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return destination
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def generate_text_description(data: dict) -> str:
    """Generate textual description for embedding"""
    parts = []
    
    if data.get('gender'):
        parts.append(data['gender'])
    if data.get('estimated_age') or data.get('age'):
        age = data.get('estimated_age') or data.get('age')
        parts.append(f"{age} years old")
    if data.get('height_cm'):
        parts.append(f"{data['height_cm']}cm tall")
    if data.get('build'):
        parts.append(f"{data['build']} build")
    if data.get('complexion'):
        parts.append(f"{data['complexion']} complexion")
    if data.get('face_shape'):
        parts.append(f"{data['face_shape']} face")
    if data.get('hair_color'):
        parts.append(f"{data['hair_color']} hair")
    if data.get('eye_color'):
        parts.append(f"{data['eye_color']} eyes")
    if data.get('distinguishing_marks'):
        parts.append(f"Marks: {data['distinguishing_marks']}")
    if data.get('distinctive_features'):
        parts.append(f"{data['distinctive_features']}")
    if data.get('clothing_description') or data.get('last_seen_clothing'):
        clothing = data.get('clothing_description') or data.get('last_seen_clothing')
        parts.append(f"Clothing: {clothing}")
    if data.get('found_address') or data.get('last_seen_address'):
        location = data.get('found_address') or data.get('last_seen_address')
        parts.append(f"Location: {location}")
    if data.get('person_description'):
        parts.append(data['person_description'])
    
    description = ". ".join(parts[:15]) + "."
    return description


def get_record_details(pid: str) -> dict:
    """Get full record details from database by PID"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Try unidentified_bodies table
    cursor.execute("SELECT * FROM unidentified_bodies WHERE pid = ?", (pid,))
    row = cursor.fetchone()
    
    if row:
        record = dict(row)
        record['record_type'] = 'unidentified_body'
    else:
        # Try missing_persons table
        cursor.execute("SELECT * FROM missing_persons WHERE pid = ?", (pid,))
        row = cursor.fetchone()
        if row:
            record = dict(row)
            record['record_type'] = 'missing_person'
        else:
            record = None
    
    conn.close()
    return record


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Missing Persons & Unidentified Bodies API",
        "version": "1.0.0",
        "endpoints": {
            "report_unidentified_body": "/api/report-unidentified-body",
            "search_missing_person": "/api/search-missing-person",
            "get_record": "/api/record/{pid}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        conn = sqlite3.connect(DB_FILE)
        conn.close()
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    try:
        # Check Qdrant
        collections = qdrant_client.get_collections()
        qdrant_status = "healthy"
    except:
        qdrant_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" and qdrant_status == "healthy" else "degraded",
        "database": db_status,
        "vector_db": qdrant_status,
        "face_recognition": "available" if FACE_RECOGNITION_AVAILABLE else "unavailable"
    }


@app.post("/api/report-unidentified-body")
async def report_unidentified_body(
    police_station: str = Form(...),
    found_date: str = Form(...),
    gender: str = Form(...),
    postmortem_date: Optional[str] = Form(None),
    estimated_age: Optional[int] = Form(None),
    height_cm: Optional[int] = Form(None),
    build: Optional[str] = Form(None),
    complexion: Optional[str] = Form(None),
    face_shape: Optional[str] = Form(None),
    hair_color: Optional[str] = Form(None),
    eye_color: Optional[str] = Form(None),
    distinguishing_marks: Optional[str] = Form(None),
    distinctive_features: Optional[str] = Form(None),
    clothing_description: Optional[str] = Form(None),
    jewelry_description: Optional[str] = Form(None),
    person_description: Optional[str] = Form(None),
    found_latitude: Optional[float] = Form(None),
    found_longitude: Optional[float] = Form(None),
    found_address: Optional[str] = Form(None),
    cause_of_death: Optional[str] = Form(None),
    estimated_death_time: Optional[str] = Form(None),
    dna_sample_collected: bool = Form(False),
    dental_records_available: bool = Form(False),
    fingerprints_collected: bool = Form(False),
    profile_photo: UploadFile = File(...)
):
    """
    Report a new unidentified body
    Adds record to database and vector database
    """
    try:
        # Save photo temporarily
        temp_photo_path = f"temp_{uuid.uuid4()}.jpg"
        save_upload_file(profile_photo, temp_photo_path)
        
        # Prepare data dictionary for db_helper
        data = {
            'case_number': f"CASE-AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'police_station': police_station,
            'reported_date': found_date,  # Use found_date as reported_date
            'found_date': found_date,
            'postmortem_date': postmortem_date,
            'estimated_age': estimated_age,
            'gender': gender,
            'height_cm': height_cm,
            'build': build,
            'complexion': complexion,
            'face_shape': face_shape,
            'hair_color': hair_color,
            'eye_color': eye_color,
            'distinguishing_marks': distinguishing_marks,
            'distinctive_features': distinctive_features,
            'clothing_description': clothing_description,
            'jewelry_description': jewelry_description,
            'person_description': person_description,
            'found_latitude': found_latitude,
            'found_longitude': found_longitude,
            'found_address': found_address,
            'cause_of_death': cause_of_death,
            'estimated_death_time': estimated_death_time,
            'dna_sample_collected': 1 if dna_sample_collected else 0,
            'dental_records_available': 1 if dental_records_available else 0,
            'fingerprints_collected': 1 if fingerprints_collected else 0,
            'postmortem_report_url': None,
            'additional_notes': None,
            'status': 'Open'
        }
        
        # Add to database
        pid = db_helper.add_unidentified_body(
            data=data,
            profile_photo_path=temp_photo_path
        )
        
        if not pid:
            raise Exception("Failed to add record to database")
        
        # Get the database ID
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM unidentified_bodies WHERE pid = ?", (pid,))
        result = cursor.fetchone()
        db_id = result[0] if result else None
        conn.close()
        
        # Clean up temp file
        if os.path.exists(temp_photo_path):
            os.remove(temp_photo_path)
        # Clean up temp file
        if os.path.exists(temp_photo_path):
            os.remove(temp_photo_path)
        
        # Get the saved photo path
        record = get_record_details(pid)
        photo_path = record.get('profile_photo', '') if record else ''
        
        # Generate embeddings and add to vector DB
        embeddings_added = []
        
        # 1. Text embedding
        try:
            data_dict = {
                'gender': gender,
                'estimated_age': estimated_age,
                'height_cm': height_cm,
                'build': build,
                'complexion': complexion,
                'face_shape': face_shape,
                'hair_color': hair_color,
                'eye_color': eye_color,
                'distinguishing_marks': distinguishing_marks,
                'distinctive_features': distinctive_features,
                'clothing_description': clothing_description,
                'jewelry_description': jewelry_description,
                'person_description': person_description,
                'found_address': found_address
            }
            
            text_description = generate_text_description(data_dict)
            text_embedding = text_embedder.get_embedding(text_description)
            
            # Create metadata
            metadata = {
                "pid": pid,
                "record_type": "unidentified_body",
                "gender": gender,
                "estimated_age": estimated_age,
                "height_cm": height_cm,
                "build": build,
                "complexion": complexion,
                "face_shape": face_shape,
                "hair_color": hair_color,
                "eye_color": eye_color,
                "distinguishing_marks": distinguishing_marks,
                "distinctive_features": distinctive_features,
                "clothing_description": clothing_description,
                "found_address": found_address,
                "police_station": police_station,
                "found_date": found_date,
                "status": "Open",
                "description": text_description
            }
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Add to Qdrant text collection
            point = PointStruct(
                id=db_id,
                vector=text_embedding.tolist(),
                payload=metadata
            )
            qdrant_client.upsert(
                collection_name="text_embeddings",
                points=[point]
            )
            embeddings_added.append("text")
            
        except Exception as e:
            print(f"Warning: Failed to add text embedding: {e}")
        
        # 2. Face embedding (if face recognition available)
        if FACE_RECOGNITION_AVAILABLE and record and photo_path:
            try:
                # Get full photo path
                full_photo_path = photo_path if os.path.isabs(photo_path) else os.path.join(os.getcwd(), photo_path)
                
                if os.path.exists(full_photo_path):
                    face_embedding = face_extractor.extract_embedding(full_photo_path, return_normalized=True)
                    
                    # Add to Qdrant face collection
                    point = PointStruct(
                        id=db_id,
                        vector=face_embedding.tolist(),
                        payload=metadata
                    )
                    qdrant_client.upsert(
                        collection_name="face_embeddings",
                        points=[point]
                    )
                    embeddings_added.append("face")
                
            except Exception as e:
                print(f"Warning: Failed to add face embedding: {e}")
        
        return {
            "status": "success",
            "message": "Unidentified body report created successfully",
            "data": {
                "pid": pid,
                "id": db_id,
                "photo_path": photo_path,
                "embeddings_added": embeddings_added
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")


@app.post("/api/search-missing-person")
async def search_missing_person(
    full_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    height_cm: Optional[int] = Form(None),
    build: Optional[str] = Form(None),
    hair_color: Optional[str] = Form(None),
    eye_color: Optional[str] = Form(None),
    distinguishing_marks: Optional[str] = Form(None),
    last_seen_clothing: Optional[str] = Form(None),
    person_description: Optional[str] = Form(None),
    search_text: Optional[str] = Form(None),
    top_n: int = Form(10),
    face_weight: float = Form(0.6),
    text_weight: float = Form(0.4),
    photo: Optional[UploadFile] = File(None)
):
    """
    Search for missing person matches
    Returns top N matches from vector database with full details
    """
    try:
        face_embedding = None
        text_embedding = None
        
        # 1. Process photo if provided
        if photo and FACE_RECOGNITION_AVAILABLE:
            try:
                # Save temporary photo
                temp_photo_path = f"temp_{uuid.uuid4()}.jpg"
                save_upload_file(photo, temp_photo_path)
                
                # Extract face embedding
                face_embedding = face_extractor.extract_embedding(temp_photo_path, return_normalized=True)
                
                # Clean up temp file
                os.remove(temp_photo_path)
                
            except Exception as e:
                print(f"Warning: Failed to extract face embedding: {e}")
        
        # 2. Generate text embedding
        if search_text:
            # Use custom search text if provided
            description = search_text
        else:
            # Generate from form data
            data_dict = {
                'full_name': full_name,
                'age': age,
                'gender': gender,
                'height_cm': height_cm,
                'build': build,
                'hair_color': hair_color,
                'eye_color': eye_color,
                'distinguishing_marks': distinguishing_marks,
                'last_seen_clothing': last_seen_clothing,
                'person_description': person_description
            }
            description = generate_text_description(data_dict)
        
        try:
            text_embedding = text_embedder.get_embedding(description)
        except Exception as e:
            print(f"Warning: Failed to generate text embedding: {e}")
        
        # 3. Perform vector search
        if face_embedding is None and text_embedding is None:
            raise HTTPException(
                status_code=400,
                detail="No valid embeddings generated. Provide either a photo or text description."
            )
        
        # Search using vector retrieval
        search_results = vector_retrieval.search_and_combine(
            face_embedding=face_embedding,
            text_embedding=text_embedding,
            gender=None,  # No metadata filters
            age_min=None,
            age_max=None,
            height_min=None,
            height_max=None,
            w1=face_weight,
            w2=text_weight,
            top_n=top_n,
            limit_per_collection=50
        )
        
        # 4. Enrich results with full database details
        enriched_results = []
        for result in search_results:
            pid = result['pid']
            record_details = get_record_details(pid)
            
            if record_details:
                # Parse extra_photos if it's a JSON string
                if record_details.get('extra_photos'):
                    try:
                        record_details['extra_photos'] = json.loads(record_details['extra_photos'])
                    except:
                        pass
                
                enriched_results.append({
                    "pid": pid,
                    "combined_score": result['combined_score'],
                    "face_score": result['face_score'],
                    "text_score": result['text_score'],
                    "confidence_percentage": round(result['combined_score'] * 100, 2),
                    "details": record_details
                })
        
        return {
            "status": "success",
            "message": f"Found {len(enriched_results)} potential matches",
            "search_params": {
                "description": description,
                "has_photo": photo is not None,
                "face_weight": face_weight,
                "text_weight": text_weight
            },
            "results": enriched_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/record/{pid}")
async def get_record(pid: str):
    """Get full record details by PID"""
    try:
        record = get_record_details(pid)
        
        if not record:
            raise HTTPException(status_code=404, detail=f"Record not found: {pid}")
        
        # Parse extra_photos if it's a JSON string
        if record.get('extra_photos'):
            try:
                record['extra_photos'] = json.loads(record['extra_photos'])
            except:
                pass
        
        return {
            "status": "success",
            "data": record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch record: {str(e)}")


@app.get("/api/stats")
async def get_statistics():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Count unidentified bodies
        cursor.execute("SELECT COUNT(*) FROM unidentified_bodies")
        uidb_count = cursor.fetchone()[0]
        
        # Count missing persons
        cursor.execute("SELECT COUNT(*) FROM missing_persons")
        mp_count = cursor.fetchone()[0]
        
        # Count by status
        cursor.execute("SELECT status, COUNT(*) FROM unidentified_bodies GROUP BY status")
        uidb_by_status = dict(cursor.fetchall())
        
        cursor.execute("SELECT status, COUNT(*) FROM missing_persons GROUP BY status")
        mp_by_status = dict(cursor.fetchall())
        
        conn.close()
        
        # Qdrant stats
        try:
            text_collection = qdrant_client.get_collection("text_embeddings")
            text_count = text_collection.points_count
        except:
            text_count = 0
        
        try:
            face_collection = qdrant_client.get_collection("face_embeddings")
            face_count = face_collection.points_count
        except:
            face_count = 0
        
        return {
            "status": "success",
            "data": {
                "database": {
                    "unidentified_bodies": uidb_count,
                    "missing_persons": mp_count,
                    "uidb_by_status": uidb_by_status,
                    "mp_by_status": mp_by_status
                },
                "vector_database": {
                    "text_embeddings": text_count,
                    "face_embeddings": face_count
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("Starting Missing Persons & Unidentified Bodies API")
    print("="*70)
    print(f"Database: {DB_FILE}")
    print(f"Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")
    print(f"Face Recognition: {'Available' if FACE_RECOGNITION_AVAILABLE else 'Not Available'}")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
