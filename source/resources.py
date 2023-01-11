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

from datetime import timedelta
from time import time_ns

from flask_restx import Resource, marshal
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, current_user

from source.api import api
from source.database import UserModel, URLModel
from source.jwt import blocklist_token
from source.parsers import (
    login_parser,
    register_parser,
    short_url_parser,
    url_update_parser,
    user_update_parser,
)
from source.marshallers import (
    login_response,
    user_basic_response,
    user_registered_response,
    user_detailed_response,
    url_basic_response,
    url_detailed_response,
)


@api.route("/", endpoint="index")
class Index(Resource):
    @api.response(204, "No Content")
    def get(self):
        return None, 204


@api.route("/user/login", endpoint="login")
class Login(Resource):
    @api.expect(login_parser)
    @api.response(200, "Success", login_response)
    @api.response(400, "Bad Request")
    def post(self):
        data = login_parser.parse_args(strict=True)
        user = UserModel.query.filter(
            UserModel.username == data["username"],
            UserModel.password == data["password"],
        ).one_or_none()
        if user:
            return (
                marshal(
                    dict(
                        access_token=create_access_token(
                            identity=user, expires_delta=timedelta(minutes=30)
                        ),
                        usage="You will need to pass this in the Authorization header like Bearer access_token",
                    ),
                    login_response,
                ),
                200,
            )
        return dict(message="Invalid credentials"), 400


@api.route("/user/logout", endpoint="logout")
class Logout(Resource):
    @jwt_required(optional=True)
    @api.response(204, "No Content")
    def get(self):
        jwt = get_jwt()
        if jwt:
            blocklist_token(jwt["jti"])
        return None, 204


@api.route("/user/register", endpoint="register")
class Register(Resource):
    @api.expect(register_parser)
    @api.response(201, "Success", user_registered_response)
    @api.response(400, "Bad Request")
    @api.response(500, "Server Error")
    def post(self):
        data = register_parser.parse_args(strict=True)
        user = UserModel(**data)
        added = user.save_in_db()
        if added:
            return marshal(user, user_registered_response), 201
        return dict(message="Please try again after sometime"), 500


@api.route("/user", endpoint="user")
class User(Resource):
    @jwt_required()
    @api.marshal_with(user_detailed_response, code=200, description="Success")
    def get(self):
        current_user.urls.all()
        return current_user

    @jwt_required()
    @api.expect(user_update_parser)
    @api.response(200, "Success", user_basic_response)
    @api.response(304, "Not Modified")
    @api.response(400, "Bad Request")
    def patch(self):
        data = user_update_parser.parse_args()
        if not any(data.values()):
            return None, 304
        elif (
            "email" in data
            and current_user.email != data["email"]
            and UserModel.query.filter_by(email=data["email"]).one_or_none() is not None
        ):
            return dict(message="email address already exists."), 400
        else:
            current_user.first_name = data.get("first_name") or current_user.first_name
            current_user.last_name = data.get("last_name") or current_user.last_name
            current_user.email = data.get("email") or current_user.email
            current_user.password = data.get("password") or current_user.password
            current_user.update_in_db()
            return marshal(current_user, user_basic_response), 200

    @jwt_required()
    @api.response(200, "Success")
    @api.response(304, "Not Modified")
    def delete(self):
        deleted = current_user.delete_from_db()
        if deleted:
            blocklist_token(get_jwt()["jti"])
        return None, 200 if deleted else 304


@api.route("/url/go/<string:slug>", endpoint="go")
class Go(Resource):
    @api.response(200, "Success", url_basic_response)
    @api.response(404, "Not Found")
    def get(self, slug: str):
        if slug and slug.isalnum():
            url = URLModel.query.filter_by(slug=slug).one_or_none()
            if url and url.active:
                url.visit_count += 1
                url.update_in_db()
                return marshal(url, url_basic_response), 200
        return None, 404


@api.route("/url/short", endpoint="short")
class Short(Resource):
    @jwt_required()
    @api.expect(short_url_parser)
    @api.response(201, "Success", url_detailed_response)
    @api.response(500, "Server Error")
    def post(self):
        data = short_url_parser.parse_args(strict=True)
        url = URLModel(**data)
        url.slug = self.__get_unique_slug()
        url.user_id = current_user.id
        saved = url.save_in_db()
        if saved:
            return marshal(url, url_detailed_response), 201
        return dict(message="Please try again after sometime"), 500

    def __get_unique_slug(self):
        base_62_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        slug = ""
        timestamp_ns = time_ns()
        while timestamp_ns > 0:
            slug += base_62_str[timestamp_ns % 62]
            timestamp_ns //= 62
        return slug[:7]


@api.route("/url/<int:url_id>", endpoint="url")
class URL(Resource):
    @jwt_required()
    @api.response(200, "Success", url_detailed_response)
    @api.response(404, "Not Found")
    def get(self, url_id: int):
        url = self.__get_url_object(current_user.id, url_id)
        if url:
            return marshal(url, url_detailed_response), 200
        return None, 404

    @jwt_required()
    @api.expect(url_update_parser)
    @api.response(200, "Success", url_detailed_response)
    @api.response(304, "Not Modified")
    @api.response(400, "Bad Request")
    @api.response(404, "Not Found")
    def patch(self, url_id: int):
        data = url_update_parser.parse_args(strict=True)
        if not any(v is not None for v in data.values()):
            return None, 304
        url = self.__get_url_object(current_user.id, url_id)
        if url:
            url.active = (
                data["active"] if data.get("active") is not None else url.active
            )
            if data.get("slug") and data["slug"] != url.slug and data["slug"].isalnum():
                slug_exists = URLModel.query.filter_by(slug=data["slug"]).one_or_none()
                if not slug_exists:
                    url.slug = data["slug"]
                else:
                    return dict(message="slug already exists"), 400
            url.update_in_db()
            return marshal(url, url_detailed_response), 200
        return None, 404

    @jwt_required()
    @api.response(200, "Success")
    @api.response(304, "Not Modified")
    def delete(self, url_id: int):
        url = self.__get_url_object(current_user.id, url_id)
        if url:
            url.active = False
            updated = url.update_in_db()
        return None, 200 if updated else 304

    def __get_url_object(self, user_id: int, url_id: int):
        return URLModel.query.filter(
            URLModel.id == url_id, URLModel.user_id == user_id
        ).one_or_none()
