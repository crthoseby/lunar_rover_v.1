"""
Lunar Rover System Diagnostic Tool
Tests all components and APIs to verify system health
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
INFO = "\033[94mℹ INFO\033[0m"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_server_connection():
    """Test if server is running and accessible"""
    print(f"\n{INFO} Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code == 200:
            print(f"{PASS} Server is running at {BASE_URL}")
            return True
        else:
            print(f"{FAIL} Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"{FAIL} Cannot connect to server: {e}")
        print(f"{INFO} Make sure server is running: python web_server.py")
        return False

def test_status_api():
    """Test /api/status endpoint"""
    print(f"\n{INFO} Testing status API...")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=2)
        data = response.json()
        print(f"{PASS} Status API responding")
        print(f"    Status: {data.get('status')}")
        print(f"    Speed: {data.get('speed')}%")
        print(f"    Commands sent: {data.get('commands_sent')}")
        return True
    except Exception as e:
        print(f"{FAIL} Status API failed: {e}")
        return False

def test_logs_api():
    """Test /api/logs/recent endpoint"""
    print(f"\n{INFO} Testing logs API...")
    try:
        response = requests.get(f"{BASE_URL}/api/logs/recent?count=5", timeout=2)
        data = response.json()
        logs = data.get('logs', [])
        print(f"{PASS} Logs API responding")
        print(f"    Log entries: {len(logs)}")
        if logs:
            print(f"    Latest: {logs[-1].get('message')}")
        return True
    except Exception as e:
        print(f"{FAIL} Logs API failed: {e}")
        return False

def test_command_api(command="forward"):
    """Test sending a command"""
    print(f"\n{INFO} Testing command API: {command.upper()}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/command/{command}",
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        data = response.json()
        if data.get('success'):
            print(f"{PASS} Command '{command}' executed successfully")
            return True
        else:
            print(f"{FAIL} Command failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"{FAIL} Command API failed: {e}")
        return False

def test_command_logging():
    """Test if commands appear in logs"""
    print(f"\n{INFO} Testing command logging...")
    
    # Get initial log count
    response1 = requests.get(f"{BASE_URL}/api/logs/recent?count=50")
    initial_count = len(response1.json().get('logs', []))
    
    # Send command
    print(f"    Sending STOP command...")
    requests.post(f"{BASE_URL}/api/command/stop", 
                  headers={'Content-Type': 'application/json'},
                  timeout=5)
    
    # Wait a moment
    time.sleep(0.5)
    
    # Check logs again
    response2 = requests.get(f"{BASE_URL}/api/logs/recent?count=50")
    final_count = len(response2.json().get('logs', []))
    
    if final_count > initial_count:
        print(f"{PASS} Command logged successfully")
        print(f"    Log entries: {initial_count} → {final_count}")
        return True
    else:
        print(f"{FAIL} Command not logged")
        print(f"    Log entries unchanged: {initial_count}")
        return False

def test_ground_conditions():
    """Test ground conditions API"""
    print(f"\n{INFO} Testing ground conditions API...")
    try:
        response = requests.get(f"{BASE_URL}/api/ground/status", timeout=2)
        data = response.json()
        print(f"{PASS} Ground conditions API responding")
        print(f"    Environment: {data.get('environment')}")
        print(f"    Terrain: {data.get('terrain_type')}")
        print(f"    Gravity: {data.get('gravity')} m/s²")
        return True
    except Exception as e:
        print(f"{FAIL} Ground conditions API failed: {e}")
        return False

def test_camera_feed():
    """Test camera feed endpoint"""
    print(f"\n{INFO} Testing camera feed...")
    try:
        response = requests.get(f"{BASE_URL}/video_feed", timeout=2, stream=True)
        if response.status_code == 200:
            print(f"{PASS} Camera feed is streaming")
            return True
        else:
            print(f"{FAIL} Camera feed returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"{FAIL} Camera feed failed: {e}")
        return False

def run_all_tests():
    """Run complete diagnostic suite"""
    print_header("LUNAR ROVER SYSTEM DIAGNOSTICS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    results = []
    
    # Core tests
    results.append(("Server Connection", test_server_connection()))
    if not results[-1][1]:
        print(f"\n{FAIL} Cannot proceed without server connection")
        return
    
    results.append(("Status API", test_status_api()))
    results.append(("Logs API", test_logs_api()))
    results.append(("Command API", test_command_api("stop")))
    results.append(("Command Logging", test_command_logging()))
    results.append(("Ground Conditions", test_ground_conditions()))
    results.append(("Camera Feed", test_camera_feed()))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = PASS if result else FAIL
        print(f"{status} {test_name}")
    
    print(f"\n{'='*60}")
    if passed == total:
        print(f"{PASS} ALL TESTS PASSED ({passed}/{total})")
        print("\n🎉 System is fully operational!")
        print("\nYou can now:")
        print("  • Control rover from http://localhost:5000")
        print("  • Deploy to Raspberry Pi using setup_pi.sh")
        print("  • Access from phone/tablet on same network")
    else:
        print(f"{FAIL} SOME TESTS FAILED ({passed}/{total} passed)")
        print("\n⚠️  Check failed tests above for details")
    print('='*60 + "\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nDiagnostics interrupted by user")
    except Exception as e:
        print(f"\n{FAIL} Unexpected error: {e}")
