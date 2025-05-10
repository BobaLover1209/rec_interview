from app import db
from datetime import datetime

# Association Tables
user_dietary_restrictions = db.Table(
    'user_dietary_restrictions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('restriction_id', db.Integer, db.ForeignKey('dietary_restrictions.id'), primary_key=True)
)

restaurant_endorsements = db.Table(
    'restaurant_endorsements',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('endorsement_id', db.Integer, db.ForeignKey('endorsements.id'), primary_key=True)
)

reservation_users = db.Table(
    'reservation_users',
    db.Column('reservation_id', db.Integer, db.ForeignKey('reservations.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

def get_current_time():
    """Get current UTC time."""
    return datetime.utcnow()

class User(db.Model):
    """User model representing restaurant customers."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dietary_restrictions = db.relationship(
        'DietaryRestriction',
        secondary=user_dietary_restrictions,
        backref='users',
        lazy=True
    )

class DietaryRestriction(db.Model):
    """Dietary restriction model for user preferences."""
    __tablename__ = 'dietary_restrictions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    restriction_type = db.Column(db.String(50), nullable=True)

class Restaurant(db.Model):
    """Restaurant model with tables and endorsements."""
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    tables = db.relationship('Table', backref='restaurant', lazy=True)
    endorsements = db.relationship(
        'Endorsement',
        secondary=restaurant_endorsements,
        backref='restaurants',
        lazy=True
    )

class Endorsement(db.Model):
    """Endorsement model for restaurant certifications."""
    __tablename__ = 'endorsements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    endorsement_type = db.Column(db.String(50), nullable=True)

class Table(db.Model):
    """Table model representing restaurant seating."""
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    reservations = db.relationship('Reservation', backref='table', lazy=True)

class Reservation(db.Model):
    """Reservation model for booking tables."""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    users = db.relationship(
        'User',
        secondary=reservation_users,
        backref='reservations',
        lazy=True
    )
    
    def __init__(self, table_id, datetime, additional_guests=0):
        """Initialize a new reservation."""
        self.table_id = table_id
        self.datetime = datetime
        self.additional_guests = additional_guests 