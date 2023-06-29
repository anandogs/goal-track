from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import track
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')  # SQLite database file
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set a secret key for session management
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Call the get_time_entries function with the provided email and password
        time_entries = track.get_time_entries(email, password)
        
        # Check if the result is None, indicating incorrect username or password
        if time_entries is None:
            error_message = 'Incorrect username or password.'
            return render_template('login.html', error_message=error_message)
        
        # Store the user's email and password in session
        session['email'] = email
        session['password'] = password
        return redirect('/')
    
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def tasks():
    if 'email' not in session or 'password' not in session:
        return redirect('/login')
    
    # Retrieve the user's email and password from session
    email = session['email']
    password = session['password']

    if request.method == 'POST':
        task_name = request.form['task_name']
        task_duration = request.form['task_duration']

        # Check if any input is empty
        if not task_name or not task_duration:
            error_message = 'Please fill in all fields.'
            tasks = Task.query.all()
            return render_template('index.html', tasks=tasks, error_message=error_message)

        # Convert duration to an integer
        try:
            task_duration = int(task_duration)
        except ValueError:
            error_message = 'Invalid duration. Please enter a valid number.'
            tasks = Task.query.all()
            return render_template('index.html', tasks=tasks, error_message=error_message)

        task = Task.query.filter_by(name=task_name).first()
        if not task:
            task = Task(name=task_name, duration=task_duration)
            db.session.add(task)
            db.session.commit()
        return redirect('/')

    # Get tasks from Track
    all_time_entries = track.get_time_entries(email, password)
    tasks = Task.query.all()
    descriptions = {}
    for task in tasks:
        descriptions[task.name] = task.duration * 60
    completed_tasks = 0
    total_tasks = len(descriptions)
    
    for entry in all_time_entries:
        if entry['description'] in descriptions:
            descriptions[entry['description']] -= entry['duration']
            if descriptions[entry['description']] <= 0:
                completed_tasks += 1
                descriptions[entry['description']] = 0

    total_tasks = len(descriptions)

    if completed_tasks == total_tasks:
        status = '\U0001F389'  # Celebration emoji
    else:
        status = f'{completed_tasks}/{total_tasks}'

    return render_template('index.html', tasks=tasks, status=status)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect('/')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data to log out the user
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
