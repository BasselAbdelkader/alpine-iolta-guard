#!/usr/bin/env python
"""
Concurrent Performance Test: Sequential vs Reversed Digit Client Numbering
Tests with multiple concurrent threads to simulate real-world load
"""
import os
import django
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from django.db import transaction, connection
from apps.clients.models import Client

# Thread-safe counter for unique client numbers
class ThreadSafeCounter:
    def __init__(self, start=1):
        self.value = start
        self.lock = threading.Lock()
    
    def get_next(self):
        with self.lock:
            current = self.value
            self.value += 1
            return current

# Global counters for each strategy
sequential_counter = ThreadSafeCounter(1)
reversed_counter = ThreadSafeCounter(1)

def cleanup_test_data():
    """Remove any existing test data"""
    print("🧹 Cleaning test data...")
    deleted = Client.objects.filter(first_name__startswith='CONC_').delete()
    print(f"   Deleted {deleted[0]} test records")

def generate_sequential_number(counter):
    """Traditional sequential numbering"""
    num = counter.get_next()
    return f"CONC-SEQ-{num:06d}"

def generate_reversed_number(counter):
    """Reversed digit numbering for better distribution"""
    num = counter.get_next()
    # Use a larger number space to avoid collisions
    prefixed_num = int(f"2{num:06d}")  # 2 + 6-digit number
    reversed_digits = str(prefixed_num)[::-1]
    return f"CONC-REV-{reversed_digits}"

def create_clients_batch(strategy, batch_size, thread_id):
    """Create a batch of clients with specified strategy"""
    results = {
        'thread_id': thread_id,
        'created': 0,
        'errors': 0,
        'start_time': time.time(),
        'error_messages': []
    }
    
    # Select counter based on strategy
    if strategy == 'sequential':
        counter = sequential_counter
    else:
        counter = reversed_counter
    
    for i in range(batch_size):
        try:
            # Generate client number
            if strategy == 'sequential':
                client_number = generate_sequential_number(counter)
            else:
                client_number = generate_reversed_number(counter)
            
            # Create client with transaction
            with transaction.atomic():
                client = Client.objects.create(
                    client_number=client_number,
                    first_name=f'CONC_{strategy.upper()}',
                    last_name=f'T{thread_id}_B{i}',
                    is_active=True
                )
                results['created'] += 1
                
        except Exception as e:
            results['errors'] += 1
            if len(results['error_messages']) < 3:  # Keep first 3 error messages
                results['error_messages'].append(str(e))
    
    results['end_time'] = time.time()
    results['duration'] = results['end_time'] - results['start_time']
    
    return results

def test_concurrent_performance(strategy, total_clients=2000, num_threads=10):
    """Test concurrent insertion performance"""
    print(f"\n🚀 Testing {strategy.upper()} strategy (concurrent)")
    print(f"   📊 Total clients: {total_clients:,}")
    print(f"   🧵 Threads: {num_threads}")
    
    batch_size = total_clients // num_threads
    print(f"   📦 Batch size: {batch_size} clients per thread")
    
    start_time = time.time()
    results = []
    
    # Reset counters
    if strategy == 'sequential':
        global sequential_counter
        sequential_counter = ThreadSafeCounter(1)
    else:
        global reversed_counter
        reversed_counter = ThreadSafeCounter(1)
    
    # Monitor database connections before
    initial_connections = get_db_connections()
    
    # Run concurrent batches
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        
        for thread_id in range(num_threads):
            future = executor.submit(create_clients_batch, strategy, batch_size, thread_id)
            futures.append(future)
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)
                results.append(result)
                print(f"   Thread {result['thread_id']}: {result['created']} created, "
                      f"{result['errors']} errors, {result['duration']:.2f}s")
            except Exception as e:
                print(f"   ❌ Thread failed: {e}")
                results.append({
                    'created': 0, 'errors': batch_size, 'duration': 0,
                    'error_messages': [str(e)]
                })
    
    end_time = time.time()
    total_duration = end_time - start_time
    final_connections = get_db_connections()
    
    # Calculate aggregate results
    total_created = sum(r['created'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    avg_thread_time = sum(r['duration'] for r in results) / len(results) if results else 0
    max_thread_time = max(r['duration'] for r in results) if results else 0
    min_thread_time = min(r['duration'] for r in results) if results else 0
    
    # Calculate performance metrics
    clients_per_second = total_created / total_duration if total_duration > 0 else 0
    threading_efficiency = (min_thread_time / max_thread_time * 100) if max_thread_time > 0 else 0
    
    summary = {
        'strategy': strategy,
        'total_created': total_created,
        'total_errors': total_errors,
        'total_duration': total_duration,
        'clients_per_second': clients_per_second,
        'avg_thread_time': avg_thread_time,
        'max_thread_time': max_thread_time,
        'min_thread_time': min_thread_time,
        'threading_efficiency': threading_efficiency,
        'initial_connections': initial_connections,
        'final_connections': final_connections,
        'threads_used': num_threads
    }
    
    print_concurrent_results(summary)
    
    # Show sample client numbers
    show_sample_numbers(strategy, 5)
    
    return summary

def get_db_connections():
    """Get current database connections"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database() AND state = 'active'
            """)
            return cursor.fetchone()[0]
    except:
        return 0

def print_concurrent_results(results):
    """Print detailed concurrent test results"""
    print(f"\n   📈 {results['strategy'].upper()} CONCURRENT RESULTS:")
    print(f"   ✅ Created: {results['total_created']:,} clients")
    print(f"   ❌ Errors: {results['total_errors']:,}")
    print(f"   ⏱️  Total time: {results['total_duration']:.3f} seconds")
    print(f"   🚀 Throughput: {results['clients_per_second']:.2f} clients/second")
    print(f"   🧵 Thread efficiency: {results['threading_efficiency']:.1f}%")
    print(f"   📊 Thread times: avg={results['avg_thread_time']:.3f}s, "
          f"max={results['max_thread_time']:.3f}s, min={results['min_thread_time']:.3f}s")
    print(f"   🔗 DB connections: {results['initial_connections']} → {results['final_connections']}")

def show_sample_numbers(strategy, count=5):
    """Show sample client numbers for analysis"""
    prefix = f'CONC_{strategy.upper()}'
    samples = Client.objects.filter(
        first_name=prefix
    ).values_list('client_number', flat=True)[:count]
    
    print(f"   📋 Sample numbers: {list(samples)}")

def main():
    """Run the concurrent benchmark"""
    print("🏁 Concurrent Client Numbering Performance Benchmark")
    print(f"🕐 Start time: {datetime.now()}")
    
    # Cleanup existing test data
    cleanup_test_data()
    
    # Test parameters - scaled for meaningful concurrent testing
    test_params = {
        'total_clients': 3000,  # Total clients to create
        'num_threads': 15       # Concurrent threads
    }
    
    print(f"\n⚙️  Concurrent Test Parameters:")
    for key, value in test_params.items():
        print(f"   {key}: {value:,}")
    
    # Run concurrent tests
    results = {}
    
    # Test 1: Sequential numbering under concurrent load
    results['sequential'] = test_concurrent_performance('sequential', **test_params)
    
    # Brief pause between tests
    time.sleep(2)
    
    # Test 2: Reversed numbering under concurrent load  
    results['reversed'] = test_concurrent_performance('reversed', **test_params)
    
    # Compare concurrent results
    print("\n" + "="*80)
    print("📈 CONCURRENT PERFORMANCE COMPARISON")
    print("="*80)
    
    seq = results['sequential']
    rev = results['reversed']
    
    print(f"{'Metric':<30} {'Sequential':<15} {'Reversed':<15} {'Difference'}")
    print("-" * 75)
    
    # Throughput comparison
    throughput_diff = ((rev['clients_per_second'] / seq['clients_per_second'] - 1) * 100) if seq['clients_per_second'] > 0 else 0
    print(f"{'Clients/second (throughput)':<30} {seq['clients_per_second']:<15.1f} "
          f"{rev['clients_per_second']:<15.1f} {throughput_diff:+.1f}%")
    
    # Thread efficiency comparison
    efficiency_diff = rev['threading_efficiency'] - seq['threading_efficiency']
    print(f"{'Threading efficiency':<30} {seq['threading_efficiency']:<15.1f}% "
          f"{rev['threading_efficiency']:<15.1f}% {efficiency_diff:+.1f}%")
    
    # Error rate comparison
    seq_error_rate = (seq['total_errors'] / (seq['total_created'] + seq['total_errors']) * 100) if (seq['total_created'] + seq['total_errors']) > 0 else 0
    rev_error_rate = (rev['total_errors'] / (rev['total_created'] + rev['total_errors']) * 100) if (rev['total_created'] + rev['total_errors']) > 0 else 0
    error_diff = rev_error_rate - seq_error_rate
    print(f"{'Error rate':<30} {seq_error_rate:<15.1f}% "
          f"{rev_error_rate:<15.1f}% {error_diff:+.1f}%")
    
    # Determine concurrent winner
    print(f"\n🏆 CONCURRENT PERFORMANCE WINNER:")
    if rev['clients_per_second'] > seq['clients_per_second']:
        improvement = throughput_diff
        print(f"   REVERSED numbering wins by {improvement:.1f}% throughput improvement")
        if rev['threading_efficiency'] > seq['threading_efficiency']:
            print(f"   + Better threading efficiency (+{efficiency_diff:.1f}%)")
    else:
        improvement = -throughput_diff
        print(f"   SEQUENTIAL numbering wins by {improvement:.1f}% throughput advantage")
        if seq['threading_efficiency'] > rev['threading_efficiency']:
            print(f"   + Better threading efficiency (+{-efficiency_diff:.1f}%)")
    
    print(f"\n📊 ANALYSIS:")
    if abs(throughput_diff) < 5:
        print("   • Throughput difference is minimal (<5%)")
    elif abs(throughput_diff) < 15:
        print("   • Moderate performance difference (5-15%)")
    else:
        print("   • Significant performance difference (>15%)")
        
    if abs(efficiency_diff) > 10:
        print("   • Threading efficiency varies significantly")
        print("   • This suggests different levels of concurrency contention")
    
    if max(seq_error_rate, rev_error_rate) > 1:
        print("   • High error rate detected - possible index contention")
    
    print(f"\n💡 RECOMMENDATIONS:")
    winner = 'REVERSED' if rev['clients_per_second'] > seq['clients_per_second'] else 'SEQUENTIAL'
    print(f"   • For high-concurrency scenarios: Use {winner} numbering")
    print(f"   • Monitor database connections and index performance")
    print(f"   • Consider connection pooling for >10 concurrent operations")
    
    # Final cleanup
    cleanup_test_data()
    
    print(f"\n🏁 Concurrent benchmark completed!")
    print(f"🕐 End time: {datetime.now()}")

if __name__ == "__main__":
    main()