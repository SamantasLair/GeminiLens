# ScreenGemini Setup Instructions

## Prerequisites

1.  **Python 3.8+**
2.  **Tesseract OCR**
    - Install Tesseract OCR.
    - Ensure `tesseract.exe` is either in your system PATH or placed in a `tesseract` folder within this project (e.g., `ScreenGemini/tesseract/tesseract.exe`).
    - You can configure the path in `.env` if it's different.

## Installation

1.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

    _(Create a `requirements.txt` with: `pynput`, `pytesseract`, `google-generativeai`, `python-dotenv`, `pillow`, `win10toast`)_

2.  **API Key Configuration**:
    - Open `.env` file.
    - Replace `your_gemini_api_key_here` with your actual Google Gemini API key.

## Usage

1.  Run the application:

    ```bash
    python src/main.py
    ```

2.  **How to use**:
    - **Start Selection**: Press **Left Ctrl** or **Right Ctrl** once. (Mouse position is recorded as Start Point).
    - **End Selection**: Move your mouse to the diagonal corner of the text you want to capture. Press **Ctrl** again. (Mouse position is recorded as End Point).
    - **Result**: The application will capture the screen region, read the text, ask Gemini, and show the answer in a Toast notification.

3.  **Exit**:
    - Press `Ctrl+C` in the terminal to stop the program.

## Troubleshooting

- **Tesseract Not Found**: Check `TESSERACT_CMD` in `.env`.
- **No Toast**: Ensure notifications are enabled in Windows settings.
