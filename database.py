from flask_mysqldb import MySQL

mysql = MySQL()  # Create MySQL instance

def init_mysql(app):
    """Initialize MySQL with app configuration."""
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'waste_management'
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"  # Enables dictionary cursor
    
    mysql.init_app(app)  # Bind MySQL to Flask app

def get_db():
    """Get MySQL connection instance."""
    return mysql.connection  # Return the connection object
