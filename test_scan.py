"""Test the scan_platform function directly to see the error."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import and test directly
from bully_detector import scan_platform

try:
    results = scan_platform("whatsapp")
    print(f"Success! Got {len(results)} results")
    for r in results[:2]:
        print(f"  User: {r['user']}, Action: {r['action']['action']}")
except Exception as e:
    import traceback
    traceback.print_exc()
