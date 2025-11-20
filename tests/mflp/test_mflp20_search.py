import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client
from apps.clients.api.views import ClientViewSet
from apps.clients.api.serializers import ClientListSerializer
from django.db.models import Q, Value
from django.db.models.functions import Concat
from rest_framework.test import APIRequestFactory

print("="*80)
print("MFLP-20 VERIFICATION: Client Search by Full Name")
print("="*80)
print()

# Get sample clients to test with
clients = Client.objects.all()[:5]
print(f"Total clients in database: {Client.objects.count()}")
print()

print("Sample clients:")
for c in clients:
    print(f"  {c.id}: {c.first_name} {c.last_name}")
print()

if clients.exists():
    test_client = clients[0]
    full_name = f"{test_client.first_name} {test_client.last_name}"

    print("="*80)
    print(f"TEST 1: ORM Query - Search by Full Name '{full_name}'")
    print("="*80)

    # Test the ORM query (same as in search method)
    results = Client.objects.annotate(
        full_name_search=Concat('first_name', Value(' '), 'last_name')
    ).filter(
        Q(first_name__icontains=full_name) |
        Q(last_name__icontains=full_name) |
        Q(full_name_search__icontains=full_name)
    )

    print(f"Query: {full_name}")
    print(f"Results: {results.count()} clients found")

    if results.exists():
        print("✅ PASS: Full name search works at ORM level")
        for r in results[:3]:
            print(f"  - Found: {r.first_name} {r.last_name}")
    else:
        print("❌ FAIL: Full name search doesn't work at ORM level")

    print()

    print("="*80)
    print(f"TEST 2: API ViewSet - Search by Full Name '{full_name}'")
    print("="*80)

    # Test the actual viewset search method
    factory = APIRequestFactory()
    request = factory.get(f"/api/v1/clients/search/?q={full_name}&page_size=50")

    viewset = ClientViewSet()
    viewset.request = request
    viewset.format_kwarg = None

    try:
        response = viewset.search(request)

        print(f"Query: {full_name}")
        print(f"Response status: {response.status_code}")

        if hasattr(response, 'data'):
            data = response.data
            print(f"Results count: {data.get('count', 0)}")
            print(f"Clients in response: {len(data.get('clients', []))}")

            if data.get('clients'):
                print("✅ PASS: Search endpoint returns results")
                for client in data['clients'][:3]:
                    print(f"  - {client.get('first_name')} {client.get('last_name')}")
            else:
                print("❌ FAIL: Search endpoint returns no results")
        else:
            print("❌ FAIL: No data in response")

    except Exception as e:
        print(f"❌ FAIL: Exception occurred: {e}")
        import traceback
        traceback.print_exc()

    print()

    print("="*80)
    print("TEST 3: Search Variations")
    print("="*80)

    # Test different search patterns
    test_queries = [
        test_client.first_name,  # First name only
        test_client.last_name,   # Last name only
        full_name,               # Full name
        full_name.lower(),       # Lowercase
        full_name.upper(),       # Uppercase
    ]

    for query in test_queries:
        results = Client.objects.annotate(
            full_name_search=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(full_name_search__icontains=query)
        )

        status = "✅ PASS" if results.exists() else "❌ FAIL"
        print(f"{status}: '{query}' -> {results.count()} results")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print("If all tests pass, MFLP-20 is ALREADY FIXED (search works correctly)")
print("="*80)
