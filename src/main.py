import os
import time
import threading
import ctypes
import sys
from pynput import mouse, keyboard

try:
    from . import screen_utils, gemini_service, ui_utils, browser_utils, selenium_service
except ImportError:
    import screen_utils, gemini_service, ui_utils, browser_utils, selenium_service

# --- GLOBAL CONFIG & SETUP ---
try:
    # Make the application DPI aware to get correct coordinates
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except: pass

# --- WORKER FUNCTION ---
def process_region(p1, p2, app_mode='API', api_submode=2):
    """
    Background worker.
    app_mode: 'API', 'BROWSER', 'SELENIUM'
    api_submode: Int (1,2,3). Only used if app_mode == 'API'.
    """
    try:
        print(f"\n[INFO] Processing region: {p1} to {p2} | Mode: {app_mode} (Sub: {api_submode})")
        
        # Validate region
        if abs(p1[0] - p2[0]) < 10 or abs(p1[1] - p2[1]) < 10:
            print("[WARN] Region too small, skipping.")
            return

        # Capture
        image = screen_utils.capture_screen(p1[0], p1[1], p2[0], p2[1])
        
        # OCR
        text = screen_utils.extract_text(image)
        
        # Show question
        print("\n" + "-"*60)
        print("PERTANYAAN (DETECTED TEXT):")
        print(text)
        print("-" * 60)
        
        if not text.strip() or text.startswith("Error:"):
            print(f"[WARN] Skipping: No text detected.")
            return

        # ROUTING LOGIC
        answer = ""
        if app_mode == 'BROWSER':
            # Mode 2: Browser Automation (Stealth)
            print("[INFO] Sending to Google Chrome (Stealth Mode)...")
            answer = browser_utils.capture_browser_gemini(text)
        elif app_mode == 'SELENIUM':
            # Mode 3: Selenium Headless
            print("[INFO] Sending to Gemini via Selenium (Headless)...")
            answer = selenium_service.query_selenium(text)
        else:
            # Mode 1: API Service
            print(f"[INFO] Sending to Gemini API (Template {api_submode})...")
            answer = gemini_service.get_answer(text, api_submode)
        
        # Output
        print("\n" + "="*60)
        print("GEMINI ANSWER:")
        print("-" * 60)
        print(answer)
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Process Failed: {e}")
        print("-" * 60)

class AppState:
    def __init__(self):
        self.step = 0 # 0: Waiting for Start, 1: Waiting for End
        self.start_pos = (0, 0)
        self.mouse_controller = mouse.Controller()

class ScreenGeminiApp:
    def __init__(self, mode='API'):
        self.state = AppState()
        self.start_key = keyboard.Key.ctrl_l 
        self.end_key = keyboard.Key.ctrl_r
        
        self.mode = mode # 'API', 'BROWSER', 'SELENIUM'
        self.api_prompt_mode = 2 # Default to Standard for API
        self.is_busy = False # LOCK FLAG

    def on_key_release(self, key):
        # 1. LOCKOUT: If busy (automating), ignore EVERYTHING except ESC.
        if self.is_busy:
            if key == keyboard.Key.esc:
                 print("\n[EXIT] ESC pressed. Force Quit.")
                 selenium_service.close_driver()
                 os._exit(0)
            return # IGNORE ALL OTHER KEYS

        # --- ABSOLUTE EXIT ---
        if key == keyboard.Key.esc:
             # Stop any pending browser actions if possible (handled by driver.quit usually)
             print("\n[EXIT] ESC pressed. Cleaning up...")
             selenium_service.close_driver()
             
             print("Bye!")
             os._exit(0) # Force kill process
        
        # --- PROMPT MODE SWITCHING (ALL MODES) ---
        try:
            if hasattr(key, 'char'):
                if key.char == '1':
                    self.prompt_mode = 1
                    print(f"\n[PROMPT] Mode 1: Singkat (1 Kalimat)")
                elif key.char == '2':
                    self.prompt_mode = 2
                    print(f"\n[PROMPT] Mode 2: Singkat (3 Kalimat)")
                elif key.char == '3':
                    self.prompt_mode = 3
                    print(f"\n[PROMPT] Mode 3: Biasa (Standard)")
                elif key.char == '4':
                    self.prompt_mode = 4
                    print(f"\n[PROMPT] Mode 4: Detail (3 Paragraf)")
        except AttributeError: pass

        # --- CAPTURE LOGIC ---
        if key == self.start_key or key == self.end_key:
            current_pos = self.state.mouse_controller.position
            
            if self.state.step == 0:
                # First Point
                self.state.start_pos = current_pos
                self.state.step = 1
                print(f"[STEP 1] Start Point: {self.state.start_pos}. Move mouse and press CTRL again.")
            
            elif self.state.step == 1:
                # Second Point
                end_pos = current_pos
                
                # Validation inside listener to avoid thread issues
                if abs(self.state.start_pos[0] - end_pos[0]) < 10:
                    print("[WARN] Region too small. Resetting.")
                    self.state.step = 0
                    return

                self.state.step = 0 # Reset
                print(f"[STEP 2] End Point: {end_pos}. Processing...")
                
                # SET LOCK
                self.is_busy = True
                
                # Run processing in background
                t = threading.Thread(target=self.run_processing_thread, args=(self.state.start_pos, end_pos))
                t.daemon = True 
                t.start()

    def run_processing_thread(self, p1, p2):
        """Wrapper to handle lock state"""
        try:
            process_region(p1, p2, self.mode, self.prompt_mode)
        finally:
            # RELEASE LOCK
            self.is_busy = False
            print("[READY] Waiting for next capture...")

    def run(self):
        # Admin Check
        try:
           is_admin = ctypes.windll.shell32.IsUserAnAdmin()
           if not is_admin:
               print("\n" + "!"*50)
               print("WARNING: You are NOT running as Administrator.")
               print("!"*50 + "\n")
        except: pass

        print("="*60)
        
        mode_label = self.mode
        if self.mode == 'API': mode_label += " (Quota Managed)"
        if self.mode == 'BROWSER': mode_label += " (Stealth Mouse Automation)"
        if self.mode == 'SELENIUM': mode_label += " (Headless - No Interference)"
        
        print(f"ScreenGemini Started | RUNNING MODE: {mode_label}")
        
        if self.mode == 'API':
            print(" [1] Singkat  [2] Standard  [3] 5W1H")
            
        print("-" * 60)
        print("1. Press 'CTRL' to set Top-Left corner.")
        print("2. Move mouse.")
        print("3. Press 'CTRL' to set Bottom-Right corner.")
        print("PRESS 'ESC' TO QUIT INSTANTLY.")
        print("="*60)
        
        # Blocking listener
        with keyboard.Listener(on_release=self.on_key_release) as listener:
            listener.join()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*60)
    print("ScreenGemini - Select Mode")
    print("="*60)
    print("1. API MODE (Uses Quota, Best for speed)")
    print("2. BROWSER MODE (Stealth Mouse Automation, requires Chrome open)")
    print("3. SELENIUM MODE (Headless Browser, No Mouse Interference, RECOMMENDED)")
    print("-" * 60)
    
    choice = input("Select [1/2/3]: ").strip()
    
    app_mode = 'API'
    if choice == '2':
        app_mode = 'BROWSER'
    elif choice == '3':
        app_mode = 'SELENIUM'
        
    app = ScreenGeminiApp(mode=app_mode)
    app.run()

if __name__ == "__main__":
    main()
