import datetime
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
import os
import os
from database import init_mysql, get_db  # Import database functions
from routes import db_routes  # Import the new test_db route
from flask_wtf import FlaskForm
from wtforms import SubmitField
import MySQLdb
from werkzeug.utils import secure_filename
import traceback
import csv
from io import StringIO
from datetime import datetime



app = Flask(__name__)

# Enable CSRF Protection
csrf = CSRFProtect(app)  # Define CSRF before using it

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           

app.secret_key = "waste_secret"

# Initialize MySQL from database.py
init_mysql(app)

# Register Blueprints
app.register_blueprint(db_routes)  # Now test_db is available

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class CSRFForm(FlaskForm):
    submit = SubmitField()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name', '')
            last_name = request.form.get('last_name')
            gender = request.form.get('gender')
            birthday = request.form.get('birthday')
            contact = request.form.get('contact')
            email = request.form.get('email')
            address = request.form.get('address')
            location = request.form.get('location', 'Unknown')
            longitude = request.form.get('longitude', '0.0')
            latitude = request.form.get('latitude', '0.0')
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get("role", "member")
            account_status = 'active'
            total_income = 0.00

            print(f"📌 Received Data: {first_name}, {last_name}, {email}, {username}, {longitude}, {latitude}")

            # Hash password using pbkdf2:sha256 (if not already hashed)
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Hash password
            hashed_password = generate_password_hash(password)

            # Handle file upload
            profile_pic = request.files.get('profile_pic')
            profile_pic_filename = None
            if profile_pic and allowed_file(profile_pic.filename):
                profile_pic_filename = f"{username}_{profile_pic.filename}"
                profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER"], profile_pic_filename))

            # Database Insertion using get_db()
            cur = get_db().cursor()  # Use the get_db() function
            cur.execute("""
                INSERT INTO users 
                (first_name, middle_name, last_name, role, gender, birthday, contact, email, address, location, longitude, latitude, username, password, profile_pic, account_status, total_income) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                first_name, middle_name, last_name, role, gender, birthday, contact, email, address, location, 
                float(longitude), float(latitude), username, hashed_password, profile_pic_filename, account_status, float(total_income)
            ))

            get_db().commit()
            cur.close()

            flash("✅ Registration successful!", "success")
            print("✅ Registration successful!")

            return redirect(url_for("login"))

        except Exception as e:
            get_db().rollback()
            print(f"❌ Registration failed: {str(e)}")  # Log the error
            flash(f"❌ Registration failed: {str(e)}", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"📌 Login request received for: {username}")

        cur = get_db().cursor()
        cur.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        print("🔍 Database user:", user)  # Debugging info

        if user:
            user_id, db_username, stored_hashed_password, role = user["id"], user["username"], user["password"], user["role"]

            print(f"🔑 Entered Password: {password}")
            print(f"🔒 Stored Hashed Password: {stored_hashed_password}")

            if check_password_hash(stored_hashed_password, password):
                session['user_id'] = user_id
                session['username'] = db_username
                session['role'] = role

                flash("✅ Login successful!", "success")
                
                return redirect(url_for('admin_Dashboard' if role == "admin" else 'member_Dashboard'))
            else:
                flash("❌ Incorrect password. Please try again.", "danger")
        else:
            flash("❌ User not found.", "danger")

    return render_template("login.html")


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user_role = session.get('role')

    if user_role == 'admin':
        return redirect(url_for('admin_Dashboard'))  # Note capital D
    elif user_role == 'member':
        return redirect(url_for('member_Dashboard'))  # Note capital D
    else:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))




@app.route('/member', methods=['GET', 'POST'])
def member_Dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get all garbage types with their sale prices
        cursor.execute("SELECT id, garbage_type, garbage_pic, sale_price FROM garbage_types")
        garbage_types = cursor.fetchall()
        
        # Calculate total income for the logged-in user
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as total_income 
            FROM garbage_collection 
            WHERE user_id = %s
        """, (session['user_id'],))
        total_income = cursor.fetchone()['total_income']
        
        # Get quantities for each garbage type for this user
        garbage_data = []
        for gt in garbage_types:
            cursor.execute("""
                SELECT COALESCE(SUM(quantity), 0) as total_quantity
                FROM garbage_collection 
                WHERE user_id = %s AND garbage_type_id = %s
            """, (session['user_id'], gt['id']))
            quantity = cursor.fetchone()['total_quantity']
            
            garbage_data.append({
                'id': gt['id'],
                'type': gt['garbage_type'],
                'image': gt['garbage_pic'],
                'price': gt['sale_price'],
                'quantity': quantity,
                'total': quantity * gt['sale_price']
            })
            
    except Exception as e:
        flash('Error loading dashboard data', 'danger')
        app.logger.error(f"Dashboard error: {str(e)}")
        garbage_data = []
        total_income = 0
    finally:
        cursor.close()

    return render_template(
        'member/member_Dashboard.html',
        garbage_data=garbage_data,
        total_income=total_income
    )


@app.route('/admin', methods=['GET', 'POST'])
def admin_Dashboard():
    # Authentication check
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    # Initialize default data with safe values
    data = {
        'recycling_centers': 0,
        'members': 0,
        'garbage_collected': 0,
        'total_income': 0.0,  # Initialize as float
        'active_centers': 0
    }
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get recycling centers count
        cursor.execute("SELECT COUNT(*) as cnt FROM recycling_centers")
        data['recycling_centers'] = cursor.fetchone()['cnt'] or 0
        
        # Get total income with proper NULL handling
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_income), 0) as income,
                COUNT(CASE WHEN total_income > 0 THEN 1 END) as active_count
            FROM recycling_centers
        """)
        result = cursor.fetchone()
        data['total_income'] = float(result['income']) if result['income'] is not None else 0.0
        data['active_centers'] = result['active_count'] or 0
        
        # Get members count
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'member'")
        data['members'] = cursor.fetchone()['count'] or 0
        
        # Get garbage collected
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM garbage_collection")
        data['garbage_collected'] = cursor.fetchone()['total'] or 0
        
    except Exception as e:
        flash('Database error', 'danger')
        app.logger.error(f"Admin dashboard error: {str(e)}")
    finally:
        if 'cursor' in locals(): cursor.close()
    
    return render_template('admin/admin_Dashboard.html', **data)



@app.route('/add_recycle_center', methods=['GET', 'POST'])
def add_recycle_center():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        email = request.form.get('email')
        total_income = float(request.form.get('total_income', 0))
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')

        if not all([name, address, contact, longitude, latitude]):
            flash("Please fill all required fields", "danger")
            return redirect(url_for("add_recycle_center"))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO recycling_centers 
                (name, address, contact, email, total_income, longitude, latitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, address, contact, email, total_income, longitude, latitude))
            db.commit()
            flash("Recycling center added successfully!", "success")
            return redirect(url_for("admin_Dashboard"))
        except Exception as e:
            db.rollback()
            flash(f"Error adding recycling center: {str(e)}", "danger")
        finally:
            cursor.close()

    return render_template('admin/admin_recycling_center.html')



@app.route('/update_collection_status/<int:record_id>', methods=['POST'])
def update_collection_status(record_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    new_status = request.form.get('status')
    print(f"Status update request - Status: {new_status}, Record ID: {record_id}")

    if new_status not in ['0', '1', '2']:
        flash("Invalid status value", "danger")
        return redirect(url_for("collection_req"))

    db = get_db()
    cursor = db.cursor()
    try:
        # Verify record exists
        cursor.execute("SELECT id FROM garbage_collection WHERE id = %s", (record_id,))
        if not cursor.fetchone():
            flash("Record not found", "danger")
            return redirect(url_for("collection_req"))

        # Update status
        cursor.execute("""
            UPDATE garbage_collection 
            SET picked_up_status = %s 
            WHERE id = %s
        """, (int(new_status), record_id))

        # Process financial updates for Accepted status
        if new_status == '1':
            # Get financial data with error handling
            cursor.execute("""
                SELECT 
                    gc.total_amount, 
                    gc.center_id,
                    MONTH(gc.date) as month_num, 
                    YEAR(gc.date) as year,
                    gt.id as garbage_type_id
                FROM garbage_collection gc
                JOIN garbage_types gt ON gc.garbage_type_id = gt.id
                WHERE gc.id = %s
            """, (record_id,))
            financial_data = cursor.fetchone()
            


            if not financial_data:
                flash("Could not load financial data for record", "warning")
            else:
                print(f"Financial data: {financial_data}")  # Debug
                
                # Update monthly sales
                month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                             'july', 'august', 'september', 'october', 'november', 'december']
                month_field = month_names[financial_data['month_num'] - 1]
                
                cursor.execute(f"""
                    INSERT INTO monthly_sales 
                    (center_id, garbage_type_id, yearly_sales, {month_field}, total_sales)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    {month_field} = {month_field} + VALUES({month_field}),
                    total_sales = total_sales + VALUES(total_sales)
                """, (
                    financial_data['center_id'], 
                    financial_data['garbage_type_id'],
                    financial_data['year'],
                    financial_data['total_amount'],
                    financial_data['total_amount']
                ))
                
                # DEBUG: Print before center update
                cursor.execute("SELECT total_income FROM recycling_centers WHERE id = %s", 
                             (financial_data['center_id'],))
                before_update = cursor.fetchone()
                print(f"Before update - Center {financial_data['center_id']} total_income: {before_update['total_income']}")
                
                # Update recycling center total income
                rows_updated = cursor.execute("""
                    UPDATE recycling_centers 
                    SET total_income = total_income + %s
                    WHERE id = %s
                """, (financial_data['total_amount'], financial_data['center_id']))
                
                print(f"Rows updated in recycling_centers: {rows_updated}")  # Debug
                
                # DEBUG: Print after center update
                cursor.execute("SELECT total_income FROM recycling_centers WHERE id = %s", 
                             (financial_data['center_id'],))
                after_update = cursor.fetchone()
                print(f"After update - Center {financial_data['center_id']} total_income: {after_update['total_income']}")

        db.commit()
        flash(f"Status updated to {'Accepted' if new_status == '1' else 'Rejected' if new_status == '2' else 'Pending'} successfully", "success")
    except Exception as e:
        db.rollback()
        flash(f"Database error: {str(e)}", "danger")
        print(f"Error details: {str(e)}")  # Detailed error logging
    finally:
        cursor.close()
    
    return redirect(url_for("collection_req"))



# Delete Collection Record
@app.route('/delete_collection/<int:record_id>', methods=['POST'])
def delete_collection(record_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    try:
        # First get the record to get the image filename
        cursor.execute("SELECT garbage_pic FROM garbage_collection WHERE id = %s", (record_id,))
        record = cursor.fetchone()
        
        if not record:
            flash("Record not found", "danger")
            return redirect(url_for("collection_req"))
        
        # Delete the record
        cursor.execute("DELETE FROM garbage_collection WHERE id = %s", (record_id,))
        db.commit()
        
        # Delete the associated image file (if not default.jpg)
        if record['garbage_pic'] and record['garbage_pic'] != 'default.jpg':
            try:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], record['garbage_pic'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                app.logger.error(f"Error deleting image file: {str(e)}")
        
        flash("Record deleted successfully", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting record: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for("collection_req"))



@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route('/admin/member', methods=['GET'])
def member():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, first_name, contact, email, address, username, total_income, account_status FROM users")
    
    # Fetch all rows as a list of dictionaries
    rows = cursor.fetchall()
    
    # Debugging: Print rows to check their structure
    print(f"Fetched rows: {rows}")
    
    # Check if there are rows to process
    if rows:
        members = [
            {
                "id": row['id'],
                "first_name": row['first_name'],
                "contact": row['contact'],
                "email": row['email'],
                "address": row['address'],
                "username": row['username'],
                "total_income": row['total_income'],
                "account_status": row['account_status']
            }
            for row in rows
        ]
    else:
        members = []

    cursor.close()

    form = CSRFForm()  # Instantiate the form to pass to the template
    return render_template('admin/member.html', members=members, form=form)


@app.route('/admin/member/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    print("Received member_id:", member_id)
    
    db = get_db()
    cursor = db.cursor()

    # Deleting the member from the database
    cursor.execute("DELETE FROM users WHERE id = %s", (member_id,))
    db.commit()

    cursor.close()
    return redirect(url_for('member'))  # Redirect back to the members list


@app.route('/admin/member/edit/<int:member_id>', methods=['POST'])
def edit_member(member_id):
    account_status = request.form.get('account_status')

    print("Received member_id:", member_id)
    print("Received account_status:", account_status)
    
    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE users SET account_status = %s WHERE id = %s", (account_status, member_id))
    db.commit()

    cursor.close()
    return redirect(url_for('member'))  # Redirect back to the members list


@app.route('/admin/recycling-center', methods=['GET', 'POST'])
def admin_recycling_center():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, name, address, contact, email, total_income FROM recycling_centers")
    
    # Fetch all rows as a list of dictionaries
    rows = cursor.fetchall()
    
    # Check if there are rows to process
    if rows:
        recycle_centers = [
            {
                "id": row['id'],
                "name": row['name'],
                "address": row['address'],
                "contact": row['contact'],
                "email": row['email'],
                "total_income": row['total_income'],
            }
            for row in rows
        ]
    else:
        recycle_centers = []

    cursor.close()

    form = CSRFForm()  # Instantiate the form to pass to the template
    return render_template('admin/admin_recycling_center.html', recycle_centers=recycle_centers, form=form)


@app.route('/admin/recycle_center/edit/<int:recycle_center_id>', methods=['POST'])
def edit_recycle_center(recycle_center_id):
    name = request.form.get('name')
    address = request.form.get('address')
    contact = request.form.get('contact')
    email = request.form.get('email')
    total_income = request.form.get('total_income')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # print("Received data ------------- :", recycle_center_id, name, address, contact, email, total_income, latitude, longitude)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE recycling_centers 
        SET name = %s, address = %s, contact = %s, email = %s, 
            total_income = %s, latitude = %s, longitude = %s 
        WHERE id = %s
    """, (name, address, contact, email, total_income, latitude, longitude, recycle_center_id))

    db.commit()
    cursor.close()

    flash("Recycle center updated successfully!", "success")
    return redirect(url_for('admin_recycling_center'))  # Redirect back to the list


@app.route('/admin/recycling-center/delete/<int:recycle_center_id>', methods=['POST', 'GET'])
def delete_admin_recycle_center(recycle_center_id):

    db = get_db()
    cursor = db.cursor()

    try:
        center_id = recycle_center_id
        id = recycle_center_id
        
        print("Received center_id:", center_id, id)

        # Delete records in monthly_sales that reference garbage_collection
        cursor.execute("DELETE FROM monthly_sales WHERE garbage_type_id IN (SELECT id FROM garbage_collection WHERE center_id = %s)", (center_id,))
        
        # Delete records in garbage_collection that reference recycling_centers
        cursor.execute("DELETE FROM garbage_collection WHERE center_id = %s", (center_id,))
        
        # Now delete the recycle center
        cursor.execute("DELETE FROM recycling_centers WHERE id = %s", (id,))
        
        db.commit()
        print(f"Recycle center with ID {center_id} deleted successfully.")
    
    except Exception as e:
        db.rollback()
        print("Error:", e)
    
    finally:
        cursor.close()

    return redirect(url_for('admin_recycling_center'))  # Redirect back to the list of recycling centers


@app.route('/admin/income-report', methods=['GET'])
def reports():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, name, address, total_income FROM recycling_centers")
    
    # Fetch all rows as a list of dictionaries
    rows = cursor.fetchall()
    
    # Debugging: Print rows to check their structure
    print(f"Fetched rows: {rows}")
    
    # Check if there are rows to process
    if rows:
        recycling_centers = [
            {
                "id": row['id'],
                "name": row['name'],
                "address": row['address'],
                "total_income": row['total_income'],
            }
            for row in rows
        ]
    else:
        recycling_centers = []

    cursor.close()

    return render_template('admin/income_report.html', recycling_centers=recycling_centers)


@app.route('/admin/garbage-type-report', methods=['GET', 'POST'])
def garbage_type_report_page():  
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT ms.id, ms.center_id, gt.garbage_type, 
           ms.january, ms.february, ms.march, ms.april, ms.may, ms.june, 
           ms.july, ms.august, ms.september, ms.october, ms.november, ms.december, 
           ms.total_sales, ms.yearly_sales
    FROM monthly_sales ms
    JOIN garbage_types gt ON ms.garbage_type_id = gt.id
    ORDER BY gt.garbage_type
""")

# JOIN garbage_collection gt ON ms.garbage_type_id = gt.id
    rows = cursor.fetchall()

    monthly_sales = [
        {
            "id": row['id'],
            "center_id": row['center_id'],
            "garbage_type": row['garbage_type'],  # Correct garbage type name
            "january": row['january'],
            "february": row['february'],
            "march": row['march'],
            "april": row['april'],
            "may": row['may'],
            "june": row['june'],
            "july": row['july'],
            "august": row['august'],
            "september": row['september'],
            "october": row['october'],
            "november": row['november'],
            "december": row['december'],
            "total_sales": row['total_sales'],
            "yearly_sales": row['yearly_sales'],
            "data": [
                row['january'], row['february'], row['march'], row['april'], 
                row['may'], row['june'], row['july'], row['august'], 
                row['september'], row['october'], row['november'], row['december']
            ],
        }
        for row in rows
    ]

    cursor.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(monthly_sales)  # Return JSON data if requested via AJAX

    return render_template('admin/garbage-type-report.html', monthly_sales=monthly_sales)



@app.route('/admin/collection_req', methods=['GET', 'POST'])
def collection_req():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)  # Ensure dictionary-style results

    try:
        # Corrected SQL Query with JOIN to garbage_types table
        cursor.execute("""
            SELECT 
                gc.id, 
                gc.center_id, 
                rc.name AS center_name,
                gc.user_id, 
                gt.garbage_type,  # Get the name from garbage_types table
                gc.quantity, 
                gt.sale_price as per_kg,  # Assuming sale_price is per_kg
                gc.total_amount, 
                gc.date, 
                gc.garbage_pic, 
                gc.picked_up_status, 
                gc.latitude, 
                gc.longitude
            FROM garbage_collection gc
            JOIN garbage_types gt ON gc.garbage_type_id = gt.id
            JOIN recycling_centers rc ON gc.center_id = rc.id
            ORDER BY gc.date DESC
        """)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Process records
        records = [
            {
                "id": row['id'],
                "center_name": row['center_name'],
                "user_id": row['user_id'],
                "garbage_type": row['garbage_type'],  # Now using the joined name
                "sale_price": row['per_kg'],  # Using the joined sale_price
                "quantity": row['quantity'],
                "per_kg": row['per_kg'],
                "total_amount": row['total_amount'],
                "date": row['date'].strftime('%Y-%m-%d') if row['date'] else None,
                "garbage_pic": row['garbage_pic'],
                "picked_up_status": row['picked_up_status'],
                "latitude": row['latitude'],
                "longitude": row['longitude']
            }
            for row in rows
        ] if rows else []

        return render_template('/admin/collection_req.html', records=records, form=CSRFForm())

    except Exception as e:
        print(f"Database error: {str(e)}")
        return render_template('error.html', error="Failed to load collection requests"), 500
        
    finally:
        cursor.close()


@app.route('/admin/garbage-type-report', methods=['GET', 'POST'])
def garbage_type_report():
    return render_template('admin/garbage-type-report.html')



# Download As CSV file
@app.route('/admin/download-monthly-sales-csv')
def download_monthly_sales_csv():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    
    # Query to get monthly sales with center and garbage type names
    cursor.execute("""
        SELECT 
            ms.*,
            rc.name as center_name,
            gt.garbage_type
        FROM monthly_sales ms
        JOIN recycling_centers rc ON ms.center_id = rc.id
        JOIN garbage_types gt ON ms.garbage_type_id = gt.id
        ORDER BY gt.garbage_type, rc.name
    """)
    monthly_sales = cursor.fetchall()
    cursor.close()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'Center Name', 'Garbage Type', 
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
        'Total Sales', 'Yearly Sales'
    ])
    
    # Write data rows
    for sale in monthly_sales:
        # Calculate totals if they're 0 in database (as per your sample data)
        monthly_totals = [
            sale['january'], sale['february'], sale['march'], sale['april'],
            sale['may'], sale['june'], sale['july'], sale['august'],
            sale['september'], sale['october'], sale['november'], sale['december']
        ]
        total_sales = sale['total_sales'] if sale['total_sales'] else sum(monthly_totals)
        yearly_sales = sale['yearly_sales'] if sale['yearly_sales'] else sum(monthly_totals)
        
        writer.writerow([
            sale['center_name'],
            sale['garbage_type'],
            *monthly_totals,  # Unpack monthly values
            total_sales,
            yearly_sales
        ])
    
    # Create response with timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=monthly_sales_report_{timestamp}.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


@app.route('/admin/garbage-type', methods=['GET', 'POST'])
def garbage_type():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get all garbage types with their sale prices and images
        cursor.execute("SELECT id, garbage_type, sale_price, garbage_pic FROM garbage_types ORDER BY sale_price ASC")
        garbage_types = cursor.fetchall()
        
        # Prepare garbage data
        garbage_data = []
        for gt in garbage_types:
            garbage_data.append({
                'id': gt['id'],
                'type': gt['garbage_type'],
                'price': gt['sale_price'],
                'image': gt['garbage_pic']
            })
            
    except Exception as e:
        flash('Error loading garbage types', 'danger')
        app.logger.error(f"Garbage type error: {str(e)}")
        garbage_data = []
    finally:
        cursor.close()

    return render_template('admin/garbage-type.html', garbage_data=garbage_data)


# from admin dashboard add-garbage-type
@app.route('/admin/add-garbage-type', methods=['GET', 'POST'])
def add_garbage_type():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'garbage_pic' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['garbage_pic']
        garbage_type = request.form.get('garbage_type')
        sale_price = request.form.get('sale_price')
        
        if not all([garbage_type, sale_price]):
            flash('Please fill all required fields', 'danger')
            return redirect(request.url)
        
        try:
            sale_price = float(sale_price)
        except ValueError:
            flash('Invalid price format', 'danger')
            return redirect(request.url)
        
        # Handle file upload with default.jpg fallback
        filename = 'default.jpg'  # Default image
        if file.filename != '' and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'garbage_types')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
        
        # Save to database
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO garbage_types (garbage_type, sale_price, garbage_pic)
                VALUES (%s, %s, %s)
            """, (garbage_type, sale_price, filename))
            db.commit()
            # flash('Garbage type added successfully!', 'success')
            return redirect(url_for('garbage_type'))
        except Exception as e:
            db.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(request.url)
        finally:
            cursor.close()
    
    return render_template('admin/add-garbage-type.html')


@app.route('/admin/delete-garbage-type/<int:garbage_id>', methods=['POST'])
def delete_garbage_type(garbage_id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # First get the garbage type to get the image filename
        cursor.execute("SELECT garbage_pic FROM garbage_types WHERE id = %s", (garbage_id,))
        garbage = cursor.fetchone()
        
        if not garbage:
            flash('Garbage type not found', 'danger')
            return redirect(url_for('garbage_type'))
        
        # Delete the garbage type
        cursor.execute("DELETE FROM garbage_types WHERE id = %s", (garbage_id,))
        db.commit()
        
        # Delete the associated image file (if not default.jpg)
        if garbage['garbage_pic'] and garbage['garbage_pic'] != 'default.jpg':
            try:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'garbage_types', garbage['garbage_pic'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                app.logger.error(f"Error deleting image file: {str(e)}")
        
        # flash('Garbage type deleted successfully', 'success')
        return redirect(url_for('garbage_type'))
    
    except Exception as e:
        db.rollback()
        flash(f'Error deleting garbage type: {str(e)}', 'danger')
        return redirect(url_for('garbage_type'))
    finally:
        cursor.close()


@app.route('/admin/income-report', methods=['GET', 'POST'])
def income_report():
    return render_template('admin/income_report.html')




# members recycle_center
@app.route('/member/recycle-center', methods=['GET'])
def member_recycling_center():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, name, address, contact, email, total_income FROM recycling_centers")
    
    # Fetch all rows as a list of dictionaries
    rows = cursor.fetchall()
    
    # Check if there are rows to process
    if rows:
        member_recycle_centers = [
            {
                "id": row['id'],
                "name": row['name'],
                "address": row['address'],
                "contact": row['contact'],
                "email": row['email'],
                "total_income": row['total_income'],
            }
            for row in rows
        ]
    else:
        member_recycle_centers = []

    cursor.close()

    form = CSRFForm()  # Instantiate the form to pass to the template
    return render_template('member/recycle-center.html', member_recycle_centers=member_recycle_centers, form=form)



@app.route('/member/records', methods=['GET', 'POST'])
def records():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch records with center names (as before)
    cursor.execute("""
        SELECT gc.id, rc.name AS center_name, gt.garbage_type, 
               gc.sale_price, gc.quantity, gc.total_amount, 
               gc.date, gc.garbage_pic, gc.picked_up_status, 
               gc.latitude, gc.longitude 
        FROM garbage_collection gc
        JOIN garbage_types gt ON gc.garbage_type_id = gt.id
        JOIN recycling_centers rc ON gc.center_id = rc.id
        WHERE gc.user_id = %s
    """, (user_id,))
    rows = cursor.fetchall()
    
    # Fetch all garbage types (for the first dropdown)
    cursor.execute("SELECT id, garbage_type, sale_price FROM garbage_types")
    garbage_types = cursor.fetchall()
    
    # NEW: Fetch all recycling centers (for the second dropdown)
    cursor.execute("SELECT id, name AS center_name FROM recycling_centers")
    recycling_centers = cursor.fetchall()

    # Process records (as before)
    records = []
    for row in rows:
        records.append({
            "id": row["id"],
            "center_name": row["center_name"],
            "garbage_type": row["garbage_type"],
            "quantity": row["quantity"],
            "sale_price": row["sale_price"],
            "total_amount": float(row["total_amount"]) if row["total_amount"] else 0.0,
            "date": row["date"].strftime("%Y-%m-%d") if row["date"] else None,
            "garbage_pic": row["garbage_pic"],
            "picked_up_status": row["picked_up_status"],
            "latitude": float(row["latitude"]) if row["latitude"] is not None else 0.0,
            "longitude": float(row["longitude"]) if row["longitude"] is not None else 0.0
        })

    cursor.close()
    
    print("records", records)

    form = CSRFForm()
    return render_template('member/records.html', 
                         garbage_types=garbage_types,
                         recycling_centers=recycling_centers,  # Pass centers to template
                         records=records, 
                         form=form)



@app.route('/member/records/add', methods=['POST'])
def add_collection_req():
    # Get form data
    center_id = request.form.get('center_id')
    garbage_type = request.form.get('garbage_type')
    sale_price = request.form.get('sale_price')
    quantity = request.form.get('quantity')
    date = request.form.get('date')
    longitude = request.form.get('longitude')
    latitude = request.form.get('latitude')
    file = request.files.get('garbage_pic')

    filename = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/uploads', filename))

    # Save to database (pseudo code)
    # db.insert(center_id, garbage_type, sale_price, quantity, date, longitude, latitude, filename)

    flash('Collection record added!', 'success')
    return redirect(url_for('member_records'))


# Edit Record - POST (Update data)
@app.route('/member/records/edit/<int:record_id>', methods=['POST', 'UPDATE'])
def update_record(record_id):
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Please login first"}), 401
        
        print("record_id ---------- ", record_id)

        # Get form data
        center_id = request.form.get('center_id')  # Added center_id
        garbage_type_id = request.form.get('garbage_type')
        quantity = request.form.get('quantity')
        sale_price = request.form.get('sale_price')
        date = request.form.get('date')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        garbage_pic = request.files.get('garbage_pic')
        
        if not sale_price:
            return jsonify({"error": "Missing required fields", "missing_fields": ["sale_price"]})

        # print("Received data ----------------- ", {
        #     'center_id': center_id,  # Added to debug print
        #     'garbage_type_id': garbage_type_id,
        #     'quantity': quantity,
        #     'sale_price': sale_price,
        #     'date': date,
        #     'latitude': latitude,
        #     'longitude': longitude,
        #     'file_uploaded': garbage_pic.filename if garbage_pic else False
        # })
        
        # Validate required fields
        required_fields = {
            'center_id': center_id,  # Added center_id
            'garbage_type': garbage_type_id,
            'quantity': quantity,
            'sale_price': sale_price,
            'date': date,
            'latitude': latitude,
            'longitude': longitude
        }
        
        if not all(required_fields.values()):
            missing = [k for k, v in required_fields.items() if not v]
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing
            }), 400

        # Convert to proper data types
        try:
            quantity = float(quantity)
            sale_price = float(sale_price)
            total_amount = quantity * sale_price
        except ValueError:
            return jsonify({
                "error": "Invalid quantity or price format"
            }), 400

        # Handle file upload
        pic_filename = None
        if garbage_pic and garbage_pic.filename:
            if not allowed_file(garbage_pic.filename):
                return jsonify({"error": "Invalid file type"}), 400
            pic_filename = secure_filename(f"{record_id}_{garbage_pic.filename}")
            garbage_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))

        db = get_db()
        cursor = db.cursor()
        try:
            # Build the base query
            query = """
                UPDATE garbage_collection 
                SET center_id = %s,
                    garbage_type_id = %s,
                    quantity = %s,
                    sale_price = %s,
                    total_amount = %s,
                    date = %s,
                    latitude = %s,
                    longitude = %s
            """
            params = [
                center_id,  # Added center_id
                garbage_type_id,
                quantity,
                sale_price,
                total_amount,
                date,
                latitude,
                longitude
            ]
            
            # Conditionally add garbage_pic if uploaded
            if pic_filename:
                query += ", garbage_pic = %s"
                params.append(pic_filename)
            
            # Add WHERE clause
            query += " WHERE id = %s AND user_id = %s"
            params.extend([record_id, session['user_id']])
            
            cursor.execute(query, params)
            db.commit()
            return redirect(url_for('records'))
            
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/member/records/delete/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Please login first"}), 401

        db = get_db()
        cursor = db.cursor()
        try:
            # Verify record ownership
            cursor.execute("""
                SELECT garbage_pic FROM garbage_collection 
                WHERE id = %s AND user_id = %s
            """, (record_id, session['user_id']))
            
            record = cursor.fetchone()
            if not record:
                return jsonify({"error": "Record not found"}), 404
            
            # First delete related records in monthly_sales
            cursor.execute("""
                DELETE FROM monthly_sales 
                WHERE garbage_type_id = %s
            """, (record_id,))
            
            # Then delete the main record
            cursor.execute("""
                DELETE FROM garbage_collection 
                WHERE id = %s AND user_id = %s
            """, (record_id, session['user_id']))
            
            db.commit()
            
            # Delete associated image file
            if record['garbage_pic'] and record['garbage_pic'] != 'default.jpg':
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], record['garbage_pic']))
                except Exception as e:
                    app.logger.error(f"Error deleting file: {str(e)}")
            
            return jsonify({
                "success": True, 
                "message": "Record deleted successfully"
            })
            
        except Exception as e:
            db.rollback()
            app.logger.error(f"Database error: {str(e)}")
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            cursor.close()

    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Server error occurred"}), 500




@app.route('/member/recycle-center', methods=['GET', 'POST'])
def recycle_center():
    return render_template('member/recycle-center.html')



if __name__ == '__main__':
    app.run(debug=True)
