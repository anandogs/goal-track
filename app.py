from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import openai
import os
import track
from flask_limiter import Limiter
from flask_migrate import Migrate
import random

openai.api_key = os.getenv('OPEN_AI_KEY')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')  # SQLite database file
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set a secret key for session management
db = SQLAlchemy(app)

def get_ipaddr():
    return request.remote_addr

limiter = Limiter(app=app, key_func=get_ipaddr)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)

migrate = Migrate(app, db)

ALLOWED_EMAILS = [email.strip() for email in os.getenv('ALLOWED_EMAILS').split(',')]

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
@limiter.limit("10/minute")  # Add this line to limit calls to 10 per minute per IP
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
            task = Task(name=task_name, duration=task_duration, email=email)
            db.session.add(task)
            db.session.commit()
        return redirect('/')

    # Get tasks from Track
    all_time_entries = track.get_time_entries(email, password)
    tasks = Task.query.filter_by(email=email).all()
    # tasks = Task.query.all()
    descriptions = {}

    class Description:
        def __init__(self, id=0, name="", duration=0, completed=False):
            self.id = id
            self.name = name
            self.duration = duration
            self.completed = completed

    for task in tasks:
        descriptions[task.name] = Description(task.id, task.name, task.duration, False)
    completed_tasks = 0
    total_tasks = len(descriptions)
    
    for entry in all_time_entries:
        if entry['description'] in descriptions:
            descriptions[entry['description']].id = entry['id']
            descriptions[entry['description']].duration = descriptions[entry['description']].duration * 60 - entry['duration']
            if descriptions[entry['description']].duration <= 0:
                completed_tasks += 1
                descriptions[entry['description']].completed = True
                descriptions[entry['description']].duration = 0
                
    total_tasks = len(descriptions)

    if total_tasks > 0:
        completion_percentage = completed_tasks / total_tasks * 100
    else:
        completion_percentage = 0

    description_list = list(descriptions.values())

    image_urls = [
        "https://s.wsj.net/public/resources/images/BN-XC577_0122GO_SOC_20180122114320.jpg",
        "https://i.pinimg.com/originals/53/9c/86/539c86b2409c6b00c371f4b36b00a73a.jpg",
        "https://i.pinimg.com/736x/d8/66/cb/d866cbebe104951a436e76de36882d84.jpg",
        "https://images.news18.com/ibnlive/uploads/2018/01/pigeon.png",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSm9ThoWdcvvBdaGpbSMpwIXxxq4EyWskYCgQ&usqp=CAU"
    ]

    random_image_url = random.choice(image_urls)


    # Construct the haiku prompt based on completion percentage
    prompt = f"Witty haiku for someone who has completed {completion_percentage}% of their tasks written by a shame monster:"
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=30,
        n=1,
        stop=None,
        temperature=0.8
    )
    witty_haiku = response.choices[0].text.strip().capitalize()

    if completed_tasks == total_tasks:
        status = '\U0001F389'  # Celebration emoji
    else:
        status = f'{completed_tasks}/{total_tasks}'

    return render_template('index.html', tasks=description_list, witty_haiku=witty_haiku, status=status, random_image_url=random_image_url)

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

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html', error_message="Too many requests. Please try again later."), 429


if __name__ == '__main__':
    app.run(debug=True)
