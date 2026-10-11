import os

API_BASE_URL = os.getenv("MYCHANCE_API_BASE_URL", "http://localhost:8080").rstrip("/")
FIREBASE_API_KEY = os.getenv("MYCHANCE_FIREBASE_API_KEY", "").strip()
FIREBASE_PROJECT_ID = os.getenv("MYCHANCE_FIREBASE_PROJECT_ID", "").strip()
