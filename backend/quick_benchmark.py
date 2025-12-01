#!/usr/bin/env python
"""
Quick Performance Test: Sequential vs Reversed Digit Client Numbering
Tests insert performance with current Django/PostgreSQL setup
"""
import os
import django
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from django.db import transaction
from apps.clients.models import Client

def cleanup_test_data():
    """Remove any existing test data"""
    print("🧹 Cleaning test data...")
    deleted = Client.objects.filter(first_name__startswith='TEST_').delete()
    print(f"   Deleted {deleted[0]} test records")

def generate_sequential_number(num):
    """Traditional sequential: 1, 2, 3, 4, 5..."""
    return f"TEST-{num:06d}"

def generate_reversed_number(num):
    """Reversed digits with prefix to avoid collisions: 1→100001, 12→200021, etc."""
    # Add a prefix digit to avoid collisions and then reverse
    prefixed_num = int(f"1{num:05d}")  # 1 + 5-digit number
    reversed_digits = str(prefixed_num)[::-1]
    return f"TEST-{reversed_digits}"

def test_insert_performance(strategy, count=500):
    """Test insertion performance for a given strategy"""
    print(f"\n🚀 Testing {strategy.upper()} strategy ({count} inserts)...")
    
    start_time = time.time()
    created_count = 0
    error_count = 0
    
    for i in range(1, count + 1):
        try:
            # Generate client number based on strategy
            if strategy == 'sequential':
                client_number = generate_sequential_number(i)
            elif strategy == 'reversed':
                client_number = generate_reversed_number(i)
            
            # Create client
            with transaction.atomic():
                client = Client.objects.create(
                    client_number=client_number,
                    first_name=f'TEST_{strategy.upper()}',
                    last_name=f'User{i:04d}',
                    is_active=True
                )
                created_count += 1
                
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Show first 5 errors only
                print(f"   ❌ Error at {i}: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Calculate performance metrics
    clients_per_second = created_count / duration if duration > 0 else 0
    
    results = {
        'strategy': strategy,
        'total_attempted': count,
        'created': created_count,
        'errors': error_count,
        'duration': duration,
        'clients_per_second': clients_per_second,
        'success_rate': (created_count / count) * 100
    }
    
    print_results(results)
    return results

def print_results(results):
    """Print formatted test results"""
    print(f"   ✅ Created: {results['created']:,} clients")
    print(f"   ❌ Errors: {results['errors']:,}")
    print(f"   ⏱️  Duration: {results['duration']:.3f} seconds")
    print(f"   🚀 Speed: {results['clients_per_second']:.2f} clients/second")
    print(f"   📊 Success rate: {results['success_rate']:.1f}%")

def show_client_number_distribution():
    """Show how client numbers are distributed"""
    print("\n📊 Client Number Distribution Analysis:")
    
    # Get sample of sequential numbers
    sequential_clients = Client.objects.filter(
        first_name='TEST_SEQUENTIAL'
    ).values_list('client_number', flat=True)[:10]
    
    # Get sample of reversed numbers  
    reversed_clients = Client.objects.filter(
        first_name='TEST_REVERSED'
    ).values_list('client_number', flat=True)[:10]
    
    print(f"\n   Sequential samples: {list(sequential_clients)}")
    print(f"   Reversed samples:   {list(reversed_clients)}")
    
    # Show index distribution concept
    print(f"\n   Index Distribution Concept:")
    print(f"   Sequential: TEST-000001, TEST-000002, TEST-000003... (clustered)")
    print(f"   Reversed:   TEST-000001, TEST-000021, TEST-000031... (distributed)")

def main():
    """Run the quick benchmark"""
    print("🏁 Quick Client Numbering Performance Benchmark")
    print(f"🕐 Start time: {datetime.now()}")
    
    # Cleanup existing test data
    cleanup_test_data()
    
    # Test parameters
    test_count = 1000  # Number of clients to create per test
    
    print(f"\n⚙️  Test Parameters:")
    print(f"   Clients per test: {test_count:,}")
    print(f"   Database: PostgreSQL")
    print(f"   Framework: Django ORM")
    
    # Run tests
    results = {}
    
    # Test 1: Sequential numbering
    results['sequential'] = test_insert_performance('sequential', test_count)
    
    # Small delay between tests
    time.sleep(1)
    
    # Test 2: Reversed numbering
    results['reversed'] = test_insert_performance('reversed', test_count)
    
    # Show distribution analysis
    show_client_number_distribution()
    
    # Compare results
    print("\n" + "="*60)
    print("📈 PERFORMANCE COMPARISON")
    print("="*60)
    
    seq_result = results['sequential']
    rev_result = results['reversed']
    
    print(f"{'Metric':<25} {'Sequential':<15} {'Reversed':<15} {'Difference'}")
    print("-" * 70)
    print(f"{'Clients/second':<25} {seq_result['clients_per_second']:<15.2f} "
          f"{rev_result['clients_per_second']:<15.2f} "
          f"{((rev_result['clients_per_second'] / seq_result['clients_per_second'] - 1) * 100):+.1f}%")
    
    print(f"{'Total time (seconds)':<25} {seq_result['duration']:<15.3f} "
          f"{rev_result['duration']:<15.3f} "
          f"{((rev_result['duration'] / seq_result['duration'] - 1) * 100):+.1f}%")
    
    print(f"{'Success rate (%)':<25} {seq_result['success_rate']:<15.1f} "
          f"{rev_result['success_rate']:<15.1f} "
          f"{(rev_result['success_rate'] - seq_result['success_rate']):+.1f}")
    
    # Determine winner
    if rev_result['clients_per_second'] > seq_result['clients_per_second']:
        if seq_result['clients_per_second'] > 0:
            improvement = ((rev_result['clients_per_second'] / seq_result['clients_per_second'] - 1) * 100)
        else:
            improvement = 100
        print(f"\n🏆 WINNER: REVERSED numbering is {improvement:.1f}% faster!")
    elif seq_result['clients_per_second'] > 0 and rev_result['clients_per_second'] > 0:
        improvement = ((seq_result['clients_per_second'] / rev_result['clients_per_second'] - 1) * 100)
        print(f"\n🏆 WINNER: SEQUENTIAL numbering is {improvement:.1f}% faster!")
    else:
        print(f"\n⚠️  Cannot determine winner due to errors in one or both tests.")
    
    print(f"\n📝 Conclusion:")
    if abs(rev_result['clients_per_second'] - seq_result['clients_per_second']) < 10:
        print("   Performance difference is minimal for this test size.")
        print("   Benefits would be more apparent with higher concurrency and larger datasets.")
    else:
        print("   Significant performance difference detected!")
        print("   Consider the winning strategy for high-volume scenarios.")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test data...")
    cleanup_test_data()
    
    print(f"\n🏁 Benchmark completed!")
    print(f"🕐 End time: {datetime.now()}")

if __name__ == "__main__":
    main()