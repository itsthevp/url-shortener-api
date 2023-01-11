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

from flask_restx import Api, Namespace


api = Api(
    prefix="/api",
    doc="/swagger",
    catch_all_404s=True,
    serve_challenge_on_401=True,
)

user_namespace = Namespace(
    name="User Namespace",
    description=(
        "This namespace contains the endpoints related to USER"
        "\nNote: All endpoints are protected and requires valid JWT in Authorization Header as Bearer"
    ),
    path="/user",
    ordered=True,
)

url_namespace = Namespace(
    name="URL Namespace",
    description=(
        "This namespace contains the endpoints related to URL"
        "\nNote: All endpoints are protected and requires valid JWT in Authorization Header as Bearer"
    ),
    path="/url",
    ordered=True,
)

api.add_namespace(user_namespace)
api.add_namespace(url_namespace)
