
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