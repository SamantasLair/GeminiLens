from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# Same profile path as the service
PROFILE_DIR = os.path.join(os.getcwd(), "chrome_profile")

def setup_login():
    print("="*60)
    print("SELENIUM LOGIN SETUP")
    print("="*60)
    print(f"Profile Path: {PROFILE_DIR}")
    print("Launching Chrome... Please log in to Google (Gemini) manually.")
    print("After logging in, you can close the browser window.")
    print("-" * 60)

    options = Options()
    options.add_argument(f"user-data-dir={PROFILE_DIR}")
    options.add_argument("--window-size=1280,720")
    # NO HEADLESS here, so user can see
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://gemini.google.com/app")
    
    print("Browser opened. Waiting for you to close it...")
    
    try:
        while True:
            # Check if window is still open
            try:
                _ = driver.window_handles
                time.sleep(1)
            except:
                break
    except KeyboardInterrupt:
        pass
    
    print("Browser closed. Setup complete!")

if __name__ == "__main__":
    setup_login()
