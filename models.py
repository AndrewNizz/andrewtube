import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from db_session import SqlAlchemyBase


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.Text, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    videos = orm.relationship('Videos', back_populates='user')
    comms = orm.relationship('Comments', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Videos(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'videos'
    __table_args__ = {'extend_existing': True}

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    link = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=False)
    views = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    preview = sqlalchemy.Column(sqlalchemy.LargeBinary)

    comments = orm.relationship('Comments', back_populates='vid')
    user = orm.relationship('Users')


class Comments(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'
    __table_args__ = {'extend_existing': True}

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comment = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    video_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("videos.id"), nullable=False)

    user = orm.relationship('Users')
    vid = orm.relationship('Videos')