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
from typing import Union

from flask_jwt_extended import JWTManager

from source.redis import jwt_redis_blocklist
from source.database import UserModel


jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_callback(user: UserModel) -> int:
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_header, payload) -> Union[UserModel, None]:
    identity = payload["sub"]
    return UserModel.query.filter_by(id=identity).one_or_none()


@jwt.token_in_blocklist_loader
def token_lookup_callback(_header, payload) -> bool:
    jti = payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


def blocklist_token(jti: str) -> None:
    """Stores the `jti` in Redis block-listed database

    Args:
        jti (_type_): jti of the JWT token
    """
    jwt_redis_blocklist.set(name=jti, value="", ex=timedelta(minutes=30))
