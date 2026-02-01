# GeminiLens

Asisten sederhana (Hobby Project) untuk mengambil teks dari layar dan menanyakannya ke Google Gemini secara instan.

## Fitur Utama

- **Cepat**: Menggunakan dynamic polling untuk respons yang lebih snappier.
- **Stealth**: Berjalan di latar belakang (Headless) menggunakan Undetected Chromedriver.
- **Sederhana**: Kontrol penuh hanya dengan tombol `Ctrl` dan mode angka.

## Mode (Dalam Tahap Pengembangan)

> [!NOTE]
> Fitur mode respon di bawah ini masih bersifat eksperimental dan terus disempurnakan.

| Mode  | Nama          | Target Output      | Status        |
| :---- | :------------ | :----------------- | :------------ |
| **1** | Super Singkat | Tepat 1 Kalimat    | Eksperimental |
| **2** | Singkat       | Maksimal 3 Kalimat | Eksperimental |
| **3** | Efektif       | Ringkas & Padat    | Stabil        |
| **4** | Detail        | Analisis Mendalam  | Eksperimental |

## Persiapan

1. Pastikan Python 3.8+ dan [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) terinstall.
2. Clone repo dan install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` menjadi `.env` dan masukkan API Key Gemini Anda.

## Cara Pakai

- Jalankan `python src/main.py`.
- **Seleksi Area**: Tekan `Ctrl` di pojok kiri atas area, lalu tekan `Ctrl` lagi di pojok kanan bawah.
- **Ubah Mode**: Tekan angka `1`, `2`, `3`, atau `4` untuk mengganti gaya jawaban.
- **Berhenti**: Tekan `ESC` untuk menutup program dan membersihkan proses browser.
