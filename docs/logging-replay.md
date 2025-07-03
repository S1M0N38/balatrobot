# Logging & Replay

Complete guide to logging bot actions and replaying games for analysis and debugging.

## 📋 Table of Contents

- [Overview](#overview)
- [Action Logging](#action-logging)
- [Game State Logging](#game-state-logging)
- [Log Formats](#log-formats)
- [Replay System](#replay-system)
- [Analysis Tools](#analysis-tools)
- [Performance Monitoring](#performance-monitoring)
- [Debugging with Logs](#debugging-with-logs)
- [Best Practices](#best-practices)

## Overview

The logging and replay system in Balatrobot provides comprehensive tracking of:

- **Action Logs**: Every bot decision and game action
- **Game State**: Complete game state at each decision point
- **Performance Metrics**: Timing and resource usage data
- **Error Tracking**: Exceptions and failure conditions
- **Replay Capability**: Reconstruct and replay entire games

## Action Logging

### Basic Action Logging

Enable action logging in your bot configuration:

```lua
-- config.lua
return {
    log_actions = true,
    log_file = "logs/bot_actions.log",
    log_level = "INFO",
    -- Other settings...
}
```

### Python Bot Logging

Add logging to your bot methods:

```python
import logging
from datetime import datetime

class LoggingBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_logging()
    
    def setup_logging(self):
        log_filename = f"logs/bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def select_cards_from_hand(self, G):
        # Log the decision context
        hand_size = len(G["hand"])
        money = G["player"]["money"]
        
        self.logger.info(f"Hand Decision - Cards: {hand_size}, Money: {money}")
        
        # Make decision
        action = [Actions.PLAY_HAND, [1, 2]]
        
        # Log the action taken
        self.logger.info(f"Action: {action}")
        
        return action
```

### Structured Action Logging

Use structured logging for easier analysis:

```python
import json

class StructuredLoggingBot(Bot):
    def log_action(self, method_name, game_state_summary, action, context=None):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method_name,
            'game_state': game_state_summary,
            'action': action,
            'context': context or {}
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def select_cards_from_hand(self, G):
        # Summarize relevant game state
        state_summary = {
            'hand_size': len(G["hand"]),
            'money': G["player"]["money"],
            'round': G.get("round", {}).get("number", 0),
            'ante': G.get("ante", {}).get("number", 0)
        }
        
        # Make decision
        action = [Actions.PLAY_HAND, [1, 2]]
        
        # Add context
        context = {
            'decision_time_ms': 15.5,
            'confidence': 0.85
        }
        
        self.log_action('select_cards_from_hand', state_summary, action, context)
        return action
```

## Game State Logging

### Complete State Snapshots

Log full game state at key decision points:

```python
class StateLoggingBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_log_dir = "logs/game_states"
        os.makedirs(self.state_log_dir, exist_ok=True)
    
    def log_game_state(self, G, event_name):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{self.state_log_dir}/state_{event_name}_{timestamp}.json"
        
        # Clean and serialize game state
        clean_state = self.clean_game_state(G)
        
        with open(filename, 'w') as f:
            json.dump(clean_state, f, indent=2)
    
    def clean_game_state(self, G):
        # Remove non-serializable objects and clean data
        cleaned = {}
        for key, value in G.items():
            if self.is_serializable(value):
                cleaned[key] = value
        return cleaned
    
    def is_serializable(self, obj):
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False
```

### Selective State Logging

Log only relevant state information:

```python
def log_relevant_state(self, G, method_name):
    relevant_state = {}
    
    if method_name == 'select_cards_from_hand':
        relevant_state = {
            'hand': G.get("hand", []),
            'round_info': G.get("round", {}),
            'blind_info': G.get("ante", {}).get("blinds", {})
        }
    elif method_name == 'select_shop_action':
        relevant_state = {
            'shop': G.get("shop", {}),
            'money': G.get("player", {}).get("money", 0),
            'jokers': G.get("jokers", [])
        }
    
    self.logger.info(f"State for {method_name}: {json.dumps(relevant_state)}")
```

## Log Formats

### Standard Log Format

```
2024-01-15 14:30:25,123 - INFO - Hand Decision - Cards: 5, Money: 25
2024-01-15 14:30:25,124 - INFO - Action: ['PLAY_HAND', [1, 2]]
2024-01-15 14:30:25,125 - INFO - Shop Decision - Money: 30, Available: 3
2024-01-15 14:30:25,126 - INFO - Action: ['BUY_CARD', [1]]
```

### JSON Log Format

```json
{
  "timestamp": "2024-01-15T14:30:25.123456",
  "method": "select_cards_from_hand",
  "game_state": {
    "hand_size": 5,
    "money": 25,
    "round": 3,
    "ante": 1
  },
  "action": ["PLAY_HAND", [1, 2]],
  "context": {
    "decision_time_ms": 15.5,
    "confidence": 0.85
  }
}
```

### CSV Log Format

For statistical analysis:

```python
import csv

class CSVLoggingBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file = open('logs/bot_actions.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write header
        self.csv_writer.writerow([
            'timestamp', 'method', 'hand_size', 'money', 
            'round', 'ante', 'action_type', 'action_params'
        ])
    
    def log_to_csv(self, method, G, action):
        self.csv_writer.writerow([
            datetime.now().isoformat(),
            method,
            len(G.get("hand", [])),
            G.get("player", {}).get("money", 0),
            G.get("round", {}).get("number", 0),
            G.get("ante", {}).get("number", 0),
            action[0] if action else None,
            str(action[1:]) if len(action) > 1 else ""
        ])
        self.csv_file.flush()
```

## Replay System

### Game Replay Framework

Create a system to replay logged games:

```python
class GameReplayer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.actions = []
        self.game_states = []
        self.load_logs()
    
    def load_logs(self):
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        log_entry = json.loads(line)
                        self.actions.append(log_entry)
                    except json.JSONDecodeError:
                        # Handle non-JSON log lines
                        pass
    
    def replay_game(self, step_by_step=False):
        print("Starting game replay...")
        
        for i, action_log in enumerate(self.actions):
            print(f"\nStep {i+1}: {action_log['method']}")
            print(f"Game State: {action_log['game_state']}")
            print(f"Action: {action_log['action']}")
            
            if step_by_step:
                input("Press Enter to continue...")
    
    def analyze_decisions(self):
        decision_analysis = {}
        
        for action_log in self.actions:
            method = action_log['method']
            if method not in decision_analysis:
                decision_analysis[method] = []
            
            decision_analysis[method].append({
                'state': action_log['game_state'],
                'action': action_log['action'],
                'context': action_log.get('context', {})
            })
        
        return decision_analysis
```

### Interactive Replay

Create an interactive replay system:

```python
class InteractiveReplayer:
    def __init__(self, log_file):
        self.replayer = GameReplayer(log_file)
        self.current_step = 0
    
    def start_interactive_session(self):
        while True:
            self.show_current_step()
            command = input("\nCommands: (n)ext, (p)revious, (j)ump, (a)nalyze, (q)uit: ").lower()
            
            if command == 'n':
                self.next_step()
            elif command == 'p':
                self.previous_step()
            elif command == 'j':
                step = int(input("Jump to step: "))
                self.jump_to_step(step)
            elif command == 'a':
                self.analyze_current_decision()
            elif command == 'q':
                break
    
    def show_current_step(self):
        if 0 <= self.current_step < len(self.replayer.actions):
            action_log = self.replayer.actions[self.current_step]
            print(f"\n--- Step {self.current_step + 1} ---")
            print(f"Method: {action_log['method']}")
            print(f"Game State: {action_log['game_state']}")
            print(f"Action: {action_log['action']}")
```

## Analysis Tools

### Performance Analysis

Analyze bot performance from logs:

```python
class PerformanceAnalyzer:
    def __init__(self, log_files):
        self.log_files = log_files if isinstance(log_files, list) else [log_files]
        self.data = []
        self.load_all_logs()
    
    def load_all_logs(self):
        for log_file in self.log_files:
            replayer = GameReplayer(log_file)
            self.data.extend(replayer.actions)
    
    def analyze_decision_times(self):
        decision_times = {}
        
        for action_log in self.data:
            method = action_log['method']
            decision_time = action_log.get('context', {}).get('decision_time_ms', 0)
            
            if method not in decision_times:
                decision_times[method] = []
            
            decision_times[method].append(decision_time)
        
        # Calculate statistics
        stats = {}
        for method, times in decision_times.items():
            if times:
                stats[method] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        return stats
    
    def analyze_action_patterns(self):
        action_counts = {}
        
        for action_log in self.data:
            action_type = action_log['action'][0] if action_log['action'] else 'UNKNOWN'
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        return action_counts
```

### Decision Quality Analysis

Analyze the quality of bot decisions:

```python
class DecisionAnalyzer:
    def analyze_hand_decisions(self, logs):
        good_decisions = 0
        total_decisions = 0
        
        for action_log in logs:
            if action_log['method'] == 'select_cards_from_hand':
                total_decisions += 1
                
                # Define criteria for good decisions
                if self.is_good_hand_decision(action_log):
                    good_decisions += 1
        
        return good_decisions / total_decisions if total_decisions > 0 else 0
    
    def is_good_hand_decision(self, action_log):
        state = action_log['game_state']
        action = action_log['action']
        
        # Example criteria
        if state.get('money', 0) < 10 and action[0] == 'DISCARD_HAND':
            return False  # Should try to play when low on money
        
        if state.get('hand_size', 0) <= 2 and action[0] == 'DISCARD_HAND':
            return False  # Don't discard when hand is small
        
        return True
```

## Performance Monitoring

### Real-time Performance Monitoring

Monitor bot performance during execution:

```python
import time
import threading

class PerformanceMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.metrics = {
            'decisions_per_second': 0,
            'average_decision_time': 0,
            'total_decisions': 0,
            'errors': 0
        }
        self.monitoring = True
        self.start_monitoring()
    
    def start_monitoring(self):
        def monitor():
            while self.monitoring:
                self.update_metrics()
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def update_metrics(self):
        # Update metrics based on bot state
        total_time = time.time() - self.bot.start_time
        self.metrics['decisions_per_second'] = self.metrics['total_decisions'] / total_time
        
        print(f"DPS: {self.metrics['decisions_per_second']:.2f}, "
              f"Avg Time: {self.metrics['average_decision_time']:.2f}ms, "
              f"Errors: {self.metrics['errors']}")
```

## Debugging with Logs

### Error Tracking

Track and analyze errors:

```python
class ErrorTracker:
    def __init__(self):
        self.errors = []
    
    def log_error(self, method, error, game_state=None):
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'error': str(error),
            'error_type': type(error).__name__,
            'game_state': game_state
        }
        
        self.errors.append(error_entry)
        
        # Log to file
        with open('logs/errors.log', 'a') as f:
            f.write(json.dumps(error_entry) + '\n')
    
    def analyze_errors(self):
        error_counts = {}
        for error in self.errors:
            error_type = error['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return error_counts
```

### Debug Mode Logging

Enhanced logging for debugging:

```python
class DebugBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_mode = True
        self.decision_history = []
    
    def debug_log(self, message, data=None):
        if self.debug_mode:
            debug_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'data': data
            }
            
            print(f"DEBUG: {message}")
            if data:
                print(f"  Data: {data}")
            
            with open('logs/debug.log', 'a') as f:
                f.write(json.dumps(debug_entry) + '\n')
    
    def select_cards_from_hand(self, G):
        self.debug_log("Starting hand selection", {
            'hand_size': len(G["hand"]),
            'money': G["player"]["money"]
        })
        
        # Decision logic with debug info
        action = [Actions.PLAY_HAND, [1, 2]]
        
        self.debug_log("Hand selection complete", {
            'action': action,
            'reasoning': "Playing first two cards for safety"
        })
        
        return action
```

## Best Practices

### 1. Log Rotation

Implement log rotation to manage file sizes:

```python
import logging.handlers

def setup_rotating_logs():
    handler = logging.handlers.RotatingFileHandler(
        'logs/bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
```

### 2. Structured Logging

Use consistent log structure:

```python
def log_decision(method, state_summary, action, metadata=None):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': 'decision',
        'method': method,
        'state': state_summary,
        'action': action,
        'metadata': metadata or {}
    }
    
    logging.info(json.dumps(log_entry))
```

### 3. Selective Logging

Log based on importance levels:

```python
def should_log(event_type, importance):
    log_levels = {
        'critical': 1,
        'important': 2,
        'normal': 3,
        'debug': 4
    }
    
    current_level = log_levels.get(os.environ.get('LOG_LEVEL', 'normal'), 3)
    event_level = log_levels.get(importance, 3)
    
    return event_level <= current_level
```

### 4. Performance Considerations

Optimize logging for performance:

```python
class AsyncLogger:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.start_worker()
    
    def start_worker(self):
        def worker():
            while True:
                log_entry = self.log_queue.get()
                if log_entry is None:
                    break
                
                # Write log entry to file
                with open('logs/async.log', 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
        
        threading.Thread(target=worker, daemon=True).start()
    
    def log(self, entry):
        self.log_queue.put(entry)
```

---

*For more advanced debugging techniques, see [Troubleshooting](troubleshooting.md) and [Performance](performance.md).* 