"""
[DEPRECATED] DataStore previously held in-memory temporary mock records.
All endpoints have been transitioned directly to MySQL Database persistence via SQLAlchemy models in `app.models.sql_models`.
"""

class DataStore:
    def __init__(self):
        self.users = {}
        self.questions = {}
        self.lessons = {}
        self.modules = {}
        self.daily_sets = {}
        self.coding_problems = {}
        self.tests = {}
        self.practice_submissions = {}
        self.code_submissions = {}
        self.test_submissions = {}
        self.battle_rooms = {}
        self.notifications = {}
        self.follows = {}
        self.friend_requests = {}

data_store = DataStore()
