from app import create_app, db
from app.models import User, Restaurant, Table, Reservation, DietaryRestriction, Endorsement

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create dietary restrictions
        restrictions = [
            'Gluten-Free-Friendly',
            'Vegetarian-Friendly',
            'Vegan-Friendly',
            'Paleo-Friendly',
            'Kosher-Friendly',
            'Halal-Friendly'
        ]
        
        for restriction in restrictions:
            if not DietaryRestriction.query.filter_by(name=restriction).first():
                db.session.add(DietaryRestriction(name=restriction))
        
        # Create endorsements
        endorsements = [
            'Vegan-Friendly',
            'Gluten-Free-Friendly',
            'Vegetarian-Friendly',
            'Paleo-Friendly',
            'Kosher-Friendly',
            'Halal-Friendly'
        ]
        
        for endorsement in endorsements:
            if not Endorsement.query.filter_by(name=endorsement).first():
                db.session.add(Endorsement(name=endorsement))
        
        db.session.commit()
        
        # Create sample users
        users = [
            {'name': 'John Doe', 'email': 'john@example.com', 'restrictions': ['Gluten-Free-Friendly']},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'restrictions': ['Vegetarian-Friendly', 'Vegan-Friendly']},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'restrictions': ['Paleo-Friendly']},
            {'name': 'Alice Brown', 'email': 'alice@example.com', 'restrictions': ['Kosher-Friendly']},
            {'name': 'Charlie Wilson', 'email': 'charlie@example.com', 'restrictions': ['Halal-Friendly']}
        ]
        
        for user_data in users:
            user = User(name=user_data['name'], email=user_data['email'])
            for restriction in user_data['restrictions']:
                dietary_restriction = DietaryRestriction.query.filter_by(name=restriction).first()
                if dietary_restriction:
                    user.dietary_restrictions.append(dietary_restriction)
            db.session.add(user)
        
        # Create sample restaurants
        restaurants = [
            {
                'name': 'Green Garden',
                'address': '123 Green St, City',
                'endorsements': ['Vegan-Friendly', 'Vegetarian-Friendly', 'Gluten-Free-Friendly'],
                'tables': [4, 6, 8]
            },
            {
                'name': 'Meat Lovers',
                'address': '456 Meat Ave, City',
                'endorsements': ['Paleo-Friendly'],
                'tables': [2, 4, 6, 8]
            },
            {
                'name': 'Global Cuisine',
                'address': '789 World Blvd, City',
                'endorsements': ['Kosher-Friendly', 'Halal-Friendly'],
                'tables': [2, 4, 6]
            }
        ]
        
        for restaurant_data in restaurants:
            restaurant = Restaurant(name=restaurant_data['name'], address=restaurant_data['address'])
            for endorsement in restaurant_data['endorsements']:
                end = Endorsement.query.filter_by(name=endorsement).first()
                if end:
                    restaurant.endorsements.append(end)
            
            for capacity in restaurant_data['tables']:
                table = Table(capacity=capacity)
                restaurant.tables.append(table)
            
            db.session.add(restaurant)
        
        db.session.commit()

if __name__ == '__main__':
    init_db() 