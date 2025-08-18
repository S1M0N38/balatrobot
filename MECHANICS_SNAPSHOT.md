# Mechanics Snapshot System

This document describes the new mechanics-only snapshot and rehydration system implemented in BalatroBot.

## Overview

The mechanics snapshot system provides:

1. **Automatic mechanics-only serialization** - Strips UI elements, functions, and non-serializable content
2. **Efficient state snapshots** - Significantly smaller than full game state
3. **Robust rehydration via baseline patching** - Creates baseline run then applies mechanics patch
4. **Easy test state management** - Rapid state reset for testing

## Implementation

### Lua Components

#### `utils.serialize_mechanics_only(obj, visited)`

Generic serializer that walks any table and strips non-serializable content:

- Filters out functions, userdata, metatables
- Removes UI-related fields (children, pos, sprite, etc.)
- Skips capital-letter keys (UI convention in Balatro)
- Handles circular references

#### `utils.get_mechanics_snapshot()`

Creates mechanics-only snapshot by applying the serializer to:

- G.GAME (core game state)
- G.hand, G.jokers, G.consumeables (card areas)
- G.shop\_\* (shop state)
- G.deck, G.discard, G.play (other card areas)

#### `utils.rehydrate_game_state(snapshot, deck_key, stake)`

Re-hydrates state by:

1. Creating baseline run with `G.FUNCS.start_run()`
2. Deep-merging mechanics patch into baseline
3. Preserving UI scaffolding while restoring gameplay state

#### Helper Functions

- `utils.deep_merge()` - Recursive table merging
- `utils.create_restore_point()` - Complete restore point with metadata
- `utils.restore_from_point()` - Restore from complete restore point

### Python Client API

#### `client.get_mechanics_snapshot() -> dict`

Get mechanics-only snapshot of current game state.

#### `client.rehydrate_game_state(snapshot, deck_key="b_red", stake=1) -> bool`

Re-hydrate game state from mechanics snapshot.

#### `client.create_restore_point(label=None) -> dict`

Create complete restore point with snapshot and metadata.

#### `client.restore_from_point(restore_point) -> bool`

Restore from complete restore point.

## Usage Examples

### Basic Snapshot and Restore

```python
from balatrobot import BalatroClient

with BalatroClient() as client:
    # Save current state
    snapshot = client.get_mechanics_snapshot()
    
    # ... perform some actions that change state ...
    
    # Restore to saved state
    client.rehydrate_game_state(snapshot)
```

### Test State Management

```python
def test_sequence():
    with BalatroClient() as client:
        # Set up initial test state
        client.send_message("start_run", {"deck": "Red Deck", "stake": 1})
        
        # Save baseline for multiple tests
        baseline = client.get_mechanics_snapshot()
        
        for test_case in test_cases:
            # Restore to baseline before each test
            client.rehydrate_game_state(baseline)
            
            # Run individual test
            run_test(client, test_case)
```

### Restore Points with Metadata

```python
with BalatroClient() as client:
    # Create labeled restore point
    restore_point = client.create_restore_point("before_shop_test")
    
    # ... run tests ...
    
    # Restore using restore point
    client.restore_from_point(restore_point)
```

## Benefits for Testing

1. **Speed**: No need to restart game or recreate complex states
2. **Reliability**: Consistent baseline states for reproducible tests
3. **Efficiency**: Smaller snapshots, faster serialization
4. **Flexibility**: Easy to create checkpoints at any game state
5. **Isolation**: Each test starts from known clean state

## Testing the System

Run the included test script:

```bash
python test_snapshot_system.py
```

This will demonstrate:

- Size comparison vs full game state
- Snapshot creation and structure
- Rehydration functionality
- Usage patterns for testing

## Technical Notes

### Filtering Strategy

The serializer excludes:

- Functions and userdata (non-serializable)
- Tables with metatables (often UI objects)
- Predefined UI field names
- Keys starting with capital letters
- Private fields (starting with underscore)

### Rehydration Approach

Rather than trying to reconstruct the entire state from JSON (nearly impossible due to Balatro's complex initialization), the system:

1. Creates a fresh baseline run with proper UI initialization
2. Patches only the mechanics data over the baseline
3. Preserves all UI scaffolding and internal caches

This approach is much more robust and handles edge cases automatically.
