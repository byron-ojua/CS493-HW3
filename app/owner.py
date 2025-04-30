from flask import Blueprint, request, jsonify, url_for
from marshmallow import ValidationError
from datetime import datetime, timezone
from .db_connector import get_db
import sqlalchemy
import logging


from .schemas import Business
logger = logging.getLogger()

owner_bp = Blueprint('owner', __name__)

# get_businesses_by_owner returns a list of businesses for a specific owner
@owner_bp.route('/<int:owner_id>/businesses', methods=['GET'])
def get_businesses_by_owner(owner_id):
    # Query the database for all businesses
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM businesses WHERE owner_id = :owner_id')
        rows = conn.execute(stmt, parameters={'owner_id': owner_id})
        
        entries = [row._asdict() for row in rows]

    payload = Business().dump(entries, many=True)
    
    return jsonify(payload), 200
