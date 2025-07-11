from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table
student_group = db.Table(
    'student_group',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE')),
    db.Column('group_id',   db.Integer, db.ForeignKey('group.id',   ondelete='CASCADE'))
)

class Student(db.Model):
    __tablename__ = 'student'
    id          = db.Column(db.Integer, primary_key=True)
    fullname    = db.Column(db.String(100), nullable=False)
    parent_name = db.Column(db.String(100))
    phone1      = db.Column(db.String(20))
    phone2      = db.Column(db.String(20))
    phone3      = db.Column(db.String(20))
    status      = db.Column(db.String(20), default='active')
    join_date   = db.Column(db.Date)
    payment_day = db.Column(db.Integer)
    comments    = db.Column(db.Text)

    # many-to-many to Group
    groups = db.relationship(
        'Group',
        secondary=student_group,
        backref=db.backref('students', lazy='select'),   # ← change here!
        passive_deletes=True
    )

    attendances = db.relationship(
        'Attendance',
        backref='student',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    homeworks = db.relationship(
        'Homework',
        backref='student',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

class Group(db.Model):
    __tablename__ = 'group'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(50), nullable=False)
    schedule = db.Column(db.String(100))

    attendances = db.relationship(
        'Attendance',
        backref='group',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    homeworks = db.relationship(
        'Homework',
        backref='group',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.Date,    nullable=False)
    status     = db.Column(db.Boolean, default=False)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False
    )
    group_id   = db.Column(
        db.Integer,
        db.ForeignKey('group.id', ondelete='CASCADE'),
        nullable=False
    )

class Homework(db.Model):
    __tablename__ = 'homework'
    id           = db.Column(db.Integer, primary_key=True)
    date         = db.Column(db.Date,    nullable=False)
    percent_done = db.Column(db.Integer, default=0)
    student_id   = db.Column(
        db.Integer,
        db.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False
    )
    group_id     = db.Column(
        db.Integer,
        db.ForeignKey('group.id', ondelete='CASCADE'),
        nullable=False
    )
