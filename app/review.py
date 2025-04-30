from flask import Blueprint, request, jsonify, url_for, make_response, abort
import sqlalchemy
import logging
from .db_connector import get_db

from .schemas import Review, KIND_REVIEWS, KIND_BUSINESSES

review_bp = Blueprint('review', __name__)
logger = logging.getLogger()

# get_review returns a specific review by ID
@review_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    # Query the database for the review with the given ID
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM reviews WHERE review_id = :review_id')
        row = conn.execute(stmt, parameters={'review_id': review_id}).one_or_none()
        if row is None:
            abort(404, description=f'No review with this review_id exists')
        review = row._asdict()

    # Serialize the review data
    payload = Review().dump(review)
    return jsonify(payload), 200

# create_review creates a new review
@review_bp.route('/', methods=['POST'])
def create_review():
    data = Review().load(request.get_json())

    # Check if business_id is valid
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM businesses WHERE business_id = :business_id')
        row = conn.execute(stmt, parameters={'business_id': data.get('business_id')}).one_or_none()
        if row is None:
            abort(404, description=f'No business with this business_id exists')

    # Check if the review already exists
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM reviews WHERE user_id = :user_id AND business_id = :business_id')
        existing_reviews = conn.execute(stmt, parameters={'user_id': data.get('user_id'), 'business_id': data.get('business_id')}).one_or_none()
    if existing_reviews is not None:
        abort(409, description='You have already submitted a review for this business. You can update your previous review, or delete it and submit a new review')

    # Create a new review entry
    with get_db().connect() as conn:
        stmt = sqlalchemy.text("""
            INSERT INTO reviews (user_id, business_id, stars, review_text)
            VALUES (:user_id, :business_id, :stars, :review_text)
        """)
        if data.get('review_text') is None:
            data['review_text'] = ''

        conn.execute(stmt, parameters=data)

        stmt = sqlalchemy.text('SELECT last_insert_id()')
        id = conn.execute(stmt).scalar()
        conn.commit() 

    review = data.copy()
    review['review_id'] = id

    # Return the created review
    payload = Review().dump(review)
    res = make_response(jsonify(payload), 201)
    res.headers['Location'] = payload['self']
    return res
    
# update_review updates a specific review by ID
@review_bp.route('/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    # Validate the request data
    data = Review().load(request.get_json(), partial=('user_id', 'business_id'))

    # Query the database for the review with the given ID
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM reviews WHERE review_id = :review_id')
        row = conn.execute(stmt, parameters={'review_id': review_id}).one_or_none()
        if row is None:
            abort(404, description=f'No review with this review_id exists')

        review = row._asdict()

        # Update the review entity
        if data.get('review_text') is None and review.get('review_text') is not None:
            data['review_text'] = review['review_text']
        if data.get('review_text') is None:
            data['review_text'] = ''

        stmt = sqlalchemy.text("""
            UPDATE reviews
            SET stars = :stars,
                review_text = :review_text
            WHERE review_id = :review_id
        """)
        conn.execute(stmt, parameters={**data, 'review_id': review_id})
        conn.commit()

        review.update(data)

    # Return the updated review
    payload = Review().dump(review)
    return jsonify(payload), 200

# delete_review deletes a specific review by ID
@review_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    # Query the database for the review with the given ID
    with get_db().connect() as conn:
        stmt = sqlalchemy.text('SELECT * FROM reviews WHERE review_id = :review_id')
        row = conn.execute(stmt, parameters={'review_id': review_id}).one_or_none()
        if row is None:
            abort(404, description=f'No review with this review_id exists')

        # Delete the review from the database
        stmt = sqlalchemy.text('DELETE FROM reviews WHERE review_id = :review_id')
        conn.execute(stmt, parameters={'review_id': review_id})
        conn.commit()

    return '', 204