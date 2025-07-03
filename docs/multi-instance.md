# Multi-Instance Setup

Guide to running multiple Balatrobot instances simultaneously for parallel bot testing and development.

## Overview

Multi-instance setup allows you to run multiple bot instances simultaneously, enabling:

- **Parallel Testing**: Test different bot strategies simultaneously
- **Performance Comparison**: Compare bot performance under identical conditions
- **Development Efficiency**: Test multiple configurations at once
- **Data Collection**: Gather more game data faster

## Configuration

### Basic Multi-Instance Setup

Each instance requires unique ports and configuration:

**Instance 1 Configuration (`config_1.lua`):**
```lua
return {
    bot_port = 12346,
    game_port = 12345,
    bot_host = "127.0.0.1",
    game_host = "127.0.0.1",
    instance_id = "bot_1",
    log_file = "logs/bot_1.log"
}
```

**Instance 2 Configuration (`config_2.lua`):**
```lua
return {
    bot_port = 12348,
    game_port = 12347,
    bot_host = "127.0.0.1",
    game_host = "127.0.0.1",
    instance_id = "bot_2",
    log_file = "logs/bot_2.log"
}
```

### Python Bot Configuration

Configure bots with unique ports:

```python
# Bot Instance 1
bot1 = MyBot(
    deck="Red Deck",
    stake=1,
    bot_port=12346,
    seed="SEED_001"
)

# Bot Instance 2
bot2 = MyBot(
    deck="Red Deck", 
    stake=1,
    bot_port=12348,
    seed="SEED_001"  # Same seed for comparison
)
```

## Port Management

### Port Allocation Strategy

**Recommended Port Ranges:**
- Bot ports: 12346, 12348, 12350, 12352, ...
- Game ports: 12345, 12347, 12349, 12351, ...

```python
class PortManager:
    def __init__(self):
        self.base_bot_port = 12346
        self.base_game_port = 12345
        self.used_ports = set()
    
    def allocate_ports(self, instance_id):
        bot_port = self.base_bot_port + (instance_id * 2)
        game_port = self.base_game_port + (instance_id * 2)
        
        if bot_port in self.used_ports or game_port in self.used_ports:
            raise ValueError(f"Ports already in use for instance {instance_id}")
        
        self.used_ports.add(bot_port)
        self.used_ports.add(game_port)
        
        return bot_port, game_port
```

### Port Verification

Check port availability before starting:

```python
import socket

def is_port_available(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", port))
        sock.close()
        return True
    except OSError:
        return False

def verify_ports(bot_port, game_port):
    if not is_port_available(bot_port):
        raise RuntimeError(f"Bot port {bot_port} is not available")
    if not is_port_available(game_port):
        raise RuntimeError(f"Game port {game_port} is not available")
```

## Instance Coordination

### Manager Class

Create a manager to coordinate multiple instances:

```python
import threading
import time
from concurrent.futures import ThreadPoolExecutor

class MultiInstanceManager:
    def __init__(self):
        self.instances = []
        self.results = {}
        self.port_manager = PortManager()
    
    def add_instance(self, bot_class, **kwargs):
        instance_id = len(self.instances)
        bot_port, game_port = self.port_manager.allocate_ports(instance_id)
        
        instance = {
            'id': instance_id,
            'bot_class': bot_class,
            'bot_port': bot_port,
            'game_port': game_port,
            'kwargs': kwargs
        }
        
        self.instances.append(instance)
        return instance_id
    
    def run_instance(self, instance):
        try:
            bot = instance['bot_class'](
                bot_port=instance['bot_port'],
                **instance['kwargs']
            )
            
            result = bot.run()
            self.results[instance['id']] = {
                'status': 'completed',
                'result': result,
                'bot_port': instance['bot_port']
            }
            
        except Exception as e:
            self.results[instance['id']] = {
                'status': 'failed',
                'error': str(e),
                'bot_port': instance['bot_port']
            }
    
    def run_all(self, max_workers=4):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for instance in self.instances:
                future = executor.submit(self.run_instance, instance)
                futures.append(future)
            
            # Wait for all instances to complete
            for future in futures:
                future.result()
        
        return self.results
```

### Usage Example

```python
# Create manager and add instances
manager = MultiInstanceManager()

# Add different bot configurations
manager.add_instance(AggressiveBot, deck="Red Deck", stake=1)
manager.add_instance(ConservativeBot, deck="Red Deck", stake=1) 
manager.add_instance(BalancedBot, deck="Red Deck", stake=1)

# Run all instances
results = manager.run_all(max_workers=3)

# Analyze results
for instance_id, result in results.items():
    print(f"Instance {instance_id}: {result['status']}")
```

## Resource Management

### Memory Management

Monitor and limit memory usage per instance:

```python
import psutil
import os

class ResourceMonitor:
    def __init__(self, memory_limit_mb=512):
        self.memory_limit_mb = memory_limit_mb
        self.processes = {}
    
    def monitor_instance(self, instance_id, pid):
        try:
            process = psutil.Process(pid)
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.memory_limit_mb:
                print(f"Instance {instance_id} exceeds memory limit: {memory_mb:.1f}MB")
                return False
                
            return True
        except psutil.NoSuchProcess:
            return False
```

### CPU Management

Distribute CPU load across instances:

```python
def set_cpu_affinity(instance_id, total_instances):
    # Distribute instances across CPU cores
    import psutil
    cpu_count = psutil.cpu_count()
    core_id = instance_id % cpu_count
    
    try:
        process = psutil.Process()
        process.cpu_affinity([core_id])
        print(f"Instance {instance_id} assigned to CPU core {core_id}")
    except:
        print(f"Could not set CPU affinity for instance {instance_id}")
```

## Monitoring

### Real-time Status

Monitor instance status in real-time:

```python
class InstanceMonitor:
    def __init__(self, manager):
        self.manager = manager
        self.running = True
    
    def start_monitoring(self):
        while self.running:
            self.print_status()
            time.sleep(5)
    
    def print_status(self):
        print("\n" + "="*50)
        print("INSTANCE STATUS")
        print("="*50)
        
        for instance in self.manager.instances:
            instance_id = instance['id']
            port = instance['bot_port']
            
            # Check if port is still in use (instance running)
            if is_port_available(port):
                status = "STOPPED"
            else:
                status = "RUNNING"
            
            print(f"Instance {instance_id}: {status} (Port: {port})")
```

### Performance Metrics

Collect performance data across instances:

```python
class PerformanceCollector:
    def __init__(self):
        self.metrics = {}
    
    def collect_metrics(self, instance_id, bot):
        self.metrics[instance_id] = {
            'rounds_completed': bot.state.get('rounds_played', 0),
            'total_score': bot.state.get('total_score', 0),
            'average_score': self._calculate_average_score(bot),
            'runtime': bot.state.get('runtime', 0)
        }
    
    def _calculate_average_score(self, bot):
        rounds = bot.state.get('rounds_played', 0)
        total = bot.state.get('total_score', 0)
        return total / rounds if rounds > 0 else 0
    
    def generate_report(self):
        print("\nPERFORMANCE REPORT")
        print("="*50)
        
        for instance_id, metrics in self.metrics.items():
            print(f"\nInstance {instance_id}:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")
```

## Common Use Cases

### A/B Testing

Compare two bot strategies:

```python
def ab_test_bots():
    manager = MultiInstanceManager()
    
    # Test A: Aggressive strategy
    for i in range(5):
        manager.add_instance(
            AggressiveBot, 
            deck="Red Deck", 
            stake=1,
            seed=f"TEST_A_{i}"
        )
    
    # Test B: Conservative strategy
    for i in range(5):
        manager.add_instance(
            ConservativeBot,
            deck="Red Deck",
            stake=1, 
            seed=f"TEST_B_{i}"
        )
    
    results = manager.run_all()
    
    # Analyze A vs B performance
    a_results = [r for i, r in results.items() if i < 5]
    b_results = [r for i, r in results.items() if i >= 5]
    
    print(f"Strategy A average: {calculate_average(a_results)}")
    print(f"Strategy B average: {calculate_average(b_results)}")
```

### Parameter Sweeping

Test different parameter values:

```python
def parameter_sweep():
    manager = MultiInstanceManager()
    
    # Test different aggression levels
    for aggression in [0.1, 0.3, 0.5, 0.7, 0.9]:
        manager.add_instance(
            ParameterizedBot,
            deck="Red Deck",
            stake=1,
            aggression_level=aggression
        )
    
    results = manager.run_all()
    return results
```

### Stress Testing

Test bot stability under load:

```python
def stress_test():
    manager = MultiInstanceManager()
    
    # Create many concurrent instances
    for i in range(20):
        manager.add_instance(
            StressTestBot,
            deck="Red Deck",
            stake=1,
            rounds_limit=100
        )
    
    start_time = time.time()
    results = manager.run_all(max_workers=10)
    end_time = time.time()
    
    print(f"Stress test completed in {end_time - start_time:.1f} seconds")
    successful = sum(1 for r in results.values() if r['status'] == 'completed')
    print(f"Success rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
```

## Troubleshooting

### Common Issues

**1. Port Conflicts**
```python
# Check for port conflicts
def diagnose_port_conflicts():
    for port in range(12345, 12365):
        if not is_port_available(port):
            print(f"Port {port} is in use")
```

**2. Memory Leaks**
```python
# Monitor memory usage across instances
def check_memory_usage():
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        if 'python' in proc.info['name'].lower():
            memory_mb = proc.info['memory_info'].rss / 1024 / 1024
            if memory_mb > 500:
                print(f"High memory usage: PID {proc.info['pid']} - {memory_mb:.1f}MB")
```

**3. Instance Synchronization**
```python
# Ensure instances start in sequence
def staggered_start(manager, delay=2):
    for i, instance in enumerate(manager.instances):
        if i > 0:
            time.sleep(delay)
        
        thread = threading.Thread(target=manager.run_instance, args=(instance,))
        thread.start()
```

### Debugging Multiple Instances

```python
def debug_instances():
    # Enable debug logging for all instances
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - Instance %(name)s - %(message)s'
    )
    
    # Add instance ID to all log messages
    class InstanceLogger:
        def __init__(self, instance_id):
            self.instance_id = instance_id
            self.logger = logging.getLogger(f"Instance_{instance_id}")
        
        def debug(self, message):
            self.logger.debug(f"[{self.instance_id}] {message}")
```

---

*For performance optimization across instances, see [Performance](performance.md) and [Configuration](configuration.md).* 