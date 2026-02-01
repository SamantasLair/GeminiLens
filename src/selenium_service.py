from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Persistent Profile Path
PROFILE_DIR = os.path.join(os.getcwd(), "chrome_profile")

driver = None

def init_driver(headless=True):
    global driver
    if driver: return driver

    print("[SELENIUM] Initializing Chrome Driver (Undetected)...")
    import undetected_chromedriver as uc
    
    options = uc.ChromeOptions()
    
    # Critical: Use a custom profile to save Login state
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    
    if headless:
        options.add_argument("--headless=new") # Modern headless
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage") 
    options.add_argument("--log-level=3") # Quiet
    
    print("[SELENIUM] Loading Gemini...")
    # Fix Version Mismatch: Explicitly request version 144
    driver = uc.Chrome(options=options, version_main=144)

    driver.get("https://gemini.google.com/app")
    
    # Wait for either Login Page or Chat Interface
    time.sleep(3)
    
    if "accounts.google.com" in driver.current_url:
        print("\n" + "!"*60)
        print("[ACTION REQUIRED] You need to login to Google once.")
        print("Please restart program in HEADFUL mode (edit code temporarily) or login manually.")
        print("!"*60 + "\n")
        # For now we assume they might be logged in or we'll fail gracefully
    
    return driver

def _get_last_response_text(driver):
    """Helper to scrape the very last response text currently on screen."""
    response_selectors = [
        (By.TAG_NAME, "model-response"),           
        (By.CSS_SELECTOR, ".markdown"),            
        (By.CSS_SELECTOR, ".message-content")
    ]
    candidates = []
    for method, query in response_selectors:
        try:
            found = driver.find_elements(method, query)
            if found: candidates = found; break
        except: continue
    
    if candidates:
        for node in reversed(candidates):
            try:
                txt = driver.execute_script("return arguments[0].innerText;", node).strip()
                if txt: return txt
            except: continue
    return ""

def query_selenium(prompt_text, mode=3):
    global driver
    try:
        if not driver:
            init_driver(headless=True)
            
        suffix = ""
        # PROMPT TEMPLATES (Sandwich Strategy)
        if mode == 1: 
            prefix = "INSTRUKSI KHUSUS: JAWAB HANYA 1 KALIMAT. JANGAN MEMBERIKAN PENJELASAN."
            suffix = "\n\nINGAT: HANYA 1 KALIMAT SAJA."
        elif mode == 2: 
            prefix = "INSTRUKSI KHUSUS: JAWAB MAKSIMAL 3 KALIMAT. LANGSUNG KE INTI."
            suffix = "\n\nINGAT: MAKSIMAL 3 KALIMAT."
        elif mode == 4: 
            prefix = "INSTRUKSI KHUSUS: BERIKAN ANALISIS KRITIS DAN MENDALAM. SERTAKAN BUKTI TEORETIS JIKA ADA."
            suffix = "\n\nINGAT: WAJIB KOMPREHENSIF DENGAN STRUKTUR YANG JELAS."
        else: 
            # Mode 3 (Effective / Standard)
            prefix = "INSTRUKSI KHUSUS: JAWAB DENGAN LUGAS, AKURAT, DAN OBJEKTIF. HINDARI BASA-BASI."
            suffix = "\n\nINGAT: FOKUS PADA INTI PERMASALAHAN."
        
        final_text = f"{prefix}\n\n{prompt_text}\n{suffix}"
            
        # 1. Find Input Box
        try:
           input_box = WebDriverWait(driver, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
           )
        except:
            print("[SELENIUM] Input box not found.")
            driver.save_screenshot("debug_input_fail.png")
            return "Error: Input box not found."

        # SNAPSHOT PREVIOUS ANSWER (To avoid stale reads)
        previous_response = _get_last_response_text(driver)
        # print(f"[DEBUG] Previous response end: ...{previous_response[-20:] if previous_response else 'None'}")

        # 2. Clear & Type
        try: driver.execute_script("arguments[0].innerText = '';", input_box)
        except: input_box.clear()
        
        driver.execute_script("arguments[0].innerText = arguments[1];", input_box, final_text)
        input_box.send_keys(" ") # Trigger event
        input_box.send_keys(Keys.ENTER)
        
        # 3. FAST SEND VERIFICATION
        sent = False
        for _ in range(20): 
            try:
                if not input_box.text.strip():
                    sent = True
                    break
            except: break 
            time.sleep(0.1)
            
        if not sent:
             print("[SELENIUM] Enter might have failed, clicking Send...")
             try:
                 # Strict selectors
                 send_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Send message'], button[aria-label='Kirim pesan']")
                 for btn in send_btns:
                     if btn.is_displayed():
                         driver.execute_script("arguments[0].click();", btn)
                         break
             except: pass
        
        print("[SELENIUM] Generating...")
        
        # 4. AGGRESSIVE COMPLETION DETECTION
        start_time = time.time()
        
        # PHASE 1: WAIT FOR NEW CONTENT TO APPEAR (Anti-Stale)
        # We wait until the scraper sees text that is DIFFERENT from previous_response.
        new_content_started = False
        for _ in range(50): # Max 10s to start
            current_text = _get_last_response_text(driver)
            
            # If we had no previous response, any text is new.
            # If we had previous response, current text must contain previous + new OR be completely different (if new chat).
            # But Gemini usually appends. So the last element might be the SAME as previous if new one hasn't appeared.
            # actually, _get_last_response_text gets the *last* element. A new element should appear.
            
            if current_text and current_text != previous_response:
                new_content_started = True
                break
            
            # Check for Stop button (Strong indicator of activity)
            try:
                stop_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Stop'], button[aria-label*='Berhenti']")
                if any(btn.is_displayed() for btn in stop_btns):
                    new_content_started = True
                    break
            except: pass
            
            time.sleep(0.2)
            
        if not new_content_started:
            print("[WARN] No new content detected after 10s.")
            # We continue anyway, hoping stability check catches something, or we return what we have (might be stale).
        
        # PHASE 2: WAIT FOR COMPLETION (Stability)
        final_text = ""
        stable_count = 0
        last_text_len = 0
        
        for i in range(150): # 30s max
            time.sleep(0.2)
            
            current_text = _get_last_response_text(driver)
            
            # If we are stuck on previous response, skip this cycle (unless we timed out Phase 1)
            if new_content_started and current_text == previous_response:
                 # This shouldn't happen if new_content_started is True via text change
                 # But if via Stop button, maybe text hasn't rendered yet.
                 continue

            if current_text:
                if len(current_text) == last_text_len:
                    stable_count += 1
                else:
                    stable_count = 0 
                
                last_text_len = len(current_text)
                final_text = current_text
                
                if len(current_text) > 5 and stable_count >= 3: 
                    # Double check Stop button
                    try:
                        stop_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Stop'], button[aria-label*='Berhenti']")
                        if any(btn.is_displayed() for btn in stop_btns):
                            stable_count = 0 
                            continue
                    except: pass
                    
                    print(f"[SELENIUM] Done in {time.time() - start_time:.1f}s.")
                    break
            
            if (time.time() - start_time) > 25:
                break

        if final_text:
             # Sanity check: If we returned the EXACT same text as before, mark it.
             if final_text == previous_response:
                 return f"Error: Stale response detected. (Gemini did not update UI).\nResponse:\n{final_text}"
             return final_text
        else:
             driver.save_screenshot("debug_fail_fast.png")
             return "No response found."

    except Exception as e:
        print(f"Selenium Error: {e}")
        return f"Error: {e}"



def close_driver():
    global driver
    if driver:
        print("[SELENIUM] Closing browser...")
        try:
            driver.quit()
        except Exception as e:
            print(f"[SELENIUM] Warning during shutdown: {e}")
        finally:
            driver = None
