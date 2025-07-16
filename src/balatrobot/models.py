"""Pydantic models for BalatroBot API requests and responses."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .enums import State


class BalatroBaseModel(BaseModel):
    """Base model for all BalatroBot API models."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=True,
    )


# Request Models
class StartRunRequest(BalatroBaseModel):
    """Request model for starting a new run."""

    deck: str = Field(..., description="Name of the deck to use")
    stake: int = Field(1, ge=1, le=8, description="Stake level (1-8)")
    seed: str | None = Field(None, description="Optional seed for the run")
    challenge: str | None = Field(None, description="Optional challenge name")


class BlindActionRequest(BalatroBaseModel):
    """Request model for skip or select blind actions."""

    action: Literal["skip", "select"] = Field(
        ..., description="Action to take with the blind"
    )


class HandActionRequest(BalatroBaseModel):
    """Request model for playing hand or discarding cards."""

    action: Literal["play_hand", "discard"] = Field(
        ..., description="Action to take with the cards"
    )
    cards: list[int] = Field(
        ..., min_length=1, max_length=5, description="List of card indices (0-indexed)"
    )


class ShopActionRequest(BalatroBaseModel):
    """Request model for shop actions."""

    action: Literal["next_round"] = Field(..., description="Shop action to perform")


# Response Models
class Card(BalatroBaseModel):
    """Model for a playing card."""

    config: dict[str, Any] = Field(..., description="Card configuration data")
    label: str = Field(..., description="Card label")


class Game(BalatroBaseModel):
    """Model for game information."""

    blind_on_deck: str | None = Field(None, description="Current blind on deck")
    hands_played: int = Field(0, description="Number of hands played this round")
    current_round: dict[str, Any] = Field(
        default_factory=dict, description="Current round information"
    )
    skips: int = Field(0, description="Number of skips available")
    discount_percent: int = Field(0, description="Shop discount percentage")
    interest_cap: int = Field(0, description="Interest cap amount")
    chips: int = Field(0, description="Current chips")
    inflation: int = Field(0, description="Current inflation amount")
    round: int = Field(0, description="Current round number")
    dollars: int = Field(0, description="Current money amount")
    max_jokers: int = Field(0, description="Maximum number of jokers")
    bankrupt_at: int = Field(0, description="Bankrupt threshold")


class GameState(BalatroBaseModel):
    """Model for the complete game state."""

    state: int = Field(..., description="Current game state as integer")
    game: Game | None = Field(None, description="Game information")
    hand: list[Card] = Field(default_factory=list, description="Cards in hand")
    jokers: list[dict[str, Any]] = Field(
        default_factory=list, description="Joker cards"
    )

    @property
    def state_enum(self) -> State:
        """Get the state as an enum value."""
        return State(self.state)


class ErrorResponse(BalatroBaseModel):
    """Model for API error responses."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Standardized error code")
    state: int = Field(..., description="Current game state when error occurred")
    context: dict[str, Any] | None = Field(None, description="Additional error context")


# API Message Models
class APIRequest(BalatroBaseModel):
    """Model for API requests sent to the game."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Function name to call")
    arguments: dict[str, Any] | list = Field(
        ..., description="Arguments for the function"
    )


class APIResponse(BalatroBaseModel):
    """Model for API responses from the game."""

    model_config = ConfigDict(extra="allow")


# JSONL Log Entry
class JSONLLogEntry(BalatroBaseModel):
    """Model for JSONL log entries that record game actions."""

    timestamp_ms: int = Field(
        ...,
        description="Unix timestamp in milliseconds when the action occurred",
    )
    function: APIRequest = Field(
        ...,
        description="The game function that was called",
    )
    game_state: GameState = Field(
        ...,
        description="Complete game state before the function execution",
    )
