from __future__ import annotations

import asyncio
import unittest
from typing import Any

import httpx

from ucii import (
    UCIIAPIError,
    UCIIAuthenticationError,
    UCIIAuthorizationError,
    UCIIConflictError,
    UCIIError,
    UCIIPaymentRequiredError,
    UCIIResourceNotFoundError,
    UCIIServiceError,
    UCIITransportError,
    UCIIValidationError,
)
from ucii._transport import (
    AsyncHTTPTransport,
    HTTPTransport,
)


class PublicErrorContractTests(unittest.TestCase):
    def test_public_error_hierarchy_and_attributes(
        self,
    ) -> None:
        api_errors = (
            UCIIAuthenticationError,
            UCIIAuthorizationError,
            UCIIPaymentRequiredError,
            UCIIValidationError,
            UCIIResourceNotFoundError,
            UCIIConflictError,
            UCIIServiceError,
        )

        self.assertTrue(
            issubclass(UCIIAPIError, UCIIError)
        )

        for error_type in api_errors:
            with self.subTest(error_type=error_type.__name__):
                self.assertTrue(
                    issubclass(error_type, UCIIAPIError)
                )

        self.assertTrue(
            issubclass(UCIITransportError, UCIIError)
        )
        self.assertFalse(
            issubclass(UCIITransportError, UCIIAPIError)
        )

        source_details = {
            "field": "identity_id",
        }

        error = UCIIAPIError(
            "request failed",
            error_code="example_error",
            request_id="req-123",
            status_code=400,
            details=source_details,
        )

        self.assertEqual(
            str(error),
            "request failed",
        )
        self.assertEqual(
            error.message,
            "request failed",
        )
        self.assertEqual(
            error.error_code,
            "example_error",
        )
        self.assertEqual(
            error.request_id,
            "req-123",
        )
        self.assertEqual(
            error.status_code,
            400,
        )
        self.assertEqual(
            error.details,
            {
                "field": "identity_id",
            },
        )

        self.assertIsNot(
            error.details,
            source_details,
        )


class PublicSyncTransportErrorTests(unittest.TestCase):
    def make_transport(
        self,
        handler: Any,
        *,
        api_key: str | None = None,
        base_url: str = "https://example.invalid/",
    ) -> HTTPTransport:
        transport = HTTPTransport(
            base_url=base_url,
            api_key=api_key,
            timeout=7.5,
        )
        transport._client.close()
        transport._client = httpx.Client(
            base_url=transport.base_url,
            transport=httpx.MockTransport(handler),
            timeout=transport.timeout,
        )
        return transport

    def test_status_codes_map_to_public_errors(
        self,
    ) -> None:
        cases = (
            (400, UCIIAPIError),
            (401, UCIIAuthenticationError),
            (402, UCIIPaymentRequiredError),
            (403, UCIIAuthorizationError),
            (404, UCIIResourceNotFoundError),
            (409, UCIIConflictError),
            (422, UCIIValidationError),
            (500, UCIIServiceError),
            (503, UCIIServiceError),
        )

        for status_code, expected_type in cases:
            with self.subTest(
                status_code=status_code,
                expected_type=expected_type.__name__,
            ):
                def handler(
                    request: httpx.Request,
                    *,
                    status_code: int = status_code,
                ) -> httpx.Response:
                    return httpx.Response(
                        status_code,
                        request=request,
                        json={
                            "detail": "synthetic failure",
                        },
                    )

                transport = self.make_transport(handler)

                try:
                    with self.assertRaises(
                        expected_type
                    ) as caught:
                        transport.request(
                            "GET",
                            "/v1/example",
                        )

                    self.assertIs(
                        type(caught.exception),
                        expected_type,
                    )
                    self.assertEqual(
                        caught.exception.status_code,
                        status_code,
                    )
                    self.assertEqual(
                        caught.exception.message,
                        "synthetic failure",
                    )
                finally:
                    transport.close()

    def test_error_payload_fields_and_request_id_precedence(
        self,
    ) -> None:
        def handler(
            request: httpx.Request,
        ) -> httpx.Response:
            return httpx.Response(
                422,
                request=request,
                headers={
                    "x-request-id": "header-request-id",
                },
                json={
                    "detail": {
                        "message": "invalid identity",
                        "code": "invalid_identity",
                        "field": "identity_id",
                    },
                    "request_id": "body-request-id",
                },
            )

        transport = self.make_transport(handler)

        try:
            with self.assertRaises(
                UCIIValidationError
            ) as caught:
                transport.request(
                    "POST",
                    "/v1/example",
                )

            error = caught.exception

            self.assertEqual(
                error.message,
                "invalid identity",
            )
            self.assertEqual(
                error.error_code,
                "invalid_identity",
            )
            self.assertEqual(
                error.request_id,
                "header-request-id",
            )
            self.assertEqual(
                error.status_code,
                422,
            )
            self.assertEqual(
                error.details,
                {
                    "message": "invalid identity",
                    "code": "invalid_identity",
                    "field": "identity_id",
                },
            )
        finally:
            transport.close()

    def test_top_level_error_fields_are_preserved(
        self,
    ) -> None:
        def handler(
            request: httpx.Request,
        ) -> httpx.Response:
            return httpx.Response(
                409,
                request=request,
                json={
                    "detail": "credential conflict",
                    "error_code": "credential_conflict",
                    "request_id": "body-request-id",
                    "details": {
                        "credential_id": "cred-123",
                    },
                },
            )

        transport = self.make_transport(handler)

        try:
            with self.assertRaises(
                UCIIConflictError
            ) as caught:
                transport.request(
                    "POST",
                    "/v1/example",
                )

            error = caught.exception

            self.assertEqual(
                error.message,
                "credential conflict",
            )
            self.assertEqual(
                error.error_code,
                "credential_conflict",
            )
            self.assertEqual(
                error.request_id,
                "body-request-id",
            )
            self.assertEqual(
                error.details,
                {
                    "credential_id": "cred-123",
                },
            )
        finally:
            transport.close()

    def test_non_dict_detail_and_non_json_fallbacks(
        self,
    ) -> None:
        cases = (
            (
                httpx.Response(
                    400,
                    json={
                        "detail": [
                            "invalid",
                            "request",
                        ],
                    },
                ),
                "UCII API request failed with status 400",
                {
                    "detail": [
                        "invalid",
                        "request",
                    ],
                },
            ),
            (
                httpx.Response(
                    400,
                    content=b"not-json",
                    headers={
                        "content-type": "text/plain",
                    },
                ),
                "UCII API request failed with status 400",
                None,
            ),
        )

        for template, expected_message, expected_details in cases:
            with self.subTest(
                expected_details=expected_details
            ):
                def handler(
                    request: httpx.Request,
                    *,
                    template: httpx.Response = template,
                ) -> httpx.Response:
                    return httpx.Response(
                        template.status_code,
                        request=request,
                        headers=template.headers,
                        content=template.content,
                    )

                transport = self.make_transport(handler)

                try:
                    with self.assertRaises(
                        UCIIAPIError
                    ) as caught:
                        transport.request(
                            "GET",
                            "/v1/example",
                        )

                    self.assertIs(
                        type(caught.exception),
                        UCIIAPIError,
                    )
                    self.assertEqual(
                        caught.exception.message,
                        expected_message,
                    )
                    self.assertEqual(
                        caught.exception.details,
                        expected_details,
                    )
                finally:
                    transport.close()

    def test_default_bearer_and_override_headers(
        self,
    ) -> None:
        captured: list[httpx.Request] = []

        def handler(
            request: httpx.Request,
        ) -> httpx.Response:
            captured.append(request)
            return httpx.Response(
                200,
                request=request,
                json={"ok": True},
            )

        transport = self.make_transport(
            handler,
            api_key="public-test-key",
        )

        try:
            transport.request(
                "GET",
                "/v1/example",
            )
            transport.request(
                "GET",
                "/v1/example",
                headers={
                    "Authorization": "Custom proof",
                    "Accept": "application/problem+json",
                },
            )
        finally:
            transport.close()

        self.assertEqual(
            transport.base_url,
            "https://example.invalid",
        )
        self.assertEqual(
            transport.timeout,
            7.5,
        )

        self.assertEqual(
            captured[0].headers["accept"],
            "application/json",
        )
        self.assertEqual(
            captured[0].headers["content-type"],
            "application/json",
        )
        self.assertEqual(
            captured[0].headers["authorization"],
            "Bearer public-test-key",
        )

        self.assertEqual(
            captured[1].headers["authorization"],
            "Custom proof",
        )
        self.assertEqual(
            captured[1].headers["accept"],
            "application/problem+json",
        )
        self.assertEqual(
            captured[1].headers["content-type"],
            "application/json",
        )

    def test_httpx_failure_maps_to_transport_error(
        self,
    ) -> None:
        def handler(
            request: httpx.Request,
        ) -> httpx.Response:
            raise httpx.ConnectError(
                "synthetic connection failure",
                request=request,
            )

        transport = self.make_transport(handler)

        try:
            with self.assertRaises(
                UCIITransportError
            ) as caught:
                transport.request(
                    "GET",
                    "/v1/example",
                )

            self.assertIn(
                "synthetic connection failure",
                caught.exception.message,
            )
            self.assertIsInstance(
                caught.exception.__cause__,
                httpx.ConnectError,
            )
        finally:
            transport.close()


class PublicAsyncTransportErrorTests(unittest.TestCase):
    def test_async_error_and_transport_mapping_match_sync(
        self,
    ) -> None:
        async def exercise() -> None:
            async def error_handler(
                request: httpx.Request,
            ) -> httpx.Response:
                return httpx.Response(
                    403,
                    request=request,
                    headers={
                        "x-request-id": "async-request-id",
                    },
                    json={
                        "detail": {
                            "message": "not authorized",
                            "error_code": "not_authorized",
                        },
                    },
                )

            transport = AsyncHTTPTransport(
                base_url="https://example.invalid/",
                api_key="async-key",
                timeout=8.5,
            )
            await transport._client.aclose()
            transport._client = httpx.AsyncClient(
                base_url=transport.base_url,
                transport=httpx.MockTransport(
                    error_handler
                ),
                timeout=transport.timeout,
            )

            try:
                with self.assertRaises(
                    UCIIAuthorizationError
                ) as caught:
                    await transport.request(
                        "GET",
                        "/v1/example",
                    )

                error = caught.exception

                self.assertEqual(
                    error.message,
                    "not authorized",
                )
                self.assertEqual(
                    error.error_code,
                    "not_authorized",
                )
                self.assertEqual(
                    error.request_id,
                    "async-request-id",
                )
                self.assertEqual(
                    error.status_code,
                    403,
                )
            finally:
                await transport.close()

            async def failure_handler(
                request: httpx.Request,
            ) -> httpx.Response:
                raise httpx.ConnectError(
                    "synthetic async connection failure",
                    request=request,
                )

            transport = AsyncHTTPTransport(
                base_url="https://example.invalid/",
            )
            await transport._client.aclose()
            transport._client = httpx.AsyncClient(
                base_url=transport.base_url,
                transport=httpx.MockTransport(
                    failure_handler
                ),
            )

            try:
                with self.assertRaises(
                    UCIITransportError
                ) as caught:
                    await transport.request(
                        "GET",
                        "/v1/example",
                    )

                self.assertIn(
                    "synthetic async connection failure",
                    caught.exception.message,
                )
                self.assertIsInstance(
                    caught.exception.__cause__,
                    httpx.ConnectError,
                )
            finally:
                await transport.close()

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
