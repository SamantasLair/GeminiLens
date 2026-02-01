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

2.  **Mode Pengoperasian**:
    Tekan angka **1, 2, 3, atau 4** kapan saja (saat program tidak sedang memproses) untuk mengubah mode respon AI:

    | Mode  | Nama          | Batasan Respon          | Status        |
    | :---- | :------------ | :---------------------- | :------------ |
    | **1** | Super Singkat | **Tepat 1 Kalimat.**    | Eksperimental |
    | **2** | Singkat       | **Maksimal 3 Kalimat.** | Eksperimental |
    | **3** | Efektif       | **Lugas & Akurat.**     | Stabil        |
    | **4** | Detail        | **Analisis Kritis.**    | Eksperimental |

3.  **How to use**:
    - **Start Selection**: Tekan tombol **Ctrl** (Kiri atau Kanan) sekali di posisi awal.
    - **End Selection**: Gerakkan mouse ke sudut diagonal, lalu tekan **Ctrl** lagi.
    - **Proses**: Program akan melakukan OCR, mengirimnya ke Gemini, dan menampilkan hasil via Windows Toast.

4.  **Exit**:
    - Tekan **ESC** untuk keluar dari program dengan aman (membersihkan proses browser otomatis).

## Troubleshooting

- **Tesseract Not Found**: Check `TESSERACT_CMD` in `.env`.
- **No Toast**: Ensure notifications are enabled in Windows settings.
