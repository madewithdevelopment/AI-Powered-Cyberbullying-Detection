import json
import traceback

try:
    import bully_detector
    res = bully_detector.scan_platform('whatsapp')
    # Try to serialize to JSON to check if that's the issue
    json_str = json.dumps(res, default=str)
    print("Serialization OK - response has", len(res), "items")
except Exception as e:
    print("\n❌ ERROR OCCURRED:")
    traceback.print_exc()
    print("\nError Type:", type(e).__name__)
    print("Error Message:", str(e))
