from flask_smorest import Blueprint
from flask import jsonify
from ..extentions.db import db
from ..extentions.redis_client import redis_client

health_bp = Blueprint("health", __name__, description="Health check endpoints")

startup_complete = False  # module-level flag

@health_bp.route("/startup")
def startup():
    return jsonify(status="UP" if startup_complete else "DOWN"), 200 if startup_complete else 503

@health_bp.route("/readiness")
def readiness():
    try:
        db.session.execute("SELECT 1")   # DB check
        redis_client.ping()              # Redis check
        return jsonify(status="UP"), 200
    except Exception as e:
        return jsonify(status="DOWN", error=str(e)), 503

@health_bp.route("/liveness")
def liveness():
    return jsonify(status="UP"), 200