import pytest
from app import create_app, db
from app.models import User, Restaurant, Table, Reservation, DietaryRestriction, Endorsement
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_test_data(app):
    with app.app_context():
        # Create dietary restrictions
        restrictions = ['Gluten Free', 'Vegetarian']
        for restriction in restrictions:
            db.session.add(DietaryRestriction(name=restriction))
            db.session.add(Endorsement(name=restriction))
        
        # Create test users
        user1 = User(name='Test User 1', email='test1@example.com')
        user2 = User(name='Test User 2', email='test2@example.com')
        db.session.add_all([user1, user2])
        db.session.commit()
        # Add dietary restrictions to users
        user1.dietary_restrictions.append(
            DietaryRestriction.query.filter_by(name='Gluten Free').first()
        )
        user2.dietary_restrictions.append(
            DietaryRestriction.query.filter_by(name='Vegetarian').first()
        )
        db.session.commit()
        # Create test restaurant
        restaurant = Restaurant(name='Test Restaurant', address='123 Test St')
        db.session.add(restaurant)
        db.session.commit()
        restaurant.endorsements.append(
            Endorsement.query.filter_by(name='Gluten Free').first()
        )
        restaurant.endorsements.append(
            Endorsement.query.filter_by(name='Vegetarian').first()
        )
        # Add tables
        table1 = Table(capacity=4)
        table2 = Table(capacity=6)
        restaurant.tables.extend([table1, table2])
        db.session.add(restaurant)
        db.session.commit()

def test_search_restaurants_success(client, init_test_data):
    response = client.get('/api/restaurants/search?user_ids=1,2&datetime=2024-03-20T19:30:00')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert data[0]['name'] == 'Test Restaurant'

def test_search_restaurants_missing_params(client, init_test_data):
    response = client.get('/api/restaurants/search')
    assert response.status_code == 400

def test_search_restaurants_invalid_datetime(client, init_test_data):
    response = client.get('/api/restaurants/search?user_ids=1,2&datetime=invalid')
    assert response.status_code == 400

def test_create_reservation_success(client, init_test_data):
    data = {
        'restaurant_id': 1,
        'user_ids': [1, 2],
        'datetime': '2024-03-20T19:30:00'
    }
    response = client.post('/api/reservations', json=data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['restaurant'] == 'Test Restaurant'
    assert len(data['users']) == 2

def test_create_reservation_missing_fields(client, init_test_data):
    response = client.post('/api/reservations', json={})
    assert response.status_code == 400

def test_create_reservation_invalid_datetime(client, init_test_data):
    data = {
        'restaurant_id': 1,
        'user_ids': [1, 2],
        'datetime': 'invalid'
    }
    response = client.post('/api/reservations', json=data)
    assert response.status_code == 400

def test_delete_reservation_success(client, init_test_data):
    data = {
        'restaurant_id': 1,
        'user_ids': [1, 2],
        'datetime': '2024-03-20T19:30:00'
    }
    response = client.post('/api/reservations', json=data)
    reservation_id = response.get_json()['id']
    response = client.delete(f'/api/reservations/{reservation_id}')
    assert response.status_code == 200

def test_delete_reservation_not_found(client, init_test_data):
    response = client.delete('/api/reservations/999')
    assert response.status_code == 404 