import os

API_BASE_URL = os.getenv("MYCHANCE_API_BASE_URL", "http://localhost:8080").rstrip("/")

# UUID fixo para protótipo do recrutador (mesmo seed do backend em dev)
DEFAULT_RECRUITER_ID = "11111111-1111-1111-1111-111111111111"
