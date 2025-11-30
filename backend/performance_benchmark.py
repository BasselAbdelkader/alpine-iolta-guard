#!/usr/bin/env python
"""
Performance Benchmark: Sequential vs Reversed Digit Client Numbering
Tests PostgreSQL index performance with different numbering strategies
"""
import os
import django
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import random
import uuid
import hashlib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from django.db import transaction, connection
from apps.clients.models import Client
from django.db.models import Max

class ClientNumberingBenchmark:
    def __init__(self):
        self.results = {}
        self.lock = threading.Lock()
        
    def cleanup_test_data(self):
        """Clean up any test data before starting"""
        print("🧹 Cleaning up existing test data...")
        Client.objects.filter(first_name__startswith='BENCH_').delete()
        
    def generate_sequential_number(self, sequence_num):
        """Traditional sequential numbering"""
        return f"BENCH-{sequence_num:06d}"
    
    def generate_reversed_number(self, sequence_num):
        """Reversed digit numbering for better index distribution"""
        reversed_digits = str(sequence_num)[::-1]
        return f"BENCH-{reversed_digits.zfill(6)}"
    
    def generate_uuid_number(self, sequence_num):
        """UUID-based numbering for maximum distribution"""
        hash_input = f"{sequence_num}-{time.time()}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        return f"BENCH-{hash_hex.upper()}"
    
    def generate_random_number(self, sequence_num):
        """Random but predictable numbering"""
        random.seed(sequence_num)  # Predictable randomness
        random_num = random.randint(100000, 999999)
        return f"BENCH-{random_num:06d}"
    
    def create_client_batch(self, strategy, start_num, batch_size, thread_id):
        """Create a batch of clients with specified numbering strategy"""
        clients_created = []
        errors = 0
        
        for i in range(batch_size):
            sequence_num = start_num + i
            
            try:
                # Generate client number based on strategy
                if strategy == 'sequential':
                    client_number = self.generate_sequential_number(sequence_num)
                elif strategy == 'reversed':
                    client_number = self.generate_reversed_number(sequence_num)
                elif strategy == 'uuid':
                    client_number = self.generate_uuid_number(sequence_num)
                elif strategy == 'random':
                    client_number = self.generate_random_number(sequence_num)
                
                # Create client
                with transaction.atomic():
                    client = Client.objects.create(
                        client_number=client_number,
                        first_name=f'BENCH_{strategy.upper()}',
                        last_name=f'Thread{thread_id}_Seq{sequence_num}',
                        is_active=True
                    )
                    clients_created.append(client.id)
                    
            except Exception as e:
                errors += 1
                print(f"❌ Error in thread {thread_id}, sequence {sequence_num}: {e}")
                
        return len(clients_created), errors
    
    def benchmark_strategy(self, strategy, total_clients=1000, concurrent_threads=5, batch_size=50):
        """Benchmark a specific numbering strategy"""
        print(f"\n🚀 Benchmarking {strategy.upper()} strategy...")
        print(f"   📊 Total clients: {total_clients}")
        print(f"   🧵 Concurrent threads: {concurrent_threads}")
        print(f"   📦 Batch size: {batch_size}")
        
        # Calculate batches per thread
        batches_per_thread = total_clients // (concurrent_threads * batch_size)
        
        start_time = time.time()
        total_created = 0
        total_errors = 0
        thread_times = []
        
        # Monitor database connections
        initial_connections = self.get_db_connections()
        
        with ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
            futures = []
            
            for thread_id in range(concurrent_threads):
                for batch_num in range(batches_per_thread):
                    start_num = (thread_id * batches_per_thread + batch_num) * batch_size + 1
                    
                    future = executor.submit(
                        self.create_client_batch, 
                        strategy, 
                        start_num, 
                        batch_size, 
                        thread_id
                    )
                    futures.append((future, thread_id, time.time()))
            
            # Collect results
            for future, thread_id, submit_time in futures:
                try:
                    created, errors = future.result(timeout=60)  # 60 second timeout
                    execution_time = time.time() - submit_time
                    thread_times.append(execution_time)
                    total_created += created
                    total_errors += errors
                    
                except Exception as e:
                    print(f"❌ Thread {thread_id} failed: {e}")
                    total_errors += batch_size
        
        end_time = time.time()
        total_duration = end_time - start_time
        final_connections = self.get_db_connections()
        
        # Calculate statistics
        avg_thread_time = statistics.mean(thread_times) if thread_times else 0
        max_thread_time = max(thread_times) if thread_times else 0
        min_thread_time = min(thread_times) if thread_times else 0
        
        # Get index statistics
        index_stats = self.get_index_statistics()
        
        results = {
            'strategy': strategy,
            'total_clients_attempted': total_clients,
            'total_clients_created': total_created,
            'total_errors': total_errors,
            'total_duration_seconds': total_duration,
            'clients_per_second': total_created / total_duration if total_duration > 0 else 0,
            'average_thread_time': avg_thread_time,
            'max_thread_time': max_thread_time,
            'min_thread_time': min_thread_time,
            'initial_db_connections': initial_connections,
            'final_db_connections': final_connections,
            'index_statistics': index_stats,
            'concurrent_threads': concurrent_threads
        }
        
        self.results[strategy] = results
        self.print_strategy_results(results)
        
        return results
    
    def get_db_connections(self):
        """Get current number of database connections"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = current_database() AND state = 'active'
                """)
                return cursor.fetchone()[0]
        except:
            return 0
    
    def get_index_statistics(self):
        """Get index usage statistics"""
        try:
            with connection.cursor() as cursor:
                # Get index statistics for clients table
                cursor.execute("""
                    SELECT 
                        indexrelname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE relname = 'clients'
                    ORDER BY idx_scan DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            return [f"Error getting index stats: {e}"]
    
    def print_strategy_results(self, results):
        """Print detailed results for a strategy"""
        print(f"\n📈 {results['strategy'].upper()} RESULTS:")
        print(f"   ✅ Clients created: {results['total_clients_created']:,}")
        print(f"   ❌ Errors: {results['total_errors']:,}")
        print(f"   ⏱️  Total time: {results['total_duration_seconds']:.2f} seconds")
        print(f"   🚀 Clients/second: {results['clients_per_second']:.2f}")
        print(f"   📊 Avg thread time: {results['average_thread_time']:.3f}s")
        print(f"   📊 Max thread time: {results['max_thread_time']:.3f}s")
        print(f"   📊 Min thread time: {results['min_thread_time']:.3f}s")
        print(f"   🔗 DB connections: {results['initial_db_connections']} → {results['final_db_connections']}")
        
        if results['index_statistics']:
            print(f"   📑 Index usage:")
            for stat in results['index_statistics'][:3]:  # Show top 3
                if isinstance(stat, tuple):
                    print(f"      {stat[0]}: {stat[1]} scans, {stat[2]} reads")
    
    def run_comprehensive_benchmark(self):
        """Run benchmark for all strategies"""
        print("🏁 Starting Comprehensive Client Numbering Benchmark")
        print(f"🕐 Start time: {datetime.now()}")
        
        # Cleanup before starting
        self.cleanup_test_data()
        
        # Test parameters
        test_params = {
            'total_clients': 2000,      # Total clients per strategy
            'concurrent_threads': 8,    # Concurrent insertion threads
            'batch_size': 25           # Clients per batch
        }
        
        print(f"\n⚙️  Test Parameters:")
        for key, value in test_params.items():
            print(f"   {key}: {value}")
        
        # Test each strategy
        strategies = ['sequential', 'reversed', 'uuid', 'random']
        
        overall_start = time.time()
        
        for strategy in strategies:
            try:
                self.benchmark_strategy(strategy, **test_params)
                # Small delay between strategies
                time.sleep(2)
            except Exception as e:
                print(f"❌ Failed to benchmark {strategy}: {e}")
        
        overall_duration = time.time() - overall_start
        
        # Print comparison results
        self.print_comparison_results()
        
        print(f"\n🏁 Benchmark completed in {overall_duration:.2f} seconds")
        print(f"🕐 End time: {datetime.now()}")
        
        # Cleanup after benchmark
        self.cleanup_test_data()
    
    def print_comparison_results(self):
        """Print comparison of all strategies"""
        if not self.results:
            return
            
        print("\n" + "="*80)
        print("📊 PERFORMANCE COMPARISON SUMMARY")
        print("="*80)
        
        # Sort by clients per second (descending)
        sorted_results = sorted(
            self.results.values(), 
            key=lambda x: x['clients_per_second'], 
            reverse=True
        )
        
        print(f"{'Strategy':<12} {'Clients/sec':<12} {'Total Time':<12} {'Success Rate':<12} {'Avg Thread':<12}")
        print("-" * 70)
        
        for result in sorted_results:
            success_rate = (result['total_clients_created'] / result['total_clients_attempted']) * 100
            
            print(f"{result['strategy']:<12} "
                  f"{result['clients_per_second']:<12.2f} "
                  f"{result['total_duration_seconds']:<12.2f} "
                  f"{success_rate:<12.1f}% "
                  f"{result['average_thread_time']:<12.3f}")
        
        # Performance insights
        print("\n🎯 PERFORMANCE INSIGHTS:")
        
        best_performer = sorted_results[0]
        worst_performer = sorted_results[-1]
        
        improvement = (best_performer['clients_per_second'] / worst_performer['clients_per_second'] - 1) * 100
        
        print(f"   🏆 Best: {best_performer['strategy'].upper()} "
              f"({best_performer['clients_per_second']:.2f} clients/sec)")
        print(f"   🐌 Worst: {worst_performer['strategy'].upper()} "
              f"({worst_performer['clients_per_second']:.2f} clients/sec)")
        print(f"   📈 Performance improvement: {improvement:.1f}%")
        
        # Threading efficiency analysis
        print(f"\n🧵 THREADING EFFICIENCY:")
        for result in sorted_results:
            thread_efficiency = (result['min_thread_time'] / result['max_thread_time']) * 100
            print(f"   {result['strategy']:<12}: {thread_efficiency:.1f}% "
                  f"(variance: {result['max_thread_time'] - result['min_thread_time']:.3f}s)")

def main():
    """Run the benchmark"""
    benchmark = ClientNumberingBenchmark()
    benchmark.run_comprehensive_benchmark()

if __name__ == "__main__":
    main()