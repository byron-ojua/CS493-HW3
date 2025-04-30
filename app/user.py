from flask import Blueprint, request, jsonify, url_for
import sqlalchemy
import logging
from .db_connector import get_db
from marshmallow import ValidationError
from datetime import datetime, timezone

from .schemas import Review, KIND_REVIEWS

user_bp = Blueprint('user', __name__)

# get_reviews_by_user returns a list of reviews for a specific user
@user_bp.route('/<int:user_id>/reviews', methods=['GET'])
def get_reviews_by_user(user_id):
    # Query the database for all reviews
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM reviews WHERE user_id = :user_id')
        rows = conn.execute(stmt, parameters={'user_id': user_id})
        reviews = [row._asdict() for row in rows]
        
    payload = Review().dump(reviews, many=True)

    return jsonify(payload), 200