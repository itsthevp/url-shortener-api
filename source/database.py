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
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


db = SQLAlchemy()


class ModelMixin:
    def save_in_db(self) -> bool:
        db.session.add(self)
        return self.__commit()

    def update_in_db(self) -> bool:
        return self.__commit()

    def delete_from_db(self) -> bool:
        db.session.delete(self)
        return self.__commit()

    def __commit(self) -> bool:
        try:
            db.session.commit()
            return True
        except SQLAlchemyError as err:
            db.session.rollback()
            print(f"Transaction Failed\nReason: {str(err)}")
            return False


class UserModel(db.Model, ModelMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)
    verified = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow())

    urls = db.relationship(
        "URLModel", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )


class URLModel(db.Model, ModelMixin):
    __tablename__ = "urls"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    slug = db.Column(db.String(10), nullable=False, unique=True, index=True)
    target = db.Column(db.Text(), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    visit_count = db.Column(db.Integer(), default=0)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("UserModel", back_populates="urls")
