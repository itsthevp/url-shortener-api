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

from flask_restx import Resource, marshal_with
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from source.api import api
from source.database import UserModel
from source.redis import jwt_redis_blocklist
from source.parsers import login_parser, register_parser
from source.marshallers import login_response, register_response


@api.route("/", endpoint="index")
class Index(Resource):
    def get(self):
        return None


@api.route("/login", endpoint="login")
class Login(Resource):
    @api.expect(login_parser)
    @api.response(400, "Bad Request")
    @api.marshal_with(login_response, code=200, description="Success")
    def post(self):
        data = login_parser.parse_args(strict=True)
        user = UserModel.query.filter(
            UserModel.username == data["username"],
            UserModel.password == data["password"],
        ).one_or_none()
        if user:
            return (
                dict(
                    access_token=create_access_token(
                        identity=user, expires_delta=timedelta(minutes=30)
                    ),
                    usage="You will need to pass this in the Authorization header like Bearer access_token",
                ),
                200,
            )
        return dict(message="Invalid credentials"), 400


@api.route("/logout", endpoint="logout")
class Logout(Resource):
    @jwt_required(optional=True)
    def get(self):
        jwt = get_jwt()
        if jwt:
            jwt_redis_blocklist.set(name=jwt["jti"], value="", ex=timedelta(minutes=30))
        return dict(message="OK"), 200


@api.route("/register", endpoint="register")
class Register(Resource):
    @api.expect(register_parser)
    @api.response(400, "Bad Request")
    @api.response(500, "Server Error")
    @api.marshal_with(register_response, code=201, description="Success")
    def post(self):
        data = register_parser.parse_args(strict=True)
        user = UserModel(**data)
        added = UserModel.add(user)
        if added:
            return user, 201
        return dict(message="Please try again after sometime"), 500


@api.route("/go/<string:slug>", endpoint="go")
class Go(Resource):
    def get(self, slug: str):
        ...


@api.route("/short", endpoint="short")
class Short(Resource):
    @jwt_required()
    def post(self):
        ...
