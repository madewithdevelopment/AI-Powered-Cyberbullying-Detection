from flask import jsonify
import json
import traceback

try:
    import bully_detector
    res = bully_detector.scan_platform('whatsapp')
    print("Got response with", len(res), "items")
    
    # Try to jsonify it the way Flask does
    print("\nTrying jsonify...")
    response = jsonify(res)
    print("✅ jsonify() succeeded")
    print("Response:", response.get_json()[:500] if isinstance(response.get_json(), str) else "Dict response")
except Exception as e:
    print("\n❌ ERROR OCCURRED:")
    traceback.print_exc()
    print("\nError Type:", type(e).__name__)
    print("Error Message:", str(e))
