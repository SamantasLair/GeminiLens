import os
import sys
import time
import ctypes
import pyautogui
import mss
import platform
import struct
from PIL import Image, ImageStat
from config import TESSERACT_CMD

import os
import sys
import time
import ctypes
import pyautogui
import mss
import platform
import struct
import win32gui
import win32api
import win32con
from PIL import Image, ImageStat
from screen_utils import capture_gdi, capture_clipboard

def log(header, status, detailed_msg=""):
    print(f"[{header: <20}] {status: <10} | {detailed_msg}")

def test_system_diagnostics():
    print("="*80)
    print(f"SCREEN GEMINI DIAGNOSTICS v3.0 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # --- SECTION 1: ENVIRONMENT & SECURITY ---
    
    # H1: User Privileges
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        status = "PASS" if is_admin else "FAIL"
        log("1. PRIVILEGE", status, f"Admin Rights: {bool(is_admin)}")
    except:
        log("1. PRIVILEGE", "ERR", "Check failed")

    # H2: Secure Desktop / Session 0
    try:
        user32 = ctypes.windll.user32
        hDesk = user32.OpenInputDesktop(0, False, 0x0100)
        if not hDesk:
            log("2. DESKTOP ACC", "FAIL", "Input Desktop Locked/Secure (UAC/Saver)")
        else:
            log("2. DESKTOP ACC", "PASS", "Input Desktop Accessible")
            user32.CloseDesktop(hDesk)
    except:
        log("2. DESKTOP ACC", "ERR", "API Call Failed")

    # H3: API Architecture
    bits = struct.calcsize("P") * 8
    log("3. ARCHITECTURE", "INFO", f"Python {bits}-bit on {platform.system()} {platform.release()}")

    # H4: DPI Awareness
    try:
        awareness = ctypes.c_int()
        ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
        log("4. DPI LEVEL", "INFO", f"Awareness Level: {awareness.value}")
    except:
         log("4. DPI LEVEL", "WARN", "Unknown")

    # --- SECTION 2: HARDWARE & TOPOLOGY ---

    # H5: Monitor Topology
    try:
        with mss.mss() as sct:
            for i, m in enumerate(sct.monitors):
                log(f"5. MONITOR #{i}", "INFO", f"{m['width']}x{m['height']} @ ({m['left']}, {m['top']})")
    except:
        log("5. MONITOR", "FAIL", "Could not list monitors")

    # H6: Direct GDI Pixel Probe (Low Level)
    try:
        hdc = win32gui.GetDC(0)
        color = win32gui.GetPixel(hdc, 100, 100) # Probe (100,100)
        win32gui.ReleaseDC(0, hdc)
        log("6. GDI PROBE", "PASS", f"Pixel(100,100) ColorInt: {color}")
    except:
        log("6. GDI PROBE", "FAIL", "GetPixel Failed")

    # --- SECTION 3: CAPTURE METHOD BENCHMARK ---
    
    methods = [
        ("7. PyAutoGUI", lambda: pyautogui.screenshot()), # H7
        ("8. MSS", lambda: capture_mss_wrapper()),        # H8
        ("9. GDI Win32", lambda: capture_gdi_wrapper()),  # H9
        ("10. Clipboard", lambda: capture_clipboard_wrapper()) # H10
    ]
    
    if not os.path.exists("diagnosis_v3"): os.makedirs("diagnosis_v3")

    print("-" * 80)
    print(f"{'METHOD':<20} | {'TIME (ms)':<10} | {'STATUS':<10} | {'MEAN COLOR'}")
    print("-" * 80)

    for name, func in methods:
        start = time.time()
        try:
            img = func()
            duration = (time.time() - start) * 1000
            
            if img:
                # Save for inspection
                safe_name = name.split(". ")[1].replace(" ", "_")
                img.save(f"diagnosis_v3/{safe_name}.png")
                
                # Analyze Blackness
                stat = ImageStat.Stat(img)
                mean_val = stat.mean
                is_black = sum(mean_val) < 5 # Allowance for compression noise
                
                status = "BLACK" if is_black else "OK"
                color_str = f"[{int(mean_val[0])},{int(mean_val[1])},{int(mean_val[2])}]"
                
                print(f"{name:<20} | {duration:<10.2f} | {status:<10} | {color_str}")
            else:
                print(f"{name:<20} | {duration:<10.2f} | {'NONE':<10} | N/A")
                
        except Exception as e:
            print(f"{name:<20} | {'ERR':<10} | {'CRASH':<10} | {str(e)[:30]}")

    # --- SECTION 4: SYSTEM INTEGRITY ---
    
    # H11: Disk Write
    try:
        with open("diag_test.tmp", "w") as f: f.write("ok")
        os.remove("diag_test.tmp")
        log("11. DISK I/O", "PASS", "Write OK")
    except:
        log("11. DISK I/O", "FAIL", "Write Failed")

    # H12: Tesseract
    if os.path.exists(TESSERACT_CMD):
        log("12. TESSERACT", "PASS", "Found")
    else:
        log("12. TESSERACT", "FAIL", "Not Found")
        
    print("="*80)
    print("Check 'diagnosis_v3/' folder for captured images.")

def capture_mss_wrapper():
    with mss.mss() as sct:
        return Image.frombytes("RGB", sct.grab(sct.monitors[1]).size, sct.grab(sct.monitors[1]).bgra, "raw", "BGRX")

def capture_gdi_wrapper():
    w, h = pyautogui.size()
    return capture_gdi(0, 0, w, h)

def capture_clipboard_wrapper():
    w, h = pyautogui.size()
    return capture_clipboard(0, 0, w, h)

if __name__ == "__main__":
    test_system_diagnostics()
