# app/business.py
from flask import Blueprint, request, jsonify, url_for, make_response, abort
import sqlalchemy
import logging
from .db_connector import get_db

from .schemas import Business

business_bp = Blueprint('business', __name__)
logger = logging.getLogger()

# get_businesses returns a list of all businesses
@business_bp.route('/', strict_slashes=False, methods=['GET'])
def get_businesses():
    # Check if the request has query parameters
    limit = request.args.get('limit', default=3, type=int)
    offset = request.args.get('offset', default=0, type=int)

    # Query the database for all businesses
    with get_db().connect() as conn:
        stmt_text = 'SELECT * FROM businesses limit :limit offset :offset'

        stmt = sqlalchemy.text(stmt_text)
        rows = conn.execute(stmt, parameters={'limit': limit, 'offset': offset})

    entries = [row._asdict() for row in rows]
    data = Business().dump(entries, many=True)

    payload = {
        'entries': data,
        'next': url_for('business.get_businesses', limit=limit, offset=offset + limit, _external=True).replace('/?', '?') if len(entries) == limit else None,
    }

    return payload, 200

# get_business returns a specific business by ID
@business_bp.route('/<int:business_id>', methods=['GET'])
def get_business(business_id):
    # Query the database for the business with the given ID
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM businesses WHERE business_id = :business_id')
        row = conn.execute(stmt, parameters={'business_id': business_id}).fetchone()
        if row is None:
            abort(404, description=f'No business with this business_id exists')
        business = row._asdict()
    
    payload = Business().dump(business)
    return jsonify(payload), 200

# create_business creates a new business
@business_bp.route('/', strict_slashes=False, methods=['POST'])
def create_business():
    # Validate the request data
    data = Business().load(request.get_json())

    # Create the business in the database
    with get_db().connect() as conn:
        stmt = sqlalchemy.text("""
            INSERT INTO businesses (owner_id, name, street_address, city, state, zip_code)
            VALUES (:owner_id, :name, :street_address, :city, :state, :zip_code)
        """)
        conn.execute(stmt, parameters=data)

        stmt = sqlalchemy.text('SELECT last_insert_id()')
        id = conn.execute(stmt).scalar()
        conn.commit()

    business = data.copy()
    business['business_id'] = id

    # Return the created business
    payload = Business().dump(business)
    res = make_response(jsonify(payload), 201)
    res.headers['Location'] = payload['self']
    return res

# update_business updates a specific business by ID
@business_bp.route('/<int:business_id>', methods=['PUT'])
def update_business(business_id):
    # Validate the request data
    data = Business().load(request.get_json())
    
    # Query the database for the business with the given ID
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM businesses WHERE business_id = :business_id')
        row = conn.execute(stmt, parameters={'business_id': business_id}).one_or_none()
        if row is None:
            abort(404, description=f'No business with this business_id exists')
        
        stmt = sqlalchemy.text("""
            UPDATE businesses
            SET owner_id = :owner_id,
                name = :name,
                street_address = :street_address,
                city = :city,
                state = :state,
                zip_code = :zip_code
            WHERE business_id = :business_id
        """)
        conn.execute(stmt, parameters={**data, 'business_id': business_id})
        conn.commit()
        business = data.copy()
        business['business_id'] = business_id

    # Return the updated business
    payload = Business().dump(business)
    return jsonify(payload), 200

# delete_business deletes a specific business by ID
@business_bp.route('/<int:business_id>', methods=['DELETE'])
def delete_business(business_id):
    # Query the database for the business with the given ID
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM businesses WHERE business_id = :business_id')
        row = conn.execute(stmt, parameters={'business_id': business_id}).fetchone()
        if row is None:
            abort(404, description=f'No business with this business_id exists')

        # Delete the business from the database
        stmt = sqlalchemy.text('DELETE FROM businesses WHERE business_id = :business_id')
        conn.execute(stmt, parameters={'business_id': business_id})
        conn.commit()

    # Return a success message
    return '', 204