import json
import traceback

try:
    import bully_detector
    res = bully_detector.scan_platform('whatsapp')
    print(json.dumps(res[:2], indent=2, default=str))
except Exception as e:
    print("Exception when calling scan_platform:")
    traceback.print_exc()
