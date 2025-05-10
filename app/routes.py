from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Restaurant, Table, Reservation, DietaryRestriction, Endorsement
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

def check_table_availability(table, reservation_time):
    """Check if a table is available at the given time."""
    return not Reservation.query.filter(
        and_(
            Reservation.table_id == table.id,
            or_(
                and_(
                    Reservation.datetime <= reservation_time,
                    Reservation.datetime + timedelta(hours=2) > reservation_time
                ),
                and_(
                    Reservation.datetime < reservation_time + timedelta(hours=2),
                    Reservation.datetime >= reservation_time
                )
            )
        )
    ).first()

def get_user_conflicts(user_ids, reservation_time):
    """Get any conflicting reservations for the given users."""
    user_overlapping = Reservation.query.join(
        Reservation.users
    ).filter(
        and_(
            User.id.in_(user_ids),
            or_(
                and_(
                    Reservation.datetime <= reservation_time,
                    Reservation.datetime + timedelta(hours=2) > reservation_time
                ),
                and_(
                    Reservation.datetime < reservation_time + timedelta(hours=2),
                    Reservation.datetime >= reservation_time
                )
            )
        )
    ).all()
    
    user_conflicts = {}
    for reservation in user_overlapping:
        for user in reservation.users:
            if user.id in user_ids:
                if user.id not in user_conflicts:
                    user_conflicts[user.id] = []
                user_conflicts[user.id].append({
                    'restaurant': reservation.table.restaurant.name,
                    'datetime': reservation.datetime.isoformat()
                })
    return user_conflicts

@main.route('/api/restaurants/search', methods=['GET'])
def search_restaurants():
    """Search for available restaurants based on user requirements."""
    try:
        # Get and validate query parameters
        user_ids_str = request.args.get('user_ids')
        datetime_str = request.args.get('datetime')
        
        logger.info(f"Search request received - user_ids: {user_ids_str}, datetime: {datetime_str}")
        
        if not user_ids_str:
            logger.warning("Missing user_ids parameter")
            return jsonify({'error': 'Missing required field: user_ids'}), 400
        if not datetime_str:
            logger.warning("Missing datetime parameter")
            return jsonify({'error': 'Missing required field: datetime'}), 400
            
        # Parse user IDs
        try:
            user_ids = [int(id.strip()) for id in user_ids_str.split(',')]
            logger.info(f"Parsed user IDs: {user_ids}")
        except ValueError:
            logger.error(f"Invalid user_ids format: {user_ids_str}")
            return jsonify({'error': 'Invalid user_ids format. Expected comma-separated numbers'}), 400
            
        reservation_time = datetime.fromisoformat(datetime_str)
        logger.info(f"Reservation time: {reservation_time}")
        
        # Get users and their dietary restrictions
        users = User.query.filter(User.id.in_(user_ids)).all()
        if len(users) != len(user_ids):
            logger.warning(f"Some users not found. Requested: {user_ids}, Found: {[u.id for u in users]}")
            return jsonify({'error': 'One or more users not found'}), 404
            
        # Get group dietary restrictions
        group_restrictions = set()
        for user in users:
            user_restrictions = [r.name for r in user.dietary_restrictions]
            group_restrictions.update(user_restrictions)
            logger.info(f"User {user.id} restrictions: {user_restrictions}")
            
        logger.info(f"Group restrictions: {group_restrictions}")
            
        # Find compatible restaurants
        compatible_restaurants = Restaurant.query.filter(
            Restaurant.endorsements.any(
                Endorsement.name.in_(group_restrictions)
            )
        ).all()
        
        logger.info(f"Found {len(compatible_restaurants)} compatible restaurants")
        
        # Check for available tables
        available_restaurants = []
        for restaurant in compatible_restaurants:
            logger.info(f"Checking restaurant: {restaurant.name}")
            available_tables = Table.query.filter(
                and_(
                    Table.restaurant_id == restaurant.id,
                    Table.capacity >= len(user_ids)
                )
            ).all()
            
            logger.info(f"Found {len(available_tables)} tables with sufficient capacity")
            
            for table in available_tables:
                if check_table_availability(table, reservation_time):
                    logger.info(f"Table {table.id} has no overlapping reservations")
                    user_conflicts = get_user_conflicts(user_ids, reservation_time)
                    
                    restaurant_data = {
                        'id': restaurant.id,
                        'name': restaurant.name,
                        'endorsements': [e.name for e in restaurant.endorsements],
                        'available_table': {
                            'id': table.id,
                            'capacity': table.capacity
                        }
                    }
                    
                    if user_conflicts:
                        logger.info(f"Restaurant {restaurant.name} has conflicts: {user_conflicts}")
                        restaurant_data['user_conflicts'] = user_conflicts
                    else:
                        logger.info(f"Restaurant {restaurant.name} is available for all users")
                    
                    available_restaurants.append(restaurant_data)
                    break
                else:
                    logger.info(f"Table {table.id} has overlapping reservation")
        
        logger.info(f"Returning {len(available_restaurants)} available restaurants")
        return jsonify(available_restaurants)
        
    except ValueError as e:
        logger.error(f"Invalid datetime format: {str(e)}")
        return jsonify({'error': 'Invalid datetime format'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@main.route('/api/reservations', methods=['POST'])
def create_reservation():
    """Create a new restaurant reservation."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['restaurant_id', 'user_ids', 'datetime']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Get and validate users
        users = User.query.filter(User.id.in_(data['user_ids'])).all()
        if len(users) != len(data['user_ids']):
            return jsonify({'error': 'One or more users not found'}), 404
            
        # Get and validate table
        table = Table.query.filter(
            and_(
                Table.restaurant_id == data['restaurant_id'],
                Table.capacity >= len(users)
            )
        ).first()
        
        if not table:
            return jsonify({'error': 'No suitable table found'}), 404
            
        # Create reservation
        reservation = Reservation(
            table_id=table.id,
            datetime=datetime.fromisoformat(data['datetime']),
            additional_guests=data.get('additional_guests', 0)
        )
        
        # Add users to reservation
        reservation.users = users
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'id': reservation.id,
            'restaurant': table.restaurant.name,
            'table': {
                'id': table.id,
                'capacity': table.capacity
            },
            'datetime': reservation.datetime.isoformat(),
            'users': [{'id': user.id, 'name': user.name} for user in users],
            'additional_guests': reservation.additional_guests
        }), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid datetime format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    """Delete an existing reservation."""
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
            
        db.session.delete(reservation)
        db.session.commit()
        
        return jsonify({'message': 'Reservation deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 