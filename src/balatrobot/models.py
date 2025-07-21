"""Pydantic models for BalatroBot API matching Lua types structure."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import State


class BalatroBaseModel(BaseModel):
    """Base model for all BalatroBot API models."""

    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=True,
    )


# =============================================================================
# Request Models (keep existing - they match Lua argument types)
# =============================================================================


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


# =============================================================================
# Game State Models (matching src/lua/types.lua)
# =============================================================================


class GGameTags(BalatroBaseModel):
    """Game tags model matching GGameTags in Lua types."""

    key: str = Field("", description="Tag ID (e.g., 'tag_foil')")
    name: str = Field("", description="Tag display name (e.g., 'Foil Tag')")


class GGameLastBlind(BalatroBaseModel):
    """Last blind info matching GGameLastBlind in Lua types."""

    boss: bool = Field(False, description="Whether the last blind was a boss")
    name: str = Field("", description="Name of the last blind")


class GGameCurrentRound(BalatroBaseModel):
    """Current round info matching GGameCurrentRound in Lua types."""

    discards_left: int = Field(0, description="Number of discards remaining")
    discards_used: int = Field(0, description="Number of discards used")
    hands_left: int = Field(0, description="Number of hands remaining")
    hands_played: int = Field(0, description="Number of hands played")
    voucher: dict[str, Any] = Field(
        default_factory=dict, description="Vouchers for this round"
    )

    @field_validator("voucher", mode="before")
    @classmethod
    def convert_empty_list_to_dict(cls, v):
        """Convert empty list to empty dict."""
        return {} if v == [] else v


class GGameSelectedBack(BalatroBaseModel):
    """Selected deck info matching GGameSelectedBack in Lua types."""

    name: str = Field("", description="Name of the selected deck")


class GGameShop(BalatroBaseModel):
    """Shop configuration matching GGameShop in Lua types."""

    joker_max: int = Field(0, description="Maximum jokers in shop")


class GGameStartingParams(BalatroBaseModel):
    """Starting parameters matching GGameStartingParams in Lua types."""

    boosters_in_shop: int = Field(0, description="Number of boosters in shop")
    reroll_cost: int = Field(0, description="Cost to reroll shop")
    hand_size: int = Field(0, description="Starting hand size")
    hands: int = Field(0, description="Starting hands per round")
    ante_scaling: int = Field(0, description="Ante scaling factor")
    consumable_slots: int = Field(0, description="Number of consumable slots")
    dollars: int = Field(0, description="Starting money")
    discards: int = Field(0, description="Starting discards per round")
    joker_slots: int = Field(0, description="Number of joker slots")
    vouchers_in_shop: int = Field(0, description="Number of vouchers in shop")


class GGamePreviousRound(BalatroBaseModel):
    """Previous round info matching GGamePreviousRound in Lua types."""

    dollars: int = Field(0, description="Dollars from previous round")


class GGameProbabilities(BalatroBaseModel):
    """Game probabilities matching GGameProbabilities in Lua types."""

    normal: float = Field(1.0, description="Normal probability modifier")


class GGamePseudorandom(BalatroBaseModel):
    """Pseudorandom data matching GGamePseudorandom in Lua types."""

    seed: str = Field("", description="Pseudorandom seed")


class GGameRoundBonus(BalatroBaseModel):
    """Round bonus matching GGameRoundBonus in Lua types."""

    next_hands: int = Field(0, description="Bonus hands for next round")
    discards: int = Field(0, description="Bonus discards")


class GGameRoundScores(BalatroBaseModel):
    """Round scores matching GGameRoundScores in Lua types."""

    cards_played: dict[str, Any] = Field(
        default_factory=dict, description="Cards played stats"
    )
    cards_discarded: dict[str, Any] = Field(
        default_factory=dict, description="Cards discarded stats"
    )
    furthest_round: dict[str, Any] = Field(
        default_factory=dict, description="Furthest round stats"
    )
    furthest_ante: dict[str, Any] = Field(
        default_factory=dict, description="Furthest ante stats"
    )


class GGame(BalatroBaseModel):
    """Game state matching GGame in Lua types."""

    bankrupt_at: int = Field(0, description="Money threshold for bankruptcy")
    base_reroll_cost: int = Field(0, description="Base cost for rerolling shop")
    blind_on_deck: str = Field("", description="Current blind type")
    bosses_used: dict[str, int] = Field(
        default_factory=dict, description="Bosses used in run"
    )
    chips: int = Field(0, description="Current chip count")
    current_round: GGameCurrentRound | None = Field(
        None, description="Current round information"
    )
    discount_percent: int = Field(0, description="Shop discount percentage")
    dollars: int = Field(0, description="Current money amount")
    hands_played: int = Field(0, description="Total hands played in the run")
    inflation: int = Field(0, description="Current inflation rate")
    interest_amount: int = Field(0, description="Interest amount per dollar")
    interest_cap: int = Field(0, description="Maximum interest that can be earned")
    last_blind: GGameLastBlind | None = Field(
        None, description="Last blind information"
    )
    max_jokers: int = Field(0, description="Maximum number of jokers allowed")
    planet_rate: int = Field(0, description="Probability for planet cards in shop")
    playing_card_rate: int = Field(
        0, description="Probability for playing cards in shop"
    )
    previous_round: GGamePreviousRound | None = Field(
        None, description="Previous round information"
    )
    probabilities: GGameProbabilities | None = Field(
        None, description="Various game probabilities"
    )
    pseudorandom: GGamePseudorandom | None = Field(
        None, description="Pseudorandom seed data"
    )
    round: int = Field(0, description="Current round number")
    round_bonus: GGameRoundBonus | None = Field(
        None, description="Round bonus information"
    )
    round_scores: GGameRoundScores | None = Field(
        None, description="Round scoring data"
    )
    seeded: bool = Field(False, description="Whether the run uses a seed")
    selected_back: GGameSelectedBack | None = Field(
        None, description="Selected deck information"
    )
    shop: GGameShop | None = Field(None, description="Shop configuration")
    skips: int = Field(0, description="Number of skips used")
    smods_version: str = Field("", description="SMODS version")
    stake: int = Field(0, description="Current stake level")
    starting_params: GGameStartingParams | None = Field(
        None, description="Starting parameters"
    )
    tags: list[GGameTags] = Field(default_factory=list, description="Array of tags")
    tarot_rate: int = Field(0, description="Probability for tarot cards in shop")
    uncommon_mod: int = Field(0, description="Modifier for uncommon joker probability")
    unused_discards: int = Field(0, description="Unused discards from previous round")
    used_vouchers: dict[str, bool] | list = Field(
        default_factory=dict, description="Vouchers used in run"
    )
    voucher_text: str = Field("", description="Voucher text display")
    win_ante: int = Field(0, description="Ante required to win")
    won: bool = Field(False, description="Whether the run is won")

    @field_validator("bosses_used", "used_vouchers", mode="before")
    @classmethod
    def convert_empty_list_to_dict(cls, v):
        """Convert empty list to empty dict."""
        return {} if v == [] else v

    @field_validator(
        "previous_round",
        "probabilities",
        "pseudorandom",
        "round_bonus",
        "round_scores",
        "shop",
        "starting_params",
        mode="before",
    )
    @classmethod
    def convert_empty_list_to_none(cls, v):
        """Convert empty list to None for optional nested objects."""
        return None if v == [] else v


class GHandCardsBase(BalatroBaseModel):
    """Hand card base properties matching GHandCardsBase in Lua types."""

    id: Any = Field(None, description="Card ID")
    name: str = Field("", description="Base card name")
    nominal: str = Field("", description="Nominal value")
    original_value: str = Field("", description="Original card value")
    suit: str = Field("", description="Card suit")
    times_played: int = Field(0, description="Times this card has been played")
    value: str = Field("", description="Current card value")

    @field_validator("nominal", "original_value", "value", mode="before")
    @classmethod
    def convert_int_to_string(cls, v):
        """Convert integer values to strings."""
        return str(v) if isinstance(v, int) else v


class GHandCardsConfigCard(BalatroBaseModel):
    """Hand card config card data matching GHandCardsConfigCard in Lua types."""

    name: str = Field("", description="Card name")
    suit: str = Field("", description="Card suit")
    value: str = Field("", description="Card value")


class GHandCardsConfig(BalatroBaseModel):
    """Hand card configuration matching GHandCardsConfig in Lua types."""

    card_key: str = Field("", description="Unique card identifier")
    card: GHandCardsConfigCard | None = Field(None, description="Card-specific data")


class GHandCards(BalatroBaseModel):
    """Hand card matching GHandCards in Lua types."""

    label: str = Field("", description="Display label of the card")
    base: GHandCardsBase | None = Field(None, description="Base card properties")
    config: GHandCardsConfig | None = Field(None, description="Card configuration")
    debuff: bool = Field(False, description="Whether card is debuffed")
    facing: str = Field("front", description="Card facing direction")
    highlighted: bool = Field(False, description="Whether card is highlighted")


class GHandConfig(BalatroBaseModel):
    """Hand configuration matching GHandConfig in Lua types."""

    card_count: int = Field(0, description="Number of cards in hand")
    card_limit: int = Field(0, description="Maximum cards allowed in hand")
    highlighted_limit: int = Field(
        0, description="Maximum cards that can be highlighted"
    )


class GHand(BalatroBaseModel):
    """Hand structure matching GHand in Lua types."""

    cards: list[GHandCards] = Field(
        default_factory=list, description="Array of cards in hand"
    )
    config: GHandConfig | None = Field(None, description="Hand configuration")


class GJokersCardsConfig(BalatroBaseModel):
    """Joker card configuration matching GJokersCardsConfig in Lua types."""

    center: dict[str, Any] = Field(
        default_factory=dict, description="Center configuration for joker"
    )


class GJokersCards(BalatroBaseModel):
    """Joker card matching GJokersCards in Lua types."""

    label: str = Field("", description="Display label of the joker")
    config: GJokersCardsConfig | None = Field(None, description="Joker configuration")


class G(BalatroBaseModel):
    """Root game state response matching G in Lua types."""

    state: Any = Field(None, description="Current game state enum value")
    game: GGame | None = Field(
        None, description="Game information (null if not in game)"
    )
    hand: GHand | None = Field(
        None, description="Hand information (null if not available)"
    )
    jokers: list[GJokersCards] | dict[str, Any] = Field(
        default_factory=list, description="Jokers structure (can be list or dict)"
    )

    @field_validator("hand", mode="before")
    @classmethod
    def convert_empty_list_to_none_for_hand(cls, v):
        """Convert empty list to None for hand field."""
        return None if v == [] else v

    @property
    def state_enum(self) -> State | None:
        """Get the state as an enum value."""
        return State(self.state) if self.state is not None else None


class ErrorResponse(BalatroBaseModel):
    """Model for API error responses matching Lua ErrorResponse."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Standardized error code")
    state: Any = Field(..., description="Current game state when error occurred")
    context: dict[str, Any] | None = Field(None, description="Additional error context")


# =============================================================================
# API Message Models
# =============================================================================


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
    game_state: G = Field(
        ...,
        description="Complete game state before the function execution",
    )
