from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CodeArena" in data["platform"]

def test_auth_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "student@codearena.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"

def test_admin_login():
    response = client.post("/api/v1/auth/admin/login", json={
        "email": "admin@codearena.com",
        "password": "adminpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"

def test_student_dashboard():
    response = client.get("/api/v1/students/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "daily_challenges" in data

def test_coding_problems_and_run():
    response = client.get("/api/v1/coding/problems")
    assert response.status_code == 200
    problems = response.json()
    assert len(problems) > 0
    prob_id = problems[0]["id"]
    
    # Run code
    run_resp = client.post("/api/v1/coding/run", json={
        "problem_id": prob_id,
        "language": "python",
        "code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        d = target - num\n        if d in seen: return f'{seen[d]} {i}'\n        seen[num] = i\n    return ''\n\nimport sys\nlines = sys.stdin.read().splitlines()\nif lines:\n    print(two_sum(list(map(int, lines[0].split())), int(lines[1])))"
    })
    assert run_resp.status_code == 200
    res_data = run_resp.json()
    assert res_data["status"] == "Accepted"
