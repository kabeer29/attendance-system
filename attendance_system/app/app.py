import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import uuid
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'known_faces'
app.config['ATTENDANCE_FILE'] = 'attendance.xlsx'
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True, unique=True)
    password = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Student('{self.name}', '{self.username}')"


def init_db():
    with app.app_context():
        db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/student_login')
def student_login():
    error = request.args.get('error')
    return render_template('student.html', error=error)


@app.route('/student_signup')
def student_signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = name # set username to name
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        # Create a directory with the user's name inside the known_faces directory
        directory = os.path.join(app.config['UPLOAD_FOLDER'], name)
        os.makedirs(directory, exist_ok=True)

        # Save the uploaded image inside the user's directory with a unique name
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(directory, f"{str(uuid.uuid4())}.{filename.split('.')[-1]}")
        photo.save(photo_path)

        # Save the user details in the database
        new_student = Student(name=name, photo=photo_path, username=username, password=password)
        db.session.add(new_student)
        db.session.commit()
        print("data saved")
        print("name: ", name)
        print("username: ", username)
        print("password: ", password)

        return redirect(url_for('student_login'))
    else:
        return render_template('signup.html')

@app.route('/teacher_login')
def teacher_login():
    return render_template('teacher.html')

       


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        student = Student.query.filter_by(username=username, password=password).first()

        if student:
            return redirect(url_for('welcome', username=username, password=password))
        else:
            return render_template('student.html', error='Invalid username or password')
    else:
        return redirect(url_for('student_login'))

@app.route('/student_welcome')
def student_welcome():
    return render_template('welcome.html')


@app.route('/welcome')
def welcome():
    username = request.args.get('username')
    password = request.args.get('password')
    student = Student.query.filter_by(username=username, password=password).first()
    if student:
        attendance_file = app.config['ATTENDANCE_FILE']
        attendance_data = pd.read_excel(attendance_file, sheet_name='Sheet1')
        attendance = attendance_data[attendance_data['Name'] == student.name].to_html(index=False)
        return render_template('welcome.html', student=student, attendance=attendance)
    else:
        return redirect(url_for('student_login', error='Invalid username or password'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
