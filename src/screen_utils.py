import pytesseract
from PIL import Image
import mss
import win32gui
import win32ui
import win32con
import win32api
import ctypes

try:
    from . import config
except ImportError:
    import config
import os

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

def capture_gdi(x, y, width, height):
    """
    Fallback screen capture using Windows GDI (legacy method).
    Often works when MSS/DXGI returns black screens.
    """
    try:
        hwin = win32gui.GetDesktopWindow()
        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)
        memdc.BitBlt((0, 0), (width, height), srcdc, (x, y), win32con.SRCCOPY)
        
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        
        # Cleanup
        srcdc.DeleteDC()
        memdc.DeleteDC()
        win32gui.ReleaseDC(hwin, hwindc)
        win32gui.DeleteObject(bmp.GetHandle())
        
        return img
    except Exception as e:
        print(f"GDI Capture failed: {e}")
        return None

import time
from pynput.keyboard import Key, Controller
import win32clipboard
from io import BytesIO

keyboard = Controller()

def capture_clipboard(x, y, width, height):
    """
    Nuclear Option: Simulate PrtSc key and grab from clipboard.
    Bypasses almost all black-screen issues caused by hardware acceleration.
    """
    try:
        # Clear clipboard first
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
        
        # Press PrintScreen
        keyboard.press(Key.print_screen)
        keyboard.release(Key.print_screen)
        
        # Wait for clipboard to populate (critical)
        time.sleep(0.5)
        
        # Read from clipboard
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
            data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
            win32clipboard.CloseClipboard()
            
            # Create image from DIB data
            # DIB header is 40 bytes. We can wrap this in BMP for PIL.
            # However, simpler way is to try grabbing CF_BITMAP if available or use ImageGrab.grabclipboard()
            # Let's verify if PIL can grab it directly which is cleaner.
            pass
        else:
            win32clipboard.CloseClipboard()
            print("Clipboard does not contain image.")
            return None

        # Use PIL's grabclipboard as it handles the format parsing
        from PIL import ImageGrab
        img = ImageGrab.grabclipboard()
        
        if img:
            # Crop to region
            # Coordinates need to be relative to the monitor if PrtSc captures full virtual screen
            # Assuming single monitor or PrtSc captures all.
            # Crop: (left, top, right, bottom)
            right = x + width
            bottom = y + height
            img = img.crop((x, y, right, bottom))
            return img
            
    except Exception as e:
        print(f"Clipboard Capture failed: {e}")
        try:
             win32clipboard.CloseClipboard()
        except:
            pass
    return None

import pyautogui

def capture_pyautogui(x, y, width, height):
    """
    Fallback using PyAutoGUI (wraps pyscreeze).
    """
    try:
        # pyautogui.screenshot() returns a PIL image
        img = pyautogui.screenshot(region=(x, y, width, height))
        return img
    except Exception as e:
        print(f"PyAutoGUI Failed: {e}")
        return None

def capture_screen(x1, y1, x2, y2):
    """
    Captures screen using:
    1. PyAutoGUI (Often most reliable on simple Windows setups)
    2. MSS (Fastest)
    3. GDI (Legacy)
    4. Clipboard (Nuclear)
    """
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    
    # 0. DEBUG: Try to grab FULL screen first to verify visibility
    try:
        full_debug = pyautogui.screenshot()
        # Save occasionally or if requested, but for now we rely on the caller to save result.
        # Check if full screen is black
        if full_debug.getextrema() == ((0, 0), (0, 0), (0, 0)):
             print("CRITICAL: Even Full Screen PyAutoGUI capture is BLACK!")
    except:
        pass

    # 1. Try PyAutoGUI First (Standardizing on the most "user-friendly" lib)
    img = capture_pyautogui(left, top, width, height)
    
    # Check black
    if is_image_black(img):
        print("PyAutoGUI returned black. Trying MSS...")
        
        # 2. Try MSS
        try:
            with mss.mss() as sct:
                monitor = {"top": top, "left": left, "width": width, "height": height}
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"MSS Failed: {e}")

    # 3. Try GDI
    if is_image_black(img):
        print("MSS returned black. Trying GDI...")
        img = capture_gdi(left, top, width, height)

    # 4. Clipboard
    if is_image_black(img):
        print("GDI returned black. Trying Clipboard...")
        img = capture_clipboard(left, top, width, height)
    
    # 5. Window-Level Capture (PrintWindow) - Final Resort
    if is_image_black(img):
        print("Clipboard returned black. Trying Specific Window Capture (PrintWindow)...")
        # Find window under center of region
        cx, cy = left + width//2, top + height//2
        try:
             hwnd = win32gui.WindowFromPoint((cx, cy))
             if hwnd:
                 # We need to capture the window, then crop relative to it
                 # get window rect
                 l_win, t_win, r_win, b_win = win32gui.GetWindowRect(hwnd)
                 
                 # Capture Window
                 w_win = r_win - l_win
                 h_win = b_win - t_win
                 
                 hwindc = win32gui.GetWindowDC(hwnd)
                 srcdc = win32ui.CreateDCFromHandle(hwindc)
                 memdc = srcdc.CreateCompatibleDC()
                 bmp = win32ui.CreateBitmap()
                 bmp.CreateCompatibleBitmap(srcdc, w_win, h_win)
                 memdc.SelectObject(bmp)
                 
                 # FORCE PRINTWINDOW: This is required for Chrome/Edge/Modern Apps
                 # BitBlt fails (Black Screen) on Hardware Accelerated windows.
                 # PW_RENDERFULLCONTENT (2) forces the window to render for us.
                 result = ctypes.windll.user32.PrintWindow(hwnd, memdc.GetSafeHdc(), 2)
                 
                 if result == 0:
                      # Only if PrintWindow fails, try BitBlt as backup
                      print("[WARN] PrintWindow failed, trying BitBlt...")
                      memdc.BitBlt((0, 0), (w_win, h_win), srcdc, (0, 0), win32con.SRCCOPY)
                 
                 bmpinfo = bmp.GetInfo()
                 bmpstr = bmp.GetBitmapBits(True)
                 win_img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
                 
                 # Crop our global region from this local window image
                 # Global: left, top
                 # Window: l_win, t_win
                 # Local: left - l_win, top - t_win
                 local_x = left - l_win
                 local_y = top - t_win
                 img = win_img.crop((local_x, local_y, local_x + width, local_y + height))
                 
                 srcdc.DeleteDC()
                 memdc.DeleteDC()
                 win32gui.ReleaseDC(hwnd, hwindc)
                 win32gui.DeleteObject(bmp.GetHandle())

        except Exception as e:
            print(f"Window Capture Failed: {e}")

    return img

def is_image_black(img):
    if img is None: return True
    return img.getextrema() == ((0, 0), (0, 0), (0, 0))

def extract_text(image: Image.Image) -> str:
    """
    Extracts text from the given PIL Image using Tesseract OCR.
    """
    try:
        # Check if tesseract cmd exists
        if not os.path.exists(config.TESSERACT_CMD):
             return f"Error: Tesseract not found at {config.TESSERACT_CMD}. Please check .env or install it."

        # Preprocessing for better OCR
        # 1. Convert to grayscale
        image = image.convert('L')
        
        # 2. Scale up (2x) to handle small text on screen
        width, height = image.size
        image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        
        # 3. Optional: Thresholding (binarization) can help if contrast is low, 
        # but grayscale + resize is usually enough for screen text.

        # Configure Tesseract
        # --psm 6: Assume a single uniform block of text. Great for blocks of text or single lines.
        custom_config = r'--oem 3 --psm 6'
        
        text = pytesseract.image_to_string(image, config=custom_config)
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"
