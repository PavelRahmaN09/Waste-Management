from flask import Blueprint
from database import get_db

# Create a Blueprint for database routes
db_routes = Blueprint('db_routes', __name__)

@db_routes.route('/test_db')
def test_db_connection():
    """Test MySQL database connection."""
    try:
        cur = get_db().connection.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        return "Database Connected Successfully! ✅"
    except Exception as e:
        return f"Error Connecting to Database ❌: {str(e)}"
