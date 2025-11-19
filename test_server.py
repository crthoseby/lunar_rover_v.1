import requests
import time

print("Testing Rover Server Connection...")
print("="*50)

try:
    # Test 1: Server alive
    print("\n1. Testing server connection...")
    r = requests.get("http://localhost:5000/api/status", timeout=2)
    print(f"   ✓ Server responding: {r.status_code}")
    print(f"   Status: {r.json()}")
    
    # Test 2: Send forward command
    print("\n2. Sending FORWARD command...")
    r = requests.post("http://localhost:5000/api/command/forward", 
                     headers={'Content-Type': 'application/json'},
                     timeout=2)
    print(f"   ✓ Response: {r.json()}")
    
    # Test 3: Check logs
    time.sleep(0.5)
    print("\n3. Checking logs...")
    r = requests.get("http://localhost:5000/api/logs/recent?count=10", timeout=2)
    logs = r.json()['logs']
    print(f"   ✓ Found {len(logs)} log entries:")
    for log in logs[-5:]:
        print(f"     [{log['timestamp']}] {log['type']}: {log['message']}")
    
    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED - Server is working!")
    print("\nNow open browser to: http://localhost:5000")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nMake sure server is running: python web_server.py")
