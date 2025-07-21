# BalatroBot API

This page provides comprehensive API documentation for the BalatroBot Python framework. The API enables you to build automated bots that interact with the Balatro card game through a structured TCP communication protocol.

The API is organized into several key components: the `BalatroClient` for managing game connections and sending commands, enums that define game states and actions, exception classes for robust error handling, and data models that structure requests and responses between your bot and the game.

## Client

The `BalatroClient` is the main interface for communicating with the Balatro game through TCP connections. It handles connection management, message serialization, and error handling.

::: balatrobot.client.BalatroClient
    options:
      heading_level: 3
      show_source: true

---

## Enums

::: balatrobot.enums.State
    options:
      heading_level: 3
      show_source: true
::: balatrobot.enums.Actions
    options:
      heading_level: 3
      show_source: true
::: balatrobot.enums.Decks
    options:
      heading_level: 3
      show_source: true
::: balatrobot.enums.Stakes
    options:
      heading_level: 3
      show_source: true
::: balatrobot.enums.ErrorCode
    options:
      heading_level: 3
      show_source: true

---

## Exceptions

### Connection and Socket Errors

::: balatrobot.exceptions.SocketCreateFailedError
::: balatrobot.exceptions.SocketBindFailedError
::: balatrobot.exceptions.ConnectionFailedError

### Game State and Logic Errors

::: balatrobot.exceptions.InvalidGameStateError
::: balatrobot.exceptions.InvalidActionError
::: balatrobot.exceptions.DeckNotFoundError
::: balatrobot.exceptions.InvalidCardIndexError
::: balatrobot.exceptions.NoDiscardsLeftError

### API and Parameter Errors

::: balatrobot.exceptions.InvalidJSONError
::: balatrobot.exceptions.MissingNameError
::: balatrobot.exceptions.MissingArgumentsError
::: balatrobot.exceptions.UnknownFunctionError
::: balatrobot.exceptions.InvalidArgumentsError
::: balatrobot.exceptions.InvalidParameterError
::: balatrobot.exceptions.ParameterOutOfRangeError
::: balatrobot.exceptions.MissingGameObjectError

---

## Models

The BalatroBot API uses Pydantic models to provide type-safe data structures that exactly match the game's internal state representation. All models inherit from `BalatroBaseModel` which provides consistent validation and serialization.

#### Base Model

::: balatrobot.models.BalatroBaseModel

### Request Models

These models define the structure for specific API requests:

::: balatrobot.models.StartRunRequest
::: balatrobot.models.BlindActionRequest
::: balatrobot.models.HandActionRequest
::: balatrobot.models.ShopActionRequest

### Game State Models

The game state models provide comprehensive access to all Balatro game information, structured hierarchically to match the Lua API:

#### Root Game State

::: balatrobot.models.G

#### Game Information

::: balatrobot.models.GGame
::: balatrobot.models.GGameCurrentRound
::: balatrobot.models.GGameLastBlind
::: balatrobot.models.GGamePreviousRound
::: balatrobot.models.GGameProbabilities
::: balatrobot.models.GGamePseudorandom
::: balatrobot.models.GGameRoundBonus
::: balatrobot.models.GGameRoundScores
::: balatrobot.models.GGameSelectedBack
::: balatrobot.models.GGameShop
::: balatrobot.models.GGameStartingParams
::: balatrobot.models.GGameTags

#### Hand Management

::: balatrobot.models.GHand
::: balatrobot.models.GHandCards
::: balatrobot.models.GHandCardsBase
::: balatrobot.models.GHandCardsConfig
::: balatrobot.models.GHandCardsConfigCard
::: balatrobot.models.GHandConfig

#### Joker Information

::: balatrobot.models.GJokersCards
::: balatrobot.models.GJokersCardsConfig

### Communication Models

These models handle the communication protocol between your bot and the game:

::: balatrobot.models.APIRequest
::: balatrobot.models.APIResponse
::: balatrobot.models.ErrorResponse
::: balatrobot.models.JSONLLogEntry

## Usage Examples

For practical implementation examples:

- Follow the [Developing Bots](developing-bots.md) guide for complete bot setup
- Understand the underlying [Protocol API](protocol-api.md) for advanced usage
- Reference the [Installation](installation.md) guide for environment setup
