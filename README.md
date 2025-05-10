# Restaurant Booking API

A restaurant booking system that allows users to find and book restaurants based on dietary restrictions and table availability.

## Features

- Search for restaurants with available tables for a group
- Create reservations for groups
- Delete reservations
- Support for dietary restrictions
- Support for multiple users per reservation

## Tech Stack

- Backend: Flask (Python)
- Frontend: React
- Database: MySQL

## Setup Instructions 

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://root:@localhost/restaurant_booking
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the backend server:
```bash
export FLASK_APP=app
export FLASK_ENV=development
export DATABASE_URL=mysql+pymysql://root:@localhost/restaurant_booking
flask run
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## API Endpoints

### Search Restaurants
- `GET /api/restaurants/search`
  - Query parameters:
    - `user_ids`: List of user IDs
    - `datetime`: Reservation date and time
  - Returns: List of available restaurants matching criteria

### Create Reservation
- `POST /api/reservations`
  - Body:
    - `restaurant_id`: Restaurant ID
    - `user_ids`: List of user IDs
    - `datetime`: Reservation date and time
  - Returns: Created reservation details

### Delete Reservation
- `DELETE /api/reservations/<reservation_id>`
  - Returns: Success message

## Testing

Run backend tests:
```bash
pytest
``` 