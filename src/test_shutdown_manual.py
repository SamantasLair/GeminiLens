
import sys
import os
import time

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

try:
    import selenium_service
except ImportError:
    # Try assuming we are in src
    try:
        sys.path.append(os.path.join(os.getcwd(), 'src'))
        import selenium_service
    except ImportError:
        print("Could not import selenium_service. Run this from project root or src.")
        sys.exit(1)

def test_shutdown():
    print("TEST: Initializing Driver...")
    try:
        # We use headless=True to avoid popping up windows if possible, 
        # though init_driver forces some options.
        driver = selenium_service.init_driver(headless=True)
        print("TEST: Driver initialized (UC). ID:", driver.session_id)
        
        print("TEST: specific check - is it alive?")
        driver.title # check connection
        
        print("TEST: Calling close_driver()...")
        selenium_service.close_driver()
        
        print("TEST: Driver closed.")
        
        if selenium_service.driver is None:
            print("PASS: driver variable is None.")
        else:
            print("FAIL: driver variable is NOT None.")
            
        print("TEST: Attempting double close (should not crash)...")
        selenium_service.close_driver()
        print("PASS: Double close safe.")

    except Exception as e:
        print(f"FAIL: Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_shutdown()
