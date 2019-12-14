# flake8:noqa
import abc
import base64
import logging
from urllib.parse import urlencode, urljoin, quote, parse_qsl, urlsplit
from hashlib import sha1
from typing import Dict, Tuple
import hmac
import random
import time

from aiohttp import ClientResponse, ClientSession
from aiohttp.web import HTTPBadRequest
import yarl

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


_log = logging.getLogger(__name__)


class UserInfo:  # pylint: disable=too-few-public-methods

    default_attrs = [
        "id",
        "email",
        "first_name",
        "last_name",
        "username",
        "picture",
        "link",
        "locale",
        "city",
        "country",
        "gender",
    ]

    def __init__(self, **kwargs) -> None:
        for attr in self.default_attrs:
            setattr(self, attr, "")
        for key, value in kwargs.items():
            setattr(self, key, value)


class Signature(abc.ABC):

    """Abstract base class for signature methods."""

    name: str = None

    @staticmethod
    def _escape(string: str) -> bytes:
        """URL escape a string."""
        return quote(string.encode("utf-8"), "~").encode("utf-8")

    @abc.abstractmethod
    def sign(
        self,
        consumer_secret: str,
        method: str,
        url: str,
        oauth_token_secret: str = None,
        **params,
    ) -> str:
        pass


class HmacSha1Signature(Signature):

    """HMAC-SHA1 signature-method."""

    name = "HMAC-SHA1"

    def sign(
        self,
        consumer_secret: str,
        method: str,
        url: str,
        oauth_token_secret: str = None,
        **params,
    ) -> str:
        """Create a signature using HMAC-SHA1."""
        # build the url the same way aiohttp will build the query later on
        # cf https://github.com/KeepSafe/aiohttp/blob/master/aiohttp/client.py#L151
        # and https://github.com/KeepSafe/aiohttp/blob/master/aiohttp/client_reqrep.py#L81
        url, params = str(yarl.URL(url).with_query(sorted(params.items()))).split(
            "?", 1
        )  # type: ignore
        method = method.upper()

        signature = b"&".join(map(self._escape, (method, url, params)))  # type: ignore

        key = self._escape(consumer_secret) + b"&"
        if oauth_token_secret:
            key += self._escape(oauth_token_secret)

        hashed = hmac.new(key, signature, sha1)
        return base64.b64encode(hashed.digest()).decode()


class PlaintextSignature(Signature):

    """PLAINTEXT signature-method."""

    name = "PLAINTEXT"

    def sign(
        self,
        consumer_secret: str,
        method: str,
        url: str,
        oauth_token_secret: str = None,
        **params,
    ) -> str:
        """Create a signature using PLAINTEXT."""
        key = self._escape(consumer_secret) + b"&"
        if oauth_token_secret:
            key += self._escape(oauth_token_secret)
        return key.decode()


class Client(abc.ABC):

    """Base abstract OAuth Client class."""

    access_token_key: str = "access_token"
    shared_key: str = "oauth_verifier"
    access_token_url: str = None
    authorize_url: str = None
    base_url: str = None
    name: str = None
    user_info_url: str = None

    def __init__(
        self,
        aiohttp_session: ClientSession,
        base_url: str = None,
        authorize_url: str = None,
        access_token_key: str = None,
        access_token_url: str = None,
        user_info_url: str = None,
    ) -> None:
        """Initialize the client."""
        self.base_url = base_url or self.base_url
        self.aiohttp_session = aiohttp_session
        self.authorize_url = authorize_url or self.authorize_url
        self.access_token_key = access_token_key or self.access_token_key
        self.access_token_url = access_token_url or self.access_token_url
        self.user_info_url = user_info_url or self.user_info_url

    def _get_url(self, url: str) -> str:
        """Build provider's url. Join with base_url part if needed."""
        if self.base_url and not url.startswith(("http://", "https://")):
            return urljoin(self.base_url, url)
        return url

    def __str__(self) -> str:
        """String representation."""
        return "%s %s" % (self.name.title(), self.base_url)

    def __repr__(self) -> str:
        """String representation."""
        return "<%s>" % self

    @abc.abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        params: Dict[str, str] = None,
        headers: Dict[str, str] = None,
        **aio_kwargs,
    ) -> ClientResponse:
        pass

    async def user_info(self, **kwargs) -> Tuple[UserInfo, Dict]:
        """Load user information from provider."""
        if not self.user_info_url:
            raise NotImplementedError("The provider doesnt support user_info method.")

        response: ClientResponse = await self.request(
            "GET", self.user_info_url, **kwargs
        )
        if response.status != 200:
            raise HTTPBadRequest(
                reason=f"Failed to obtain User information. HTTP status code: {response.status}"
            )
        data = await response.json()
        user = self.user_parse(data)
        return user, data

    @classmethod
    @abc.abstractmethod
    def user_parse(cls, data) -> UserInfo:
        """Parse user's information from given provider data."""


class OAuth1Client(Client):  # pylint: disable=abstract-method

    """Implement OAuth1."""

    name = "oauth1"
    access_token_key = "oauth_token"
    request_token_url = None
    version = "1.0"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        aiohttp_session: ClientSession,
        consumer_key: str,
        consumer_secret: str,
        base_url: str = None,
        authorize_url: str = None,
        oauth_token: str = None,
        oauth_token_secret: str = None,
        request_token_url: str = None,
        access_token_url: str = None,
        access_token_key: str = None,
        signature=None,
        user_info_url: str = None,
        **params,
    ) -> None:
        """Initialize the client."""
        super().__init__(
            aiohttp_session,
            base_url,
            authorize_url,
            access_token_key,
            access_token_url,
            user_info_url,
        )

        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.request_token_url = request_token_url or self.request_token_url
        self.params = params
        self.signature = signature or HmacSha1Signature()

    def get_authorize_url(self, request_token: str = None, **params) -> str:
        """Return formatted authorization URL."""
        params.update({"oauth_token": request_token or self.oauth_token})
        return self.authorize_url + "?" + urlencode(params)

    async def request(
        self,
        method: str,
        url: str,
        params: Dict[str, str] = None,
        headers: Dict[str, str] = None,
        **aio_kwargs,
    ) -> ClientResponse:
        """Make a request to provider."""
        oparams = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": sha1(str(random.random()).encode("ascii")).hexdigest(),
            "oauth_signature_method": self.signature.name,
            "oauth_timestamp": str(int(time.time())),
            "oauth_version": self.version,
        }
        oparams.update(params or {})

        if self.oauth_token:
            oparams["oauth_token"] = self.oauth_token

        url = self._get_url(url)

        if urlsplit(url).query:
            raise ValueError(
                'Request parameters should be in the "params" parameter, not inlined in the URL'
            )

        oparams["oauth_signature"] = self.signature.sign(
            self.consumer_secret,
            method,
            url,
            oauth_token_secret=self.oauth_token_secret,
            **oparams,
        )
        _log.debug("%s %s", url, oparams)
        return await self.aiohttp_session.request(
            method, url, params=oparams, headers=headers, **aio_kwargs
        )

    async def get_request_token(self, **params) -> Tuple[str, str, Dict]:
        """Get a request_token and request_token_secret from OAuth1 provider."""
        params = dict(self.params, **params)
        response = await self.request("GET", self.request_token_url, params=params)

        data = await response.text()
        response.close()

        if response.status != 200:
            raise HTTPBadRequest(
                reason=f"Failed to obtain OAuth 1.0 request token. HTTP status code: {response.status}"
            )

        data = dict(parse_qsl(data))

        self.oauth_token = data.get("oauth_token")
        self.oauth_token_secret = data.get("oauth_token_secret")
        return self.oauth_token, self.oauth_token_secret, data

    async def get_access_token(
        self, oauth_verifier: str, request_token: str = None, **_params
    ) -> Tuple[str, str, Dict]:
        """Get access_token from OAuth1 provider.
        :returns: (access_token, access_token_secret, provider_data)
        """
        # Possibility to provide REQUEST DATA to the method
        if not isinstance(oauth_verifier, str) and self.shared_key in oauth_verifier:
            oauth_verifier = oauth_verifier[self.shared_key]

        if request_token and self.oauth_token != request_token:
            raise HTTPBadRequest(
                reason="Failed to obtain OAuth 1.0 access token. Request token is invalid"
            )

        response = await self.request(
            "POST",
            self.access_token_url,
            params={"oauth_verifier": oauth_verifier, "oauth_token": request_token},
        )
        if response.status != 200:
            raise HTTPBadRequest(
                reason=f"Failed to obtain OAuth 1.0 access token. HTTP status code: {response.status}"
            )

        data = await response.text()
        data = dict(parse_qsl(data))

        response.close()

        self.oauth_token = data.get("oauth_token")
        self.oauth_token_secret = data.get("oauth_token_secret")
        return self.oauth_token, self.oauth_token_secret, data


class OAuth2Client(Client):  # pylint: disable=abstract-method

    """Implement OAuth2."""

    name = "oauth2"
    shared_key = "code"

    def __init__(
        self,
        aiohttp_session: ClientSession,
        client_id: str,
        client_secret: str,
        base_url: str = None,
        authorize_url: str = None,
        access_token: str = None,
        access_token_url: str = None,
        access_token_key: str = None,
        user_info_url: str = None,
        **params,
    ) -> None:
        """Initialize the client."""
        super().__init__(
            aiohttp_session,
            base_url,
            authorize_url,
            access_token_key,
            access_token_url,
            user_info_url,
        )

        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.params = params

    def get_authorize_url(self, **params) -> str:
        """Return formatted authorize URL."""
        params = dict(self.params, **params)
        params.update({"client_id": self.client_id, "response_type": "code"})
        return self.authorize_url + "?" + urlencode(params)

    async def request(
        self,
        method: str,
        url: str,
        params: Dict[str, str] = None,
        headers: Dict[str, str] = None,
        **aio_kwargs,
    ) -> ClientResponse:
        """Request OAuth2 resource."""
        url = self._get_url(url)
        params = params or {}

        if self.access_token:
            params[self.access_token_key] = self.access_token

        headers = headers or {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        return await self.aiohttp_session.request(
            method, url, params=params, headers=headers, **aio_kwargs
        )

    async def get_access_token(
        self, code: str, redirect_uri: str = None, **payload
    ) -> Tuple[str, Dict]:
        """Get an access_token from OAuth provider.
        :returns: (access_token, provider_data)
        """
        # Possibility to provide REQUEST DATA to the method
        if not isinstance(code, str) and self.shared_key in code:
            code = code[self.shared_key]
        payload.setdefault("grant_type", "authorization_code")
        payload.update(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
            }
        )

        redirect_uri = redirect_uri or self.params.get("redirect_uri")
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        response = await self.request("POST", self.access_token_url, data=payload)
        if "json" in response.headers.get("CONTENT-TYPE"):
            data = await response.json()

        else:
            data = await response.text()
            data = dict(parse_qsl(data))
        try:
            self.access_token = data["access_token"]
        except KeyError:
            raise HTTPBadRequest(reason="Failed to obtain OAuth access token.")
        finally:
            response.close()

        return self.access_token, data


class GoogleClient(OAuth2Client):

    """Support Google.
    * Dashboard: https://console.developers.google.com/project
    * Docs: https://developers.google.com/accounts/docs/OAuth2
    * API reference: https://developers.google.com/gdata/docs/directory
    * API explorer: https://developers.google.com/oauthplayground/
    """

    access_token_url = "https://accounts.google.com/o/oauth2/token"
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    base_url = "https://www.googleapis.com/plus/v1/"
    name = "google"
    user_info_url = "https://www.googleapis.com/userinfo/v2/me"

    @classmethod
    def user_parse(cls, data) -> UserInfo:
        """Parse information from provider."""
        return UserInfo(
            id=data.get("sub", data.get("id")),
            email=data.get("email"),
            verified_email=data.get("verified_email"),
            first_name=data.get("given_name"),
            last_name=data.get("family_name"),
            picture=data.get("picture"),
        )


class FacebookClient(OAuth2Client):

    """Support Facebook.
    * Dashboard: https://developers.facebook.com/apps
    * Docs: http://developers.facebook.com/docs/howtos/login/server-side-login/
    * API reference: http://developers.facebook.com/docs/reference/api/
    * API explorer: http://developers.facebook.com/tools/explorer
    """

    access_token_url = "https://graph.facebook.com/oauth/access_token"
    authorize_url = "https://www.facebook.com/dialog/oauth"
    base_url = "https://graph.facebook.com/v2.4"
    name = "facebook"
    user_info_url = "https://graph.facebook.com/me"

    async def user_info(self, **kwargs) -> Tuple[UserInfo, Dict]:
        """Facebook required fields-param."""
        params = kwargs.get("params", {})
        params[
            "fields"
        ] = "id,email,first_name,last_name,name,link,locale,gender,location"
        return await super(FacebookClient, self).user_info(params=params, **kwargs)

    @staticmethod
    def user_parse(data):
        """Parse information from provider."""
        id_ = data.get("id")
        location = data.get("location", {}).get("name")
        city, country = "", ""
        if location:
            split_location = location.split(", ")
            city = split_location[0].strip()
            if len(split_location) > 1:
                country = split_location[1].strip()
        return UserInfo(
            id=id_,
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            username=data.get("name"),
            picture="http://graph.facebook.com/{0}/picture?type=large".format(id_),
            link=data.get("link"),
            locale=data.get("locale"),
            gender=data.get("gender"),
            city=city,
            country=country,
        )

