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

from re import fullmatch

from source.database import UserModel


def username_validator(username):
    username = str(username).lower()

    # Checking for length
    if not 3 <= len(username) <= 20:
        raise ValueError("username must be between 3 to 20 characters.")

    # Checking for alphanumeric
    if not username.isalnum():
        raise ValueError("username can be only alphanumeric.")

    # Checking availability
    exists = UserModel.query.filter_by(username=username).one_or_none()
    if exists:
        raise ValueError("username already taken.")

    return username


def email_validator(email):
    email = str(email).lower()
    regex = r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"

    # Checking email syntactically
    if not fullmatch(regex, email):
        raise ValueError("please provide valid email address.")

    # Checking uniqueness
    exists = UserModel.query.filter_by(email=email).one_or_none()
    if exists:
        raise ValueError("email address already exists.")

    return email


def password_validator(password):
    password = str(password)

    if not 8 <= len(password) <= 20:
        raise ValueError("password must be between 8 to 20 characters.")

    return password


def url_validator(url):
    url = str(url)
    regex = (
        "((http|https)://)(www.)?"
        + "[a-zA-Z0-9@:%._\\+~#?&//=]"
        + "{2,256}\\.[a-z]"
        + "{2,6}\\b([-a-zA-Z0-9@:%"
        + "._\\+~#?&//=]*)"
    )

    if not fullmatch(regex, url):
        raise ValueError("Target URL is invalid.")

    return url
