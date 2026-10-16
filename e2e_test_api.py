import requests
import json
import sys

BASE_URL = "http://158.101.106.119:8003"

def log_step(step_name):
    print("\n" + "=" * 60)
    print(step_name)
    print("=" * 60)

def main():
    session = requests.Session()

    # Step 1: Health check
    log_step("Step 1 — Health check: GET /")
    try:
        r1 = session.get(f"{BASE_URL}/", timeout=30)
        print(f"Status Code: {r1.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(r1.json(), indent=2))
        except Exception:
            print(f"Response Body: {r1.text}")
        if r1.status_code != 200:
            print(f"[FAIL] Health check failed with status {r1.status_code}")
            return
        print("[SUCCESS] Step 1 passed.")
    except Exception as e:
        print(f"[ERROR] Step 1 request failed: {type(e).__name__}: {e}")
        return

    # Step 2: Upload JD
    log_step("Step 2 — Upload Job Description: POST /upload-jd")
    jd_payload = {
        "title": "Senior Python Developer",
        "description": "We are looking for an experienced Python developer with strong backend skills.",
        "skills_required": ["python", "fastapi", "docker", "postgresql"],
        "experience_years": 3,
        "education": "bachelors"
    }
    try:
        r2 = session.post(f"{BASE_URL}/upload-jd", json=jd_payload, timeout=30)
        print(f"Status Code: {r2.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(r2.json(), indent=2))
        except Exception:
            print(f"Response Body: {r2.text}")
        if r2.status_code != 200:
            print(f"[FAIL] Upload JD failed with status {r2.status_code}")
            return
        print("[SUCCESS] Step 2 passed.")
    except Exception as e:
        print(f"[ERROR] Step 2 request failed: {type(e).__name__}: {e}")
        return

    # Step 3: Upload Resume
    log_step("Step 3 — Upload a resume as txt file: POST /upload-resume")
    resume_text = """Name: Ahmed Khan
Email: ahmed@example.com
Skills: Python, FastAPI, Docker, PostgreSQL, Redis
Experience: 5 years of backend development
Education: Bachelors in Computer Science
"""
    try:
        files = {
            "file": ("ahmed_khan_resume.txt", resume_text.encode("utf-8"), "text/plain")
        }
        r3 = session.post(f"{BASE_URL}/upload-resume", files=files, timeout=60)
        print(f"Status Code: {r3.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(r3.json(), indent=2))
        except Exception:
            print(f"Response Body: {r3.text}")
        if r3.status_code != 200:
            print(f"[FAIL] Upload Resume failed with status {r3.status_code}")
            return
        print("[SUCCESS] Step 3 passed.")
    except Exception as e:
        print(f"[ERROR] Step 3 request failed: {type(e).__name__}: {e}")
        return

    # Step 4: Get ranked candidates
    log_step("Step 4 — Get ranked candidates: GET /ranked-candidates")
    try:
        r4 = session.get(f"{BASE_URL}/ranked-candidates", timeout=120)
        print(f"Status Code: {r4.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(r4.json(), indent=2))
        except Exception:
            print(f"Response Body: {r4.text}")
        if r4.status_code != 200:
            print(f"[FAIL] Get ranked candidates failed with status {r4.status_code}")
            return
        print("[SUCCESS] Step 4 passed.")
    except Exception as e:
        print(f"[ERROR] Step 4 request failed: {type(e).__name__}: {e}")
        return

    # Step 5: Clear all data
    log_step("Step 5 — Clear all data: DELETE /clear")
    try:
        r5 = session.delete(f"{BASE_URL}/clear", timeout=30)
        print(f"Status Code: {r5.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(r5.json(), indent=2))
        except Exception:
            print(f"Response Body: {r5.text}")
        if r5.status_code != 200:
            print(f"[FAIL] Clear data failed with status {r5.status_code}")
            return
        print("[SUCCESS] Step 5 passed.")
    except Exception as e:
        print(f"[ERROR] Step 5 request failed: {type(e).__name__}: {e}")
        return

    print("\n" + "=" * 60)
    print("ALL 5 STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
