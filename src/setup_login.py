import undetected_chromedriver as uc
import os
import time

# Same profile path as the service
PROFILE_DIR = os.path.join(os.getcwd(), "chrome_profile")

def setup_login():
    print("="*60)
    print("SELENIUM LOGIN SETUP (Stealth Mode)")
    print("="*60)
    print(f"Profile Path: {PROFILE_DIR}")
    print("Launching Chrome... Please log in to Google (Gemini) manually.")
    print("The browser will look standard but has anti-detection features active.")
    print("-" * 60)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--window-size=1280,720")
    
    # UC handles driver download automatically usually
    print("Starting Undetected Chrome...")
    try:
        driver = uc.Chrome(options=options, version_main=144)
        driver.get("https://gemini.google.com/app")

        
        print("Browser opened. Login manually.")
        print("Close the browser window when you are done.")
        
        try:
            while True:
                # Check if window is still open
                try:
                    # Accessing property works if browser is open
                    _ = driver.window_handles
                    time.sleep(1)
                except:
                    break
        except KeyboardInterrupt:
            pass
            
        print("Browser closed. Setup complete!")
        
    except Exception as e:
        print(f"Error launching Chrome: {e}")
        print("Make sure no other Chrome instances are running with this profile!")

if __name__ == "__main__":
    setup_login()

