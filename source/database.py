"""
 Copyright (c) 2023 Vishv Patel (https://github.com/itsthevp)

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"), to deal in
 the Software without restriction, including without limitation the rights to
 use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 """

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    verified = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow())

    urls = db.relationship(
        "urls", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )


class URLModel(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    slug = db.Column(db.String(10), nullable=False, unique=True, index=True)
    target = db.Column(db.Text(), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    visit_count = db.Column(db.Integer(), default=0)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("users", back_populates="urls")
