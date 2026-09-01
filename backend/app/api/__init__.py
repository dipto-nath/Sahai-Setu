"""
API Routes Package for SIH26093
"""

from app.api import auth, cases, dashboard, analysis, recommendations, audit_log, users

__all__ = [
    "auth",
    "cases",
    "dashboard",
    "analysis",
    "recommendations",
    "audit_log",
    "users"
]