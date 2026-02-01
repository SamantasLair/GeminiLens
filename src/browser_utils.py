import time
import pyautogui
import win32gui
import win32con
import win32clipboard
from PIL import ImageGrab
import ctypes
import re

# Increase safety delays
pyautogui.PAUSE = 0.5

def capture_browser_gemini(prompt_text, mode=3):
    """
    Automates Chrome to query Gemini Web.
    STEALTH MODE: Moves window off-screen to perform actions, then minimizes.
    """
    # PROMPT TEMPLATES (Matches gemini_service)
    suffix = ""
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
        prefix = "INSTRUKSI KHUSUS: JAWAB DENGAN LUGAS, AKURAT, DAN OBJEKTIF. HINDARI BASA-BASI."
        suffix = "\n\nINGAT: FOKUS PADA INTI PERMASALAHAN."
    
    final_text = f"{prefix}\n\n{prompt_text}\n{suffix}"

    print("[BROWSER] Looking for Google Chrome...")
    
    hwnd = find_window_by_title("Google Chrome")
    if not hwnd:
        hwnd = find_window_by_title("Chrome")
    
    if not hwnd:
        return "Error: Google Chrome window not found. Please open Chrome."

    try:
        # Get current window placement to restore later? 
        # For now, we just want to hide it.
        
        # 1. STEALTH: Move window off-screen
        # -3000 x coordinate ensures it's likely invisible on most setups
        print("[BROWSER] Hiding Chrome (Off-screen isolation)...")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.MoveWindow(hwnd, -3000, 0, 1024, 768, True)
        
        # 2. Focus (Windows thinks it's visible, so input works)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5) 
        
        # New Tab
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)
        
        # URL
        pyautogui.write('https://gemini.google.com/app')
        pyautogui.press('enter')
        
        # Wait for load 
        print("[BROWSER] Waiting 4s for Gemini to load...")
        time.sleep(4.0)
        
        # Typing prompt
        pyautogui.write(final_text, interval=0.005) # Fast typing
        pyautogui.press('enter')
        
        # Wait for generation
        print("[BROWSER] Automating... (Waiting 8s)")
        time.sleep(8.0)
        
        # Scraping
        # Click to ensure focus on page content
        print("[BROWSER] Selecting text...")
        center_x, center_y = 1024 // 2, 768 // 2 # Center of our off-screen window
        pyautogui.click(center_x, center_y)
        time.sleep(0.2)
        
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.8) # Increased wait for massive selection
        
        # Double Copy for safety
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        
        # Get Clipboard
        result_text = get_clipboard_text()
        
        # 3. CLEANUP: Minimize immediately
        print("[BROWSER] Minimizing Chrome...")
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        
        return parse_gemini_clipboard(result_text)

    except Exception as e:
        # Emergency cleanup: Try to minimize if error
        try: win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        except: pass
        return f"Browser Automation Error: {e}"

def find_window_by_title(partial_title):
    hwnd_found = None
    def callback(hwnd, extra):
        nonlocal hwnd_found
        title = win32gui.GetWindowText(hwnd)
        if partial_title.lower() in title.lower() and win32gui.IsWindowVisible(hwnd):
            hwnd_found = hwnd
    win32gui.EnumWindows(callback, None)
    return hwnd_found

def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data
    except Exception:
        try:
            win32clipboard.CloseClipboard()
        except: pass
        return ""

def parse_gemini_clipboard(full_text):
    """
    Parses the massive Ctrl+A text to find the latest Gemini response.
    Gemini Web structure usually puts user prompt then response.
    """
    if not full_text: return "No text copied from browser."
    
    # Heuristic: Find the LAST occurrence of "share\nmore_vert" or standard UI elements
    # Or split by the User's prompt?
    
    # Simple Heuristic: Return the last 2000 characters for now, logic can be refined.
    # Actually, Gemini web usually has "Gemini" label above the response
    
    # Let's try to look for the user prompt inside the text.
    # But we don't know exactly how it was typed/formatted.
    
    return "BROWSER ANSWER (Raw Capture):\n" + full_text[-1000:]
