# -*- coding: utf-8 -*-
# Filename: auth
# Author: brayton
# Datetime: 2019-Oct-17 6:03 PM

import jwt

from setting import JWT_AUTH as JWT
from core import exceptions


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.headers.get('AUTHORIZATION', b'')
    # if isinstance(auth, str):
    #     # Header encoding (see RFC5987)
    #     auth = auth.encode('iso-8859-1')
    return auth


def jwt_decode_handler(token):
    options = {
        'verify_exp': JWT['VERIFY_EXPIRATION'],
    }
    # get user from token, BEFORE verification, to get user secret key
    secret_key = JWT['SECRET_KEY']
    return jwt.decode(
        token,
        JWT['PUBLIC_KEY'] or secret_key,
        JWT['VERIFY'],
        options=options,
        leeway=JWT['LEEWAY'],
        audience=JWT['AUDIENCE'],
        issuer=JWT['ISSUER'],
        algorithms=[JWT['ALGORITHM']]
    )


def jwt_encode_handler(payload):
    return jwt.encode(
        payload=payload,
        key=JWT['SECRET_KEY'],
        algorithm=JWT['ALGORITHM']
    ).decode('utf-8')


class BaseAuthentication(object):
    """
    All authentication classes should extend BaseAuthentication.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        pass


class JSONWebTokenAuthentication(BaseAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = request.token.split()
        auth_header_prefix = JWT['AUTH_HEADER_PREFIX'].lower()

        if not auth:
            if JWT['AUTH_COOKIE']:
                return request.COOKIES.get(JWT['AUTH_COOKIE'])
            return None

        if auth[0].lower() != auth_header_prefix:
            return None

        if len(auth) == 1:
            raise exceptions.Unauthorized(message='无效的授权请求头，没有提身份凭证。')
        elif len(auth) > 2:
            raise exceptions.Unauthorized(message='无效的授权头，凭据字符串不应包含空格。')

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(JWT['AUTH_HEADER_PREFIX'], self.www_authenticate_realm)

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            raise exceptions.Unauthorized(message='签名已过期！')
        except jwt.DecodeError:
            raise exceptions.Unauthorized(message='解码签名时出错！')
        except jwt.InvalidTokenError:
            raise exceptions.Unauthorized(message='无效签名！')

        user = self.authenticate_credentials(payload)

        return user, jwt_value

    @staticmethod
    def authenticate_credentials(payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        auth_uid = payload.get('userId')
        is_superuser = payload.get('isSuperuser')
        if not auth_uid:
            raise exceptions.Unauthorized(message='无效的认证信息！')
        if not is_superuser:
            raise exceptions.Forbidden(message='当前系统只支持超级用户访问！')
        return payload
