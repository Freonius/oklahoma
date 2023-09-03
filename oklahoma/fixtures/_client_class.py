from typing import cast, Iterable, Mapping

# pylint: disable=redefined-builtin
from re import split, compile, Pattern

# pylint: enable=redefined-builtin


try:
    from pytest import fixture
    from starlette.testclient import TestClient
    from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT, TimeoutTypes
    from httpx._types import (
        HeaderTypes,
        QueryParamTypes,
        URLTypes,
        CookieTypes,
        AuthTypes,
        RequestContent,
        RequestFiles,
    )
    from ._response_class import TestResponse

    _RequestData = Mapping[str, str | Iterable[str]]
    _class_pattern: Pattern[str] = compile(r"([A-Z][a-z0-9]+)")

    class APIFixture:
        api: TestClient
        __prefix__: str | None = None
        __use_class_name_as_prefix__: bool = True

        def __solve_url(self, url: URLTypes | None) -> str:
            _prefix: object | None = None
            if self.__use_class_name_as_prefix__ is True:
                _name = self.__class__.__name__.removeprefix("Test")
                _prefix = "/".join(
                    [_.strip().lower() for _ in split(_class_pattern, _name)]
                )
                if _prefix.strip() == "":
                    _prefix = "/"
                if not _prefix.startswith("/"):
                    _prefix = "/" + _prefix
                if not _prefix.endswith("/"):
                    _prefix = _prefix + "/"
                _prefix = _prefix.replace("//", "/")
            elif self.__use_class_name_as_prefix__ is False:
                _prefix = getattr(self, "__prefix__", None)
            if not isinstance(_prefix, str):
                _prefix = None
            if _prefix is None:
                if url is not None:
                    return str(url)
                raise ValueError("Could not solve prefix")
            if url is None:
                return _prefix
            if isinstance(url, str):
                return f"{_prefix}{url}".replace("//", "/")
            return f"{_prefix}{str(url)}".replace("//", "/")

        @fixture(autouse=True)
        def _client(self, client: TestClient) -> None:
            self.api = client

        def get(
            self,
            url: URLTypes | None = None,
            *,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send a `GET` request."""
            url = self.__solve_url(url)
            resp = self.api.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

        def options(
            self,
            url: URLTypes | None = None,
            *,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send an `OPTIONS` request."""
            url = self.__solve_url(url)
            resp = self.api.options(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

        def head(
            self,
            url: URLTypes | None = None,
            *,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send a `HEAD` request."""
            url = self.__solve_url(url)
            resp = self.api.head(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

        def post(
            self,
            url: URLTypes | None = None,
            *,
            content: RequestContent | None = None,
            data: _RequestData | None = None,
            files: RequestFiles | None = None,
            json: object | None = None,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send a `POST` request."""
            url = self.__solve_url(url)
            resp = self.api.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

        def put(
            self,
            url: URLTypes | None = None,
            *,
            content: RequestContent | None = None,
            data: _RequestData | None = None,
            files: RequestFiles | None = None,
            json: object | None = None,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send a `PUT` request."""
            url = self.__solve_url(url)
            resp = self.api.put(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

        def patch(
            self,
            url: URLTypes | None = None,
            *,
            content: RequestContent | None = None,
            data: _RequestData | None = None,
            files: RequestFiles | None = None,
            json: object | None = None,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send a `PATCH` request."""
            url = self.__solve_url(url)
            resp = self.api.patch(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

        def delete(
            self,
            url: URLTypes | None = None,
            *,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            follow_redirects: bool | None = None,
            allow_redirects: bool | None = None,
            timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
            extensions: dict[str, object] | None = None,
        ) -> "TestResponse":
            """Send a `DELETE` request."""
            url = self.__solve_url(url)
            resp = self.api.delete(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                allow_redirects=allow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
            resp.__class__ = TestResponse
            return cast(TestResponse, resp)

except ImportError:
    pass
