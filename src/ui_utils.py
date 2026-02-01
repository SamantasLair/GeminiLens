from plyer import notification
import threading

def show_toast(title: str, message: str, duration=10):
    """
    Shows a system notification using plyer (cross-platform).
    """
    def _show():
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='ScreenGemini',
                timeout=duration
            )
        except Exception as e:
            print(f"Error showing notification: {e}")

    # Run in a daemon thread so it doesn't block exit
    t = threading.Thread(target=_show)
    t.daemon = True
    t.start()
