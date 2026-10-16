#!/usr/bin/env python3
"""
Resume Screening AI - Backend Test Suite
Tests all endpoints of the FastAPI backend running at http://localhost:8003
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8003"

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(test_name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(message):
    print(f"{GREEN}[PASS] SUCCESS: {message}{RESET}")

def print_error(message):
    print(f"{RED}[FAIL] ERROR: {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}[INFO] INFO: {message}{RESET}")

def test_health_check():
    """Test 1: Health Check"""
    print_header("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            if data.get("status") == "running":
                print_success("Health check passed - status is 'running'")
                print_info(f"Resumes indexed: {data.get('resumes_indexed', 0)}")
                print_info(f"Model: {data.get('model')}")
                print_info(f"Embed model: {data.get('embed_model')}")
                return True
            else:
                print_error(f"Status is not 'running': {data.get('status')}")
                return False
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running at http://localhost:8003?")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_upload_jd():
    """Test 2: Upload Job Description"""
    print_header("Upload Job Description")

    jd_payload = {
        "title": "Senior Python AI Engineer",
        "description": "Looking for an expert in Python, FastAPI, Docker, LangChain, and Groq LLaMA models.",
        "skills_required": ["python", "fastapi", "docker", "langchain", "groq"],
        "experience_years": 3,
        "education": "bachelors"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/upload-jd",
            json=jd_payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Request Payload: {json.dumps(jd_payload, indent=2)}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            if "jd_id" in data and data.get("title") == jd_payload["title"]:
                print_success(f"JD uploaded successfully with ID: {data['jd_id']}")
                return data['jd_id']
            else:
                print_error(f"Unexpected response structure: {data}")
                return None
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            print(f"Error response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Error uploading JD: {str(e)}")
        return None

def test_upload_resume():
    """Test 3: Upload Resume"""
    print_header("Upload Resume")

    # First, check if we have a sample resume file
    resume_path = Path("D:/Resume-screening-ai/backend/test_resume.txt")

    # Create a simple test resume if it doesn't exist
    if not resume_path.exists():
        print_info("Creating test resume file...")
        resume_content = """John Doe
Email: john.doe@example.com
Phone: +1-555-0123

Senior Python Developer with 5 years of experience.

Skills:
- Python
- FastAPI
- Docker
- LangChain
- Groq
- Machine Learning
- NLP

Experience:
Senior Python Developer at Tech Corp (2020-Present)
- Built scalable APIs using FastAPI
- Deployed applications using Docker
- Implemented AI solutions using LangChain and Groq

Education:
Bachelor of Science in Computer Science
"""
        resume_path.write_text(resume_content)
        print_info(f"Test resume created at: {resume_path}")

    try:
        with open(resume_path, 'rb') as f:
            files = {'file': (resume_path.name, f, 'text/plain')}
            response = requests.post(
                f"{BASE_URL}/upload-resume",
                files=files,
                timeout=30
            )

        print(f"Status Code: {response.status_code}")
        print(f"Uploaded file: {resume_path.name}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            if "resume_id" in data and data.get("indexed") == True:
                print_success(f"Resume uploaded successfully with ID: {data['resume_id']}")
                parsed = data.get("parsed", {})
                print_info(f"Candidate Name: {parsed.get('name', 'N/A')}")
                print_info(f"Email: {parsed.get('email', 'N/A')}")
                print_info(f"Experience Years: {parsed.get('experience_years', 0)}")
                print_info(f"Skills Detected: {parsed.get('skills_detected', [])}")
                return data['resume_id']
            else:
                print_error(f"Unexpected response structure: {data}")
                return None
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            print(f"Error response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Error uploading resume: {str(e)}")
        return None

def test_collection_info():
    """Test 4: Verify Collection Info"""
    print_header("Collection Info")

    try:
        response = requests.get(f"{BASE_URL}/collection-info", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            count = data.get("count", 0)
            if count > 0:
                print_success(f"ChromaDB has {count} indexed resume(s)")
                print_info(f"Sample IDs: {data.get('sample_ids', [])}")
                return True
            else:
                print_info("ChromaDB is empty (no resumes indexed yet)")
                return True
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error fetching collection info: {str(e)}")
        return False

def test_ranked_candidates():
    """Test 5: Ranked Candidates Pipeline"""
    print_header("Ranked Candidates Pipeline")

    try:
        response = requests.get(f"{BASE_URL}/ranked-candidates", timeout=60)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            # Verify key components
            checks = {
                "job_title": data.get("job_title"),
                "expanded_query": data.get("expanded_query"),
                "total_indexed": data.get("total_indexed"),
                "retrieved_by_search": data.get("retrieved_by_search"),
                "sent_to_llm": data.get("sent_to_llm"),
                "ranked_candidates": data.get("ranked_candidates")
            }

            all_passed = True

            if data.get("job_title"):
                print_success(f"Job Title: {data['job_title']}")
            else:
                print_error("Missing job_title")
                all_passed = False

            if data.get("expanded_query"):
                print_success(f"Query Transformation: {data['expanded_query'][:100]}...")
            else:
                print_error("Missing expanded_query")
                all_passed = False

            print_info(f"Total Indexed: {data.get('total_indexed', 0)}")
            print_info(f"Retrieved by Search: {data.get('retrieved_by_search', 0)}")
            print_info(f"Sent to LLM: {data.get('sent_to_llm', 0)}")

            if data.get("shortlisted") is not None:
                print_info(f"Shortlisted: {data.get('shortlisted')}")
            if data.get("maybe") is not None:
                print_info(f"Maybe: {data.get('maybe')}")
            if data.get("rejected") is not None:
                print_info(f"Rejected: {data.get('rejected')}")

            candidates = data.get("ranked_candidates", [])
            if candidates:
                print_success(f"Found {len(candidates)} ranked candidates")
                for i, cand in enumerate(candidates[:3], 1):
                    print_info(f"\nCandidate {i}:")
                    print_info(f"  Name: {cand.get('candidate_name', 'N/A')}")
                    print_info(f"  Final Score: {cand.get('final_score', 0)}")
                    print_info(f"  Recommendation: {cand.get('recommendation', 'N/A')}")
                    print_info(f"  Rerank Score: {cand.get('rerank_score', 0)}")
                    print_info(f"  Vector Distance: {cand.get('vector_distance', 0)}")
                    print_info(f"  Matched Skills: {cand.get('matched_skills', [])}")
            else:
                print_info("No candidates found (expected if no resumes uploaded)")

            if all_passed:
                print_success("Ranked candidates pipeline executed successfully")
            return all_passed

        elif response.status_code == 404:
            data = response.json()
            print_info(f"Expected 404 (no data yet): {data.get('detail', 'No resumes indexed yet')}")
            return True
        else:
            print_error(f"Expected status 200 or 404, got {response.status_code}")
            print(f"Error response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error fetching ranked candidates: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}RESUME SCREENING AI - BACKEND TEST SUITE{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"{YELLOW}Testing endpoint: {BASE_URL}{RESET}\n")

    results = {}

    # Test 1: Health Check
    results["health_check"] = test_health_check()

    # Test 2: Upload JD
    jd_id = test_upload_jd()
    results["upload_jd"] = jd_id is not None

    # Test 3: Upload Resume
    resume_id = test_upload_resume()
    results["upload_resume"] = resume_id is not None

    # Test 4: Collection Info
    results["collection_info"] = test_collection_info()

    # Test 5: Ranked Candidates
    results["ranked_candidates"] = test_ranked_candidates()

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        print(f"{status} - {test_name}")

    print(f"\n{BLUE}Total: {passed_tests}/{total_tests} tests passed{RESET}")

    if passed_tests == total_tests:
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}ALL TESTS PASSED! 🎉{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
    else:
        print(f"{RED}{'='*60}{RESET}")
        print(f"{RED}SOME TESTS FAILED{RESET}")
        print(f"{RED}{'='*60}{RESET}")

if __name__ == "__main__":
    main()
