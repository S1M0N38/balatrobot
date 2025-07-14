"""Custom exceptions for BalatroBot API."""

from typing import Any

from .enums import ErrorCode


class BalatroError(Exception):
    """Base exception for all BalatroBot errors."""

    def __init__(
        self,
        message: str,
        error_code: str | ErrorCode,
        state: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = (
            error_code if isinstance(error_code, ErrorCode) else ErrorCode(error_code)
        )
        self.state = state
        self.context = context or {}

    def __str__(self) -> str:
        return f"{self.error_code.value}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code.value}', state={self.state})"


# Protocol errors (E001-E005)
class InvalidJSONError(BalatroError):
    """Invalid JSON in request (E001)."""

    pass


class MissingNameError(BalatroError):
    """Message missing required 'name' field (E002)."""

    pass


class MissingArgumentsError(BalatroError):
    """Message missing required 'arguments' field (E003)."""

    pass


class UnknownFunctionError(BalatroError):
    """Unknown function name (E004)."""

    pass


class InvalidArgumentsError(BalatroError):
    """Invalid arguments provided (E005)."""

    pass


# Network errors (E006-E008)
class SocketCreateFailedError(BalatroError):
    """Socket creation failed (E006)."""

    pass


class SocketBindFailedError(BalatroError):
    """Socket bind failed (E007)."""

    pass


class ConnectionFailedError(BalatroError):
    """Connection failed (E008)."""

    pass


# Validation errors (E009-E012)
class InvalidGameStateError(BalatroError):
    """Invalid game state for requested action (E009)."""

    pass


class InvalidParameterError(BalatroError):
    """Invalid or missing required parameter (E010)."""

    pass


class ParameterOutOfRangeError(BalatroError):
    """Parameter value out of valid range (E011)."""

    pass


class MissingGameObjectError(BalatroError):
    """Required game object missing (E012)."""

    pass


# Game logic errors (E013-E016)
class DeckNotFoundError(BalatroError):
    """Deck not found (E013)."""

    pass


class InvalidCardIndexError(BalatroError):
    """Invalid card index (E014)."""

    pass


class NoDiscardsLeftError(BalatroError):
    """No discards remaining (E015)."""

    pass


class InvalidActionError(BalatroError):
    """Invalid action for current context (E016)."""

    pass


# Mapping from error codes to exception classes
ERROR_CODE_TO_EXCEPTION = {
    ErrorCode.INVALID_JSON: InvalidJSONError,
    ErrorCode.MISSING_NAME: MissingNameError,
    ErrorCode.MISSING_ARGUMENTS: MissingArgumentsError,
    ErrorCode.UNKNOWN_FUNCTION: UnknownFunctionError,
    ErrorCode.INVALID_ARGUMENTS: InvalidArgumentsError,
    ErrorCode.SOCKET_CREATE_FAILED: SocketCreateFailedError,
    ErrorCode.SOCKET_BIND_FAILED: SocketBindFailedError,
    ErrorCode.CONNECTION_FAILED: ConnectionFailedError,
    ErrorCode.INVALID_GAME_STATE: InvalidGameStateError,
    ErrorCode.INVALID_PARAMETER: InvalidParameterError,
    ErrorCode.PARAMETER_OUT_OF_RANGE: ParameterOutOfRangeError,
    ErrorCode.MISSING_GAME_OBJECT: MissingGameObjectError,
    ErrorCode.DECK_NOT_FOUND: DeckNotFoundError,
    ErrorCode.INVALID_CARD_INDEX: InvalidCardIndexError,
    ErrorCode.NO_DISCARDS_LEFT: NoDiscardsLeftError,
    ErrorCode.INVALID_ACTION: InvalidActionError,
}


def create_exception_from_error_response(
    error_response: dict[str, Any],
) -> BalatroError:
    """Create an appropriate exception from an error response."""
    error_code = ErrorCode(error_response["error_code"])
    exception_class = ERROR_CODE_TO_EXCEPTION.get(error_code, BalatroError)

    return exception_class(
        message=error_response["error"],
        error_code=error_code,
        state=error_response["state"],
        context=error_response.get("context"),
    )
