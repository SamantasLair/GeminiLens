# FIX: Black Screen on Laptop (Dual GPU Issue)

**Masalah:** Laptop Anda kemungkinan memiliki 2 GPU (Intel + NVIDIA/AMD). Python berjalan di satu GPU, sementara layar di GPU lain, sehingga hasil screenshot menjadi **HITAM**.

**SOLUSI:** Anda harus memaksa Python untuk menggunakan **Power Saving Mode** (Integrated Graphics).

## Langkah-langkah:

1.  **Copy Path Python ini:**

    ```
    C:\Python311\python.exe
    ```

2.  **Buka Graphics Settings:**
    - Tekan tombol `Windows` + `S`.
    - Ketik **"Graphics Settings"** (atau "Pengaturan Grafis").
    - Tekan **Enter**.

3.  **Tambahkan Python:**
    - Di bagian "Choose an app to set preference", pilih **Desktop app**.
    - Klik **Browse**.
    - Paste/Cari file `python.exe` dari langkah 1.
    - Klik **Add**.

4.  **Ubah Setting:**
    - Klik icon **Python** yang baru muncul di list.
    - Klik **Options**.
    - Pilih **Power Saving** (biasanya GPU: Intel HD Graphics).
    - Klik **Save**.

5.  **Restart Program:**
    - Tutup terminal Anda.
    - Buka lagi (Run as Administrator).
    - Jalankan programnya.
