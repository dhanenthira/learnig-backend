import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class DataStore:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.questions: Dict[str, Dict[str, Any]] = {}
        self.lessons: Dict[str, Dict[str, Any]] = {}
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.daily_sets: Dict[str, Dict[str, Any]] = {}
        self.coding_problems: Dict[str, Dict[str, Any]] = {}
        self.tests: Dict[str, Dict[str, Any]] = {}
        self.practice_submissions: Dict[str, Dict[str, Any]] = {}
        self.code_submissions: Dict[str, Dict[str, Any]] = {}
        self.test_submissions: Dict[str, Dict[str, Any]] = {}
        self.battle_rooms: Dict[str, Dict[str, Any]] = {}
        self.notifications: Dict[str, List[Dict[str, Any]]] = {}
        self.follows: Dict[str, List[str]] = {} # user_id -> [following_ids]
        self.friend_requests: Dict[str, List[str]] = {} # user_id -> [incoming_requester_ids]
        self.seed_initial_data()

    def seed_initial_data(self):
        # 1. Seed Admin User
        admin_id = "user_admin_01"
        self.users[admin_id] = {
            "id": admin_id,
            "student_id": "ADM-001",
            "email": "admin@codearena.com",
            "password": "adminpassword123",
            "name": "System Administrator",
            "role": "admin",
            "college_name": "CodeArena HQ",
            "department": "Platform Core",
            "graduation_year": 2024,
            "bio": "Lead System Architect & Admin",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=admin",
            "created_at": datetime.utcnow() - timedelta(days=90),
            "streak_days": 45,
            "total_points": 12500,
            "problems_solved": 320,
            "questions_solved": 850,
            "overall_accuracy": 94.5,
            "coding_problems_solved": 140,
            "battles_won": 42,
            "followers_count": 128,
            "following_count": 12,
            "is_active": True
        }

        # 2. Seed Demo Student Users
        student_1_id = "user_student_01"
        self.users[student_1_id] = {
            "id": student_1_id,
            "student_id": "CA-2026-9042",
            "email": "student@codearena.com",
            "password": "password123",
            "name": "Alex Mercer",
            "role": "student",
            "college_name": "National Institute of Technology",
            "department": "Computer Science & Engineering",
            "graduation_year": 2026,
            "bio": "Passionate competitive programmer and full-stack enthusiast.",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
            "created_at": datetime.utcnow() - timedelta(days=45),
            "streak_days": 14,
            "total_points": 4850,
            "problems_solved": 142,
            "questions_solved": 380,
            "overall_accuracy": 88.2,
            "coding_problems_solved": 56,
            "battles_won": 19,
            "followers_count": 28,
            "following_count": 15,
            "is_active": True
        }

        student_2_id = "user_student_02"
        self.users[student_2_id] = {
            "id": student_2_id,
            "student_id": "CA-2026-8190",
            "email": "sophia@codearena.com",
            "password": "password123",
            "name": "Sophia Chen",
            "role": "student",
            "college_name": "Tech University",
            "department": "Information Technology",
            "graduation_year": 2025,
            "bio": "Algorithms lover & hackathon enthusiast.",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sophia",
            "created_at": datetime.utcnow() - timedelta(days=60),
            "streak_days": 21,
            "total_points": 5620,
            "problems_solved": 180,
            "questions_solved": 450,
            "overall_accuracy": 91.0,
            "coding_problems_solved": 78,
            "battles_won": 27,
            "followers_count": 45,
            "following_count": 30,
            "is_active": True
        }

        # Follow relationships
        self.follows[student_1_id] = [student_2_id, admin_id]
        self.follows[student_2_id] = [student_1_id]

        # 3. Seed Questions (Aptitude & Technical)
        q1_id = "q_apt_01"
        self.questions[q1_id] = {
            "id": q1_id,
            "title": "Train Speed & Distance",
            "content": "A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train in meters?",
            "category": "aptitude",
            "topic": "Time & Distance",
            "difficulty": "easy",
            "question_type": "mcq",
            "options": ["120 metres", "150 metres", "180 metres", "324 metres"],
            "correct_answer": "150 metres",
            "explanation": "Speed = 60 * (5/18) m/sec = 50/3 m/sec. Length = Speed * Time = (50/3) * 9 = 150 metres.",
            "marks": 1,
            "tags": ["Aptitude", "Speed", "Trains"],
            "created_at": datetime.utcnow() - timedelta(days=10)
        }

        q2_id = "q_apt_02"
        self.questions[q2_id] = {
            "id": q2_id,
            "title": "Profit and Loss Calculation",
            "content": "A shopkeeper sells an article for $240 and gains 20%. What was the cost price of the article?",
            "category": "aptitude",
            "topic": "Profit & Loss",
            "difficulty": "easy",
            "question_type": "mcq",
            "options": ["$190", "$200", "$210", "$220"],
            "correct_answer": "$200",
            "explanation": "Cost Price = (Selling Price * 100) / (100 + Gain%) = (240 * 100) / 120 = $200.",
            "marks": 1,
            "tags": ["Aptitude", "Arithmetic", "Profit"],
            "created_at": datetime.utcnow() - timedelta(days=10)
        }

        q3_id = "q_tech_01"
        self.questions[q3_id] = {
            "id": q3_id,
            "title": "Time Complexity of Binary Search",
            "content": "What is the worst-case time complexity of Binary Search on a sorted array of n elements?",
            "category": "technical",
            "topic": "Data Structures & Algorithms",
            "difficulty": "easy",
            "question_type": "mcq",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            "correct_answer": "O(log n)",
            "explanation": "In each step, binary search halves the search space, giving a logarithmic time complexity of O(log n).",
            "marks": 1,
            "tags": ["DSA", "Binary Search", "Complexity"],
            "created_at": datetime.utcnow() - timedelta(days=9)
        }

        q4_id = "q_tech_02"
        self.questions[q4_id] = {
            "id": q4_id,
            "title": "HTTP Status Code for Unauthorized",
            "content": "Which HTTP status code signifies that authentication is required and has failed or has not yet been provided?",
            "category": "technical",
            "topic": "Computer Networks & Web",
            "difficulty": "easy",
            "question_type": "mcq",
            "options": ["400 Bad Request", "401 Unauthorized", "403 Forbidden", "404 Not Found"],
            "correct_answer": "401 Unauthorized",
            "explanation": "401 Unauthorized is returned when authentication credentials are required and missing or invalid.",
            "marks": 1,
            "tags": ["Networks", "HTTP", "Web"],
            "created_at": datetime.utcnow() - timedelta(days=8)
        }

        # 4. Seed Learning Modules & Lessons (W3Schools style)
        mod_py_id = "mod_python"
        self.modules[mod_py_id] = {
            "id": mod_py_id,
            "title": "Python Programming",
            "category": "python",
            "description": "Master Python from basics to object-oriented programming and standard libraries.",
            "icon": "code-2",
            "total_lessons": 4,
            "completed_lessons": 2,
            "progress_percentage": 50.0,
            "topics": [
                {"id": "py_intro", "title": "Python Introduction", "slug": "python-intro", "order": 1, "is_completed": True},
                {"id": "py_syntax", "title": "Python Syntax & Variables", "slug": "python-syntax", "order": 2, "is_completed": True},
                {"id": "py_data_types", "title": "Python Data Structures", "slug": "python-data-types", "order": 3, "is_completed": False},
                {"id": "py_functions", "title": "Python Functions & Lambda", "slug": "python-functions", "order": 4, "is_completed": False},
            ]
        }

        self.lessons["py_intro"] = {
            "id": "py_intro",
            "module_id": mod_py_id,
            "topic_id": "py_intro",
            "title": "Python Introduction & Getting Started",
            "intro": "Python is a popular, high-level, interpreted programming language created by Guido van Rossum and released in 1991.",
            "definition": "Python is designed for readability and simplicity, with English-like syntax and extensive cross-platform library support.",
            "explanation": "Python can be used on a server to create web applications, alongside software to create workflows, to connect to database systems, and to handle big data and complex mathematics.",
            "syntax": "print('Hello, CodeArena!')",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "# Our first Python program\nname = 'CodeArena Champion'\nprint(f'Welcome to the arena, {name}!')",
                    "output": "Welcome to the arena, CodeArena Champion!"
                }
            ],
            "notes": [
                "Python uses indentation to indicate a block of code instead of curly braces.",
                "Python works on different platforms (Windows, Mac, Linux, Raspberry Pi, etc).",
                "Python has a simple syntax similar to the English language."
            ],
            "category": "python",
            "order": 1,
            "is_completed": True,
            "practice_topic_id": "q_tech_01"
        }

        self.lessons["py_syntax"] = {
            "id": "py_syntax",
            "module_id": mod_py_id,
            "topic_id": "py_syntax",
            "title": "Python Syntax, Variables & Types",
            "intro": "Variables are containers for storing data values. Unlike other languages, Python has no command for declaring a variable.",
            "definition": "A variable is created the moment you first assign a value to it using the assignment operator (=).",
            "explanation": "Variables do not need to be declared with any particular type, and can even change type after they have been set.",
            "syntax": "x = 5\ny = 'Hello'",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "x = 10        # x is of type int\ny = 'Arena'   # y is now of type str\nprint(type(x))\nprint(type(y))",
                    "output": "<class 'int'>\n<class 'str'>"
                }
            ],
            "notes": [
                "Variable names are case-sensitive (age, Age and AGE are three different variables).",
                "A variable name must start with a letter or the underscore character."
            ],
            "category": "python",
            "order": 2,
            "is_completed": True,
            "practice_topic_id": "q_tech_01"
        }

        # 5. Seed Coding Problems (LeetCode / HackerRank style)
        cp1_id = "cp_two_sum"
        self.coding_problems[cp1_id] = {
            "id": cp1_id,
            "title": "Two Sum Target Indices",
            "slug": "two-sum-target-indices",
            "difficulty": "easy",
            "topic": "Arrays & Hash Table",
            "description": "Given an array of integers `nums` and an integer `target`, return the indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
            "constraints": [
                "2 <= nums.length <= 10^4",
                "-10^9 <= nums[i] <= 10^9",
                "-10^9 <= target <= 10^9",
                "Only one valid answer exists."
            ],
            "examples": [
                {
                    "input": "nums = [2,7,11,15], target = 9",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                },
                {
                    "input": "nums = [3,2,4], target = 6",
                    "output": "[1,2]"
                }
            ],
            "input_format": "Space-separated integers for nums on line 1, target integer on line 2.",
            "output_format": "Two space-separated integers representing the 0-indexed positions.",
            "hints": [
                "A brute force approach checks every pair in O(n^2) time.",
                "Can you use a Hash Map to store complements in O(n) time?"
            ],
            "time_limit_seconds": 2.0,
            "memory_limit_mb": 128,
            "sample_test_cases": [
                {"input": "2 7 11 15\n9", "expected_output": "0 1", "is_hidden": False, "explanation": "2+7=9 at indices 0,1"},
                {"input": "3 2 4\n6", "expected_output": "1 2", "is_hidden": False, "explanation": "2+4=6 at indices 1,2"}
            ],
            "hidden_test_cases": [
                {"input": "3 3\n6", "expected_output": "0 1", "is_hidden": True},
                {"input": "1 5 8 12 19\n20", "expected_output": "0 4", "is_hidden": True}
            ],
            "starter_codes": [
                {
                    "language": "python",
                    "code": "def two_sum(nums, target):\n    # Write your solution here\n    seen = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in seen:\n            return f\"{seen[diff]} {i}\"\n        seen[num] = i\n    return \"\"\n\nif __name__ == '__main__':\n    import sys\n    lines = sys.stdin.read().splitlines()\n    if lines:\n        nums = list(map(int, lines[0].split()))\n        target = int(lines[1])\n        print(two_sum(nums, target))"
                },
                {
                    "language": "javascript",
                    "code": "const fs = require('fs');\nconst input = fs.readFileSync('/dev/stdin', 'utf-8').trim().split('\\n');\nif (input.length >= 2) {\n    const nums = input[0].trim().split(/\\s+/).map(Number);\n    const target = Number(input[1]);\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const complement = target - nums[i];\n        if (map.has(complement)) {\n            console.log(`${map.get(complement)} ${i}`);\n            process.exit(0);\n        }\n        map.set(nums[i], i);\n    }\n}"
                },
                {
                    "language": "cpp",
                    "code": "#include <iostream>\n#include <vector>\n#include <unordered_map>\nusing namespace std;\n\nint main() {\n    int target;\n    vector<int> nums;\n    int val;\n    while (cin >> val) nums.push_back(val);\n    target = nums.back();\n    nums.pop_back();\n    unordered_map<int, int> mp;\n    for (int i = 0; i < nums.size(); i++) {\n        int comp = target - nums[i];\n        if (mp.count(comp)) {\n            cout << mp[comp] << \" \" << i << endl;\n            return 0;\n        }\n        mp[nums[i]] = i;\n    }\n    return 0;\n}"
                }
            ],
            "tags": ["Array", "Hash Table", "Top Interview"],
            "is_solved": True,
            "total_submissions": 450,
            "acceptance_rate": 82.4
        }

        # 6. Seed Daily Practice Sets
        d_apt_id = "ds_apt_today"
        self.daily_sets[d_apt_id] = {
            "id": d_apt_id,
            "title": "Daily Aptitude Challenge - Set #42",
            "category": "aptitude",
            "difficulty": "medium",
            "question_count": 2,
            "estimated_minutes": 10,
            "marks_per_question": 1,
            "total_marks": 2,
            "is_completed": False,
            "created_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "question_ids": [q1_id, q2_id]
        }

        d_tech_id = "ds_tech_today"
        self.daily_sets[d_tech_id] = {
            "id": d_tech_id,
            "title": "Daily Technical Challenge - Set #42",
            "category": "technical",
            "difficulty": "easy",
            "question_count": 2,
            "estimated_minutes": 8,
            "marks_per_question": 1,
            "total_marks": 2,
            "is_completed": True,
            "best_score": 2,
            "created_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "question_ids": [q3_id, q4_id]
        }

        # 7. Seed Formal Assessment Test
        t1_id = "test_nationwide_01"
        self.tests[t1_id] = {
            "id": t1_id,
            "title": "All-India Coding & Aptitude Grand Assessment",
            "description": "National level screening test evaluating speed, logical reasoning, and computer science fundamentals.",
            "category": "mixed",
            "difficulty": "medium",
            "duration_minutes": 30,
            "total_marks": 40,
            "total_questions": 4,
            "rules": [
                "Once started, the countdown timer cannot be paused.",
                "Full-screen mode recommended.",
                "Questions carry 1 mark each with no negative marking.",
                "Final score and detailed solutions will be unlocked after the assessment window."
            ],
            "start_time": datetime.utcnow() - timedelta(hours=2),
            "end_time": datetime.utcnow() + timedelta(days=5),
            "status": "active",
            "is_attempted": False,
            "question_ids": [q1_id, q2_id, q3_id, q4_id]
        }

        # 8. Seed Notifications
        self.notifications[student_1_id] = [
            {
                "id": "notif_01",
                "title": "Daily Aptitude Practice is Ready!",
                "message": "Today's Time & Distance aptitude challenge has been published. Maintain your 14-day streak!",
                "type": "daily_challenge",
                "is_read": False,
                "action_url": "/student/practice",
                "created_at": datetime.utcnow() - timedelta(hours=3)
            },
            {
                "id": "notif_02",
                "title": "Grand Assessment Live",
                "message": "All-India Coding & Aptitude Grand Assessment is now open for submissions.",
                "type": "test",
                "is_read": True,
                "action_url": "/student/tests",
                "created_at": datetime.utcnow() - timedelta(days=1)
            }
        ]

data_store = DataStore()
