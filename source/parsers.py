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

from flask_restx.reqparse import RequestParser

from source.validators import (
    username_validator,
    email_validator,
    password_validator,
    url_validator,
)


login_parser = RequestParser(trim=True)
login_parser.add_argument("username", type=str, required=True, location="json")
login_parser.add_argument("password", type=str, required=True, location="json")

register_parser = RequestParser(trim=True)
register_parser.add_argument("first_name", type=str, required=True, location="json")
register_parser.add_argument("last_name", type=str, required=True, location="json")
register_parser.add_argument(
    "email", type=email_validator, required=True, location="json"
)
register_parser.add_argument(
    "username", type=username_validator, required=True, location="json"
)
register_parser.add_argument(
    "password", type=password_validator, required=True, location="json"
)

short_url_parser = RequestParser(trim=True)
short_url_parser.add_argument(
    "url", dest="target", type=url_validator, required=True, location="json"
)
short_url_parser.add_argument(
    "active",
    type=lambda v: v is not None and str(v).lower() in ("true", 1),
    location="json",
)
