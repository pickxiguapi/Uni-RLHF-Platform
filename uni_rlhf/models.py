from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    def __init__(self, username, password,email):
        self.username = username
        self.set_password(password)
        self.email=email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return '<User %r>' % self.username

class Project(db.Model):
    __tablename__ = 'Project'
    project_id = db.Column(db.String(80), primary_key=True)
    project_name = db.Column(db.String(120))
    description = db.Column(db.Text)
    due_time = db.Column(db.DateTime)
    visibility = db.Column(db.Integer)
    dataset_path = db.Column(db.String(200))
    domain = db.Column(db.String(80))
    task = db.Column(db.String(80))
    environment_name = db.Column(db.String(80))
    instruction = db.Column(db.Text)
    mode = db.Column(db.String(80))
    sampler_type = db.Column(db.String(80))
    feedback_type = db.Column(db.String(80))
    query_num = db.Column(db.Integer)
    query_length = db.Column(db.Integer)
    video_width = db.Column(db.Integer)
    video_height = db.Column(db.Integer)
    fps = db.Column(db.Integer)
    creator = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    create_time = db.Column(db.DateTime)
    status = db.Column(db.String(80))
    annotation_num = db.Column(db.Integer)
    question = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)

class Query(db.Model):
    __tablename__ = 'Query'
    query_id = db.Column(db.String(80), primary_key=True)
    project_id = db.Column(db.String(80), db.ForeignKey('Project.project_id'))
    completion_time = db.Column(db.DateTime)
    marked_num = db.Column(db.Integer)
    skip_num = db.Column(db.Integer)
    video_info = db.Column(db.Text)
    video_url = db.Column(db.String(200))
    label_info = db.Column(db.Text)  
    is_deleted = db.Column(db.Boolean, default=False)

class QueryAnnotator(db.Model):
    __tablename__ = 'QueryAnnotator'
    query_annotator_id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String(80), db.ForeignKey('Query.query_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    is_deleted = db.Column(db.Boolean, default=False)

class UserProject(db.Model):
    __tablename__ = 'UserProject'
    user_project_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(80), db.ForeignKey('Project.project_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    is_deleted = db.Column(db.Boolean, default=False)
