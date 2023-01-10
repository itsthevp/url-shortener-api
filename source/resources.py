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
from source.redis import jwt_redis_blocklist
from source.parsers import login_parser, register_parser, short_url_parser
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
    def get(self):
        return None


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
    def get(self):
        jwt = get_jwt()
        if jwt:
            jwt_redis_blocklist.set(name=jwt["jti"], value="", ex=timedelta(minutes=30))
        return dict(message="OK"), 200


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


@api.route("/user/<int:user_id>", endpoint="user")
class User(Resource):
    @jwt_required()
    @api.response(200, "Success", user_detailed_response)
    def get(self, user_id: int):
        ...

    @jwt_required()
    @api.response(200, "Success", user_basic_response)
    def patch(self, user_id: int):
        ...

    @jwt_required()
    @api.response(200, "Success")
    def delete(self, user_id: int):
        ...


@api.route("/go/<string:slug>", endpoint="go")
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


@api.route("/short", endpoint="short")
class Short(Resource):
    @jwt_required()
    @api.expect(short_url_parser)
    @api.response(201, "Success", url_detailed_response)
    @api.response(500, "Server Error")
    def post(self):
        data = short_url_parser.parse_args(strict=True)
        url = URLModel(**data)
        url.slug = self.get_unique_slug()
        url.user_id = current_user.id
        saved = url.save_in_db()
        if saved:
            return marshal(url, url_detailed_response), 201
        return dict(message="Please try again after sometime"), 500

    def get_unique_slug(self):
        base_62_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        slug = ""
        timestamp_ns = time_ns()
        while timestamp_ns > 0:
            slug += base_62_str[timestamp_ns % 62]
            timestamp_ns //= 62
        return slug[:7]
