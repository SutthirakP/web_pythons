"""CORS homework: allow every HTTP method except HEAD, and a /foo route to prove it.

Why a subclass is needed
------------------------
Browsers only send a preflight (OPTIONS) for "non-simple" requests. HEAD, GET and
POST without custom headers are "simple", so `fetch(url, {method: "HEAD"})` goes
straight to the server with no preflight. Starlette's CORSMiddleware only checks
`allow_methods` during the preflight, so on its own it would still add
`Access-Control-Allow-Origin` to the HEAD response and the browser would allow it.

MethodCheckingCORSMiddleware also checks the method on simple requests: a method
that isn't allowed gets no CORS headers, so the browser blocks the response.

Note: CORS is enforced by the browser, not the server. The HEAD request still
reaches /foo (it shows up in the server log as 200) - the browser just refuses to
hand the response to the page. curl or /docs are not affected.
"""

from fastapi import APIRouter, Response
from starlette.datastructures import Headers
from starlette.middleware.cors import CORSMiddleware
from starlette.types import Receive, Scope, Send

ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
# every method except HEAD
ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


class MethodCheckingCORSMiddleware(CORSMiddleware):
    async def simple_response(
        self, scope: Scope, receive: Receive, send: Send, request_headers: Headers
    ) -> None:
        if scope["method"] not in self.allow_methods:
            # pass through without any Access-Control-* headers -> browser blocks it
            await self.app(scope, receive, send)
            return
        await super().simple_response(scope, receive, send, request_headers)


router = APIRouter(tags=["cors homework"])


@router.head("/foo")
def head_foo() -> Response:
    # HEAD = "GET without the body": only status + headers come back
    return Response(headers={"X-Foo": "hello from HEAD"})


@router.get("/foo")
def get_foo():
    # same URL, allowed method - used on the page to compare with HEAD
    return {"message": "GET /foo is allowed by CORS"}
