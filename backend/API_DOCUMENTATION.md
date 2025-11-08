# API Documentation

## Missing Persons & Unidentified Bodies API

### Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check API and service status.

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "vector_db": "healthy",
  "face_recognition": "available"
}
```

---

### 2. Get Statistics
**GET** `/api/stats`

Get database statistics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "database": {
      "unidentified_bodies": 30,
      "missing_persons": 0,
      "uidb_by_status": {"Open": 30},
      "mp_by_status": {}
    },
    "vector_database": {
      "text_embeddings": 30,
      "face_embeddings": 0
    }
  }
}
```

---

### 3. Report Unidentified Body
**POST** `/api/report-unidentified-body`

Report a new unidentified body (multipart/form-data).

**Form Parameters:**
- `police_station` (required): Police station name
- `found_date` (required): Date/time found (YYYY-MM-DD HH:MM:SS)
- `gender` (required): Gender (Male/Female/Other/Unknown)
- `profile_photo` (required): Photo file (JPEG/PNG)
- `estimated_age` (optional): Estimated age in years
- `height_cm` (optional): Height in centimeters
- `build` (optional): Body build (Slim/Medium/Heavy)
- `complexion` (optional): Skin complexion
- `face_shape` (optional): Face shape description
- `hair_color` (optional): Hair color
- `eye_color` (optional): Eye color
- `distinguishing_marks` (optional): Notable marks/scars
- `distinctive_features` (optional): Distinctive features
- `clothing_description` (optional): Clothing description
- `jewelry_description` (optional): Jewelry description
- `person_description` (optional): General description
- `found_latitude` (optional): GPS latitude
- `found_longitude` (optional): GPS longitude
- `found_address` (optional): Address where found
- `cause_of_death` (optional): Cause of death
- `dna_sample_collected` (optional): Boolean (default: false)
- `dental_records_available` (optional): Boolean (default: false)
- `fingerprints_collected` (optional): Boolean (default: false)

**Response:**
```json
{
  "status": "success",
  "message": "Unidentified body report created successfully",
  "data": {
    "pid": "UIDB-2025-00131",
    "id": 31,
    "photo_path": "photos/unidentified_bodies/UIDB-2025-00131.jpg",
    "embeddings_added": ["text", "face"]
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/report-unidentified-body \
  -F "police_station=Worli Police Station" \
  -F "found_date=2025-11-09 10:00:00" \
  -F "gender=Male" \
  -F "estimated_age=65" \
  -F "height_cm=170" \
  -F "build=Medium" \
  -F "complexion=Fair" \
  -F "hair_color=Grey" \
  -F "eye_color=Brown" \
  -F "person_description=Elderly male with grey hair" \
  -F "found_address=Mumbai" \
  -F "profile_photo=@test.jpg"
```

---

### 4. Search Missing Person
**POST** `/api/search-missing-person`

Search for matching unidentified bodies (multipart/form-data).

**Form Parameters:**
- `photo` (optional): Photo file for face matching
- `search_text` (optional): Custom search description
- `full_name` (optional): Person's name
- `age` (optional): Age in years
- `gender` (optional): Gender
- `height_cm` (optional): Height in cm
- `build` (optional): Body build
- `hair_color` (optional): Hair color
- `eye_color` (optional): Eye color
- `distinguishing_marks` (optional): Distinguishing marks
- `last_seen_clothing` (optional): Last seen clothing
- `person_description` (optional): Person description
- `top_n` (optional): Number of results (default: 10, max: 50)
- `face_weight` (optional): Face similarity weight 0-1 (default: 0.6)
- `text_weight` (optional): Text similarity weight 0-1 (default: 0.4)

**Response:**
```json
{
  "status": "success",
  "message": "Found 5 potential matches",
  "search_params": {
    "description": "Male, 67 years old, 165cm tall...",
    "has_photo": true,
    "face_weight": 0.6,
    "text_weight": 0.4
  },
  "results": [
    {
      "pid": "UIDB-2025-00101",
      "combined_score": 0.8523,
      "face_score": 0.8912,
      "text_score": 0.7845,
      "confidence_percentage": 85.23,
      "details": {
        "pid": "UIDB-2025-00101",
        "gender": "Male",
        "estimated_age": 72,
        "height_cm": 160,
        "found_address": "Near Old Delhi Railway Station...",
        "police_station": "Kamla Nagar Police Station",
        "profile_photo": "1.jpg",
        ...
      }
    }
  ]
}
```

**cURL Example (with photo):**
```bash
curl -X POST http://localhost:8000/api/search-missing-person \
  -F "full_name=Rohan Sharma" \
  -F "age=67" \
  -F "gender=Male" \
  -F "height_cm=165" \
  -F "person_description=Elderly male with white beard" \
  -F "top_n=5" \
  -F "face_weight=0.6" \
  -F "text_weight=0.4" \
  -F "photo=@test.jpg"
```

**cURL Example (text only):**
```bash
curl -X POST http://localhost:8000/api/search-missing-person \
  -F "search_text=Male, 67 years old, slim build, white hair" \
  -F "top_n=5" \
  -F "face_weight=0" \
  -F "text_weight=1"
```

---

### 5. Get Record by PID
**GET** `/api/record/{pid}`

Get full record details by PID.

**Parameters:**
- `pid`: Person ID (e.g., UIDB-2025-00101)

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "pid": "UIDB-2025-00101",
    "record_type": "unidentified_body",
    "gender": "Male",
    "estimated_age": 72,
    "height_cm": 160,
    "build": "Slim",
    "complexion": "Fair to Medium",
    "face_shape": "Oval with prominent cheekbones",
    "hair_color": "White (bald top, grey sides)",
    "eye_color": "Brown",
    "found_address": "Near Old Delhi Railway Station, Chandni Chowk, Delhi",
    "police_station": "Kamla Nagar Police Station, Delhi",
    "found_date": "2025-01-15 07:30:00",
    "status": "Open",
    ...
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/record/UIDB-2025-00101
```

---

## Running the API

### Install Dependencies
```bash
pip install -r requirements_api.txt
```

### Start Server
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Test Endpoints
```bash
python test_api.py
```

### Access API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Not found
- `500`: Server error
