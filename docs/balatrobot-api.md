# BalatroBot API

This page provides comprehensive API documentation for the BalatroBot Python framework. The API enables you to build automated bots that interact with the Balatro card game through a structured TCP communication protocol.

The API is organized into several key components: the `BalatroClient` for managing game connections and sending commands, enums that define game states and actions, exception classes for robust error handling, and data models that structure requests and responses between your bot and the game.

## Client

::: balatrobot.client.BalatroClient
options:
heading_level: 3

---

## Enums

::: balatrobot.enums.State
options:
heading_level: 3
::: balatrobot.enums.Actions
options:
heading_level: 3
::: balatrobot.enums.Decks
options:
heading_level: 3
::: balatrobot.enums.Stakes
options:
heading_level: 3
::: balatrobot.enums.ErrorCode
options:
heading_level: 3

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

### Request Models

::: balatrobot.models.StartRunRequest
::: balatrobot.models.BlindActionRequest
::: balatrobot.models.HandActionRequest
::: balatrobot.models.ShopActionRequest

### Game State Models

::: balatrobot.models.Card
::: balatrobot.models.Game
::: balatrobot.models.GameState

### Communication Models

::: balatrobot.models.ErrorResponse
::: balatrobot.models.APIRequest
::: balatrobot.models.APIResponse

## Usage Examples

For practical implementation examples:

- Follow the [Developing Bots](developing-bots.md) guide for complete bot setup
- Understand the underlying [Protocol API](protocol-api.md) for advanced usage
- Reference the [Installation](installation.md) guide for environment setup
