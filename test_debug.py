from analyzer import analyze_complaint
import json

complaint = {
    'id': 'test-1',
    'customer': 'Test User',
    'channel': 'Web',
    'subject': 'Test Question',
    'message': 'How to run a python file?'
}

try:
    result = analyze_complaint(complaint)
    print(json.dumps(result, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
