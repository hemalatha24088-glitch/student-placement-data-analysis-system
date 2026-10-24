"""
Rate Limiter instance for Student Placement Data Analysis System.
Protects authentication and submission endpoints against brute-force attacks.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300 per day", "100 per hour"],
    storage_uri="memory://"
)
