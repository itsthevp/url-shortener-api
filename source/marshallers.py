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

from flask_restx import fields, Model

from source.api import api


login_response = api.model(
    "LoginResponse", {"access_token": fields.String, "usage": fields.String}
)

url_basic_response = api.model(
    "URLBasicResponse",
    {
        "id": fields.Integer,
        "slug": fields.String,
        "target": fields.String,
    },
)

url_detailed_response = api.inherit(
    "URLDetailedResponse",
    url_basic_response,
    {
        "active": fields.Boolean,
        "visit_count": fields.Integer,
    },
)

user_basic_response = api.model(
    "UserBasicResponse",
    {
        "id": fields.Integer,
        "first_name": fields.String,
        "last_name": fields.String,
        "username": fields.String,
        "email": fields.String,
    },
)

user_registered_response = api.inherit(
    "UserRegisteredResponse",
    user_basic_response,
    {"created": fields.DateTime, "active": fields.Boolean, "verified": fields.Boolean},
)

user_detailed_response = api.inherit(
    "UserDetailedResponse",
    user_registered_response,
    {"urls": fields.List(fields.Nested(url_basic_response))},
)
