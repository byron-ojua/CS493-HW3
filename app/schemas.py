from marshmallow import Schema, fields, pre_dump
from datetime import datetime, timezone
from flask import url_for

KIND_BUSINESSES = 'businesses'
KIND_OWNERS = 'owners'
KIND_REVIEWS = 'reviews'
KIND_USERS = 'users'

TABLE_BUSINESSES = 'businesses'
TABLE_REVIEWS = 'reviews'

# Define the schema for the business entity
class Business(Schema):
    id = fields.Int(dump_only=True, attribute='business_id')
    owner_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=lambda x: len(x) <= 50)
    street_address = fields.Str(required=True, validate=lambda x: len(x) <= 100)
    city = fields.Str(required=True, validate=lambda x: len(x) <= 50)
    state = fields.Str(required=True, validate=lambda x: len(x) == 2)
    zip_code = fields.Int(required=True, validate=lambda x: len(str(x)) == 5)
    self = fields.Method("get_self", dump_only=True)

    def get_self(self, obj):
        # `obj` here is your dict with business_id in it
        return url_for('business.get_business',
                       business_id=obj['business_id'],
                       _external=True)

# Define the schema for the review entity
class Review(Schema):
    id = fields.Int(dump_only=True, attribute='review_id')
    user_id = fields.Int(required=True)
    business_id = fields.Int(required=True, load_only=True)
    business = fields.Method("get_business", dump_only=True)
    stars = fields.Int(required=True, validate=lambda x: 1 <= x <= 5)
    review_text = fields.Str(required=False, validate=lambda x: len(x) <= 1000)
    self = fields.Method("get_self", dump_only=True)

    def get_self(self, obj):
        # `obj` here is your dict with review_id in it
        return url_for('review.get_review',
                       review_id=obj['review_id'],
                       _external=True)
    
    def get_business(self, obj):
        # `obj` here is your dict with business_id in it
        return url_for('business.get_business',
                       business_id=obj['business_id'],
                       _external=True)