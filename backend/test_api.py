"""
Test script for FastAPI endpoints
Demonstrates how to use the API for reporting and searching
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_get_statistics():
    """Test statistics endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Get Statistics")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_report_unidentified_body():
    """Test reporting an unidentified body"""
    print("\n" + "="*70)
    print("TEST 3: Report Unidentified Body")
    print("="*70)
    
    # Check if test image exists
    test_image = "test.jpg"
    if not Path(test_image).exists():
        print(f"⚠ Test image not found: {test_image}")
        print("  Skipping this test")
        return None
    
    # Form data
    data = {
        "police_station": "Test Police Station, Mumbai",
        "found_date": "2025-11-09 10:00:00",
        "gender": "Male",
        "estimated_age": 65,
        "height_cm": 170,
        "build": "Medium",
        "complexion": "Fair",
        "face_shape": "Oval",
        "hair_color": "Grey",
        "eye_color": "Brown",
        "distinguishing_marks": "Scar on left cheek",
        "distinctive_features": "White beard",
        "clothing_description": "Blue shirt and black trousers",
        "found_address": "Test Location, Mumbai",
        "found_latitude": 19.0760,
        "found_longitude": 72.8777,
        "person_description": "Elderly male found unconscious",
        "dna_sample_collected": True,
        "dental_records_available": False,
        "fingerprints_collected": True
    }
    
    # Upload file
    files = {
        "profile_photo": open(test_image, "rb")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/report-unidentified-body",
            data=data,
            files=files
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json()['data']['pid']
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        files["profile_photo"].close()
    
    return None


def test_search_missing_person_with_photo():
    """Test searching with photo"""
    print("\n" + "="*70)
    print("TEST 4: Search Missing Person (with photo)")
    print("="*70)
    
    test_image = "test.jpg"
    if not Path(test_image).exists():
        print(f"⚠ Test image not found: {test_image}")
        print("  Skipping this test")
        return
    
    # Form data
    data = {
        "full_name": "Rohan Sharma",
        "age": 67,
        "gender": "Male",
        "height_cm": 165,
        "build": "Slim",
        "hair_color": "White/Grey",
        "person_description": "Elderly male with white beard, bald on top",
        "top_n": 5,
        "face_weight": 0.6,
        "text_weight": 0.4
    }
    
    # Upload file
    files = {
        "photo": open(test_image, "rb")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search-missing-person",
            data=data,
            files=files
        )
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(f"\nSearch Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"\nTop {len(result['results'])} Results:")
        
        for i, match in enumerate(result['results'], 1):
            print(f"\n  {i}. PID: {match['pid']}")
            print(f"     Confidence: {match['confidence_percentage']:.2f}%")
            print(f"     Combined Score: {match['combined_score']:.4f}")
            print(f"     Face Score: {match['face_score']:.4f}")
            print(f"     Text Score: {match['text_score']:.4f}")
            
            details = match['details']
            print(f"     Gender: {details.get('gender', 'N/A')}")
            print(f"     Age: {details.get('estimated_age', details.get('age', 'N/A'))}")
            print(f"     Location: {details.get('found_address', details.get('last_seen_address', 'N/A'))[:50]}...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        files["photo"].close()


def test_search_missing_person_text_only():
    """Test searching with text description only"""
    print("\n" + "="*70)
    print("TEST 5: Search Missing Person (text only)")
    print("="*70)
    
    # Form data
    data = {
        "search_text": "Male, 67 years old, slim build, white hair, bald on top, white beard, brown eyes, vitiligo patches on face",
        "top_n": 5,
        "face_weight": 0.0,
        "text_weight": 1.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search-missing-person",
            data=data
        )
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(f"\nSearch Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"\nTop {len(result['results'])} Results:")
        
        for i, match in enumerate(result['results'], 1):
            print(f"\n  {i}. PID: {match['pid']}")
            print(f"     Confidence: {match['confidence_percentage']:.2f}%")
            print(f"     Text Score: {match['text_score']:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")


def test_get_record(pid: str):
    """Test getting record by PID"""
    print("\n" + "="*70)
    print(f"TEST 6: Get Record by PID ({pid})")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/api/record/{pid}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nRecord Details:")
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"Error: {response.json()}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("FASTAPI ENDPOINT TESTS")
    print("="*70)
    print("\nMake sure the API server is running:")
    print("  python main.py")
    print("\nPress Enter to continue...")
    input()
    
    # Test 1: Health check
    if not test_health_check():
        print("\n⚠ API server not responding. Make sure it's running on port 8000")
        return
    
    # Test 2: Statistics
    test_get_statistics()
    
    # Test 3: Report unidentified body
    new_pid = test_report_unidentified_body()
    
    # Test 4: Search with photo
    test_search_missing_person_with_photo()
    
    # Test 5: Search with text only
    test_search_missing_person_text_only()
    
    # Test 6: Get record (if we created one)
    if new_pid:
        test_get_record(new_pid)
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
