"""Tests for exception handling and error response creation."""

from balatrobot.enums import ErrorCode
from balatrobot.exceptions import (
    BalatroError,
    ConnectionFailedError,
    InvalidJSONError,
    create_exception_from_error_response,
)


class TestBalatroError:
    """Test suite for BalatroError base class."""

    def test_repr_method(self):
        """Test __repr__ method returns correct string representation."""
        error = BalatroError(
            message="Test error message",
            error_code=ErrorCode.INVALID_JSON,
            state=5,
        )

        expected = (
            "BalatroError(message='Test error message', error_code='E001', state=5)"
        )
        assert repr(error) == expected

    def test_repr_method_with_none_state(self):
        """Test __repr__ method with None state."""
        error = BalatroError(
            message="Test error",
            error_code="E008",
            state=None,
        )

        expected = "BalatroError(message='Test error', error_code='E008', state=None)"
        assert repr(error) == expected


class TestCreateExceptionFromErrorResponse:
    """Test suite for create_exception_from_error_response function."""

    def test_create_exception_with_context(self):
        """Test creating exception with context field present."""
        error_response = {
            "error": "Connection failed",
            "error_code": "E008",
            "state": 1,
            "context": {"host": "127.0.0.1", "port": 12346},
        }

        exception = create_exception_from_error_response(error_response)

        assert isinstance(exception, ConnectionFailedError)
        assert exception.message == "Connection failed"
        assert exception.error_code == ErrorCode.CONNECTION_FAILED
        assert exception.state == 1
        assert exception.context == {"host": "127.0.0.1", "port": 12346}

    def test_create_exception_without_context(self):
        """Test creating exception without context field."""
        error_response = {
            "error": "Invalid JSON format",
            "error_code": "E001",
            "state": 11,
        }

        exception = create_exception_from_error_response(error_response)

        assert isinstance(exception, InvalidJSONError)
        assert exception.message == "Invalid JSON format"
        assert exception.error_code == ErrorCode.INVALID_JSON
        assert exception.state == 11
        assert exception.context == {}

    def test_create_exception_with_different_error_code(self):
        """Test creating exception with different error code."""
        error_response = {
            "error": "Invalid parameter",
            "error_code": "E010",
            "state": 2,
        }

        exception = create_exception_from_error_response(error_response)

        # Should create the correct exception type based on error code
        assert hasattr(exception, "message")
        assert exception.message == "Invalid parameter"
        assert exception.error_code.value == "E010"
        assert exception.state == 2
