from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import track


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'  # SQLite database file
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        task_name = request.form['task_name']
        task_duration = request.form['task_duration']

        # Check if any input is empty
        if not task_name or not task_duration:
            error_message = 'Please fill in all fields.'
            tasks = Task.query.all()
            return render_template('tasks.html', tasks=tasks, error_message=error_message)

        # Convert duration to an integer
        try:
            task_duration = int(task_duration)
        except ValueError:
            error_message = 'Invalid duration. Please enter a valid number.'
            tasks = Task.query.all()
            return render_template('tasks.html', tasks=tasks, error_message=error_message)

        task = Task.query.filter_by(name=task_name).first()
        if not task:
            task = Task(name=task_name, duration=task_duration)
            db.session.add(task)
            db.session.commit()
        return redirect('/tasks')

    # Get tasks from Track
    all_time_entries = track.get_time_entries()
    # print(all_tasks)
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


    return render_template('tasks.html', tasks=tasks, status=status)

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect('/tasks')


@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
