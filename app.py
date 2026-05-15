from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'ebmssecretkey'

# MYSQL CONFIG

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_DB'] = 'ebms'

mysql = MySQL(app)

# HOME PAGE

@app.route('/')
def home():
    return render_template('index.html')

# USER REGISTER

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # AUTO GENERATE METER NUMBER

        cur.execute("SELECT COUNT(*) FROM consumer")
        count = cur.fetchone()[0]

        meter_number = f"EBMS{1000 + count + 1}"

        cur.execute("""
        INSERT INTO consumer
        (full_name, email, phone, address, meter_number, password)
        VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            full_name,
            email,
            phone,
            address,
            meter_number,
            password
        ))

        mysql.connection.commit()

        return redirect('/login')

    return render_template('register.html')

# USER LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("""
        SELECT * FROM consumer
        WHERE email=%s AND password=%s
        """, (email, password))

        user = cur.fetchone()

        if user:

            session['consumer_id'] = user[0]
            session['full_name'] = user[1]

            return redirect('/user_dashboard')

    return render_template('login.html')

# FORGOT PASSWORD

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']
        new_password = request.form['new_password']

        cur = mysql.connection.cursor()

        cur.execute("""
        UPDATE consumer
        SET password=%s
        WHERE email=%s
        """, (new_password, email))

        mysql.connection.commit()

        return redirect('/login')

    return render_template('forgot_password.html')

# USER DASHBOARD

@app.route('/user_dashboard')
def user_dashboard():

    if 'consumer_id' not in session:
        return redirect('/login')

    consumer_id = session['consumer_id']

    cur = mysql.connection.cursor()

    # FETCH BILLS

    cur.execute("""
    SELECT * FROM bill
    WHERE consumer_id=%s
    """, (consumer_id,))

    bills = cur.fetchall()

    # FETCH COMPLAINTS

    cur.execute("""
    SELECT * FROM complaint
    WHERE consumer_id=%s
    """, (consumer_id,))

    complaints = cur.fetchall()

    return render_template(
        'user_dashboard.html',
        bills=bills,
        complaints=complaints,
        name=session['full_name']
    )

# ADD COMPLAINT

@app.route('/add_complaint', methods=['POST'])
def add_complaint():

    if 'consumer_id' not in session:
        return redirect('/login')

    description = request.form['description']

    consumer_id = session['consumer_id']

    cur = mysql.connection.cursor()

    cur.execute("""
    INSERT INTO complaint
    (consumer_id, description, complaint_status)
    VALUES (%s,%s,%s)
    """, (
        consumer_id,
        description,
        'Unsolved'
    ))

    mysql.connection.commit()

    return redirect('/user_dashboard')

# PAY BILL

@app.route('/pay_bill/<int:bill_id>')
def pay_bill(bill_id):

    cur = mysql.connection.cursor()

    cur.execute("""
    UPDATE bill
    SET bill_status='Paid'
    WHERE bill_id=%s
    """, (bill_id,))

    mysql.connection.commit()

    return redirect('/user_dashboard')

# ADMIN LOGIN

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':

        admin_email = 'admin@gmail.com'
        admin_password = 'admin123'

        if (
            request.form['email'] == admin_email and
            request.form['password'] == admin_password
        ):

            session['admin'] = True

            return redirect('/admin_dashboard')

    return render_template('admin_login.html')

# ADMIN DASHBOARD

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    cur = mysql.connection.cursor()

    # USERS

    cur.execute("SELECT * FROM consumer")
    users = cur.fetchall()

    # BILLS

    cur.execute("SELECT * FROM bill")
    bills = cur.fetchall()

    # COMPLAINTS

    cur.execute("SELECT * FROM complaint")
    complaints = cur.fetchall()

    return render_template(
        'admin_dashboard.html',
        users=users,
        bills=bills,
        complaints=complaints
    )

# GENERATE BILL

@app.route('/add_bill', methods=['POST'])
def add_bill():

    if 'admin' not in session:
        return redirect('/admin')

    consumer_id = request.form['consumer_id']
    month = request.form['month']
    units_consumed = int(request.form['units_consumed'])

    # SIMPLE BILL CALCULATION

    total_amount = units_consumed * 5

    cur = mysql.connection.cursor()

    cur.execute("""
    INSERT INTO bill
    (consumer_id, month, units_consumed, total_amount, bill_status)
    VALUES (%s,%s,%s,%s,%s)
    """, (
        consumer_id,
        month,
        units_consumed,
        total_amount,
        'Unpaid'
    ))

    mysql.connection.commit()

    return redirect('/admin_dashboard')

# TOGGLE COMPLAINT STATUS

@app.route('/toggle_complaint/<int:complaint_id>')
def toggle_complaint(complaint_id):

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT complaint_status
    FROM complaint
    WHERE complaint_id=%s
    """, (complaint_id,))

    status = cur.fetchone()[0]

    if status == 'Unsolved':
        new_status = 'Solved'
    else:
        new_status = 'Unsolved'

    cur.execute("""
    UPDATE complaint
    SET complaint_status=%s
    WHERE complaint_id=%s
    """, (new_status, complaint_id))

    mysql.connection.commit()

    return redirect('/admin_dashboard')

# TOGGLE BILL STATUS

@app.route('/toggle_bill/<int:bill_id>')
def toggle_bill(bill_id):

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT bill_status
    FROM bill
    WHERE bill_id=%s
    """, (bill_id,))

    status = cur.fetchone()[0]

    if status == 'Unpaid':
        new_status = 'Paid'
    else:
        new_status = 'Unpaid'

    cur.execute("""
    UPDATE bill
    SET bill_status=%s
    WHERE bill_id=%s
    """, (new_status, bill_id))

    mysql.connection.commit()

    return redirect('/admin_dashboard')

# DELETE CONSUMER

@app.route('/delete_consumer/<int:consumer_id>')
def delete_consumer(consumer_id):

    cur = mysql.connection.cursor()

    # DELETE COMPLAINTS

    cur.execute("""
    DELETE FROM complaint
    WHERE consumer_id=%s
    """, (consumer_id,))

    # KEEP BILL HISTORY

    cur.execute("""
    UPDATE bill
    SET consumer_id=NULL
    WHERE consumer_id=%s
    """, (consumer_id,))

    # DELETE USER

    cur.execute("""
    DELETE FROM consumer
    WHERE consumer_id=%s
    """, (consumer_id,))

    mysql.connection.commit()

    return redirect('/admin_dashboard')

# LOGOUT

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# RUN APP

if __name__ == '__main__':
    app.run(debug=True)