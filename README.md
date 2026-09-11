# Smart Money Screener — by HanSolo

Screener saham IDX berbasis **Intensity vs Price Action**.  
Mendeteksi aktivitas Smart Money menggunakan analisis volume intensity secara real-time.

## Fitur
- Filter fase: Smart Money, SM Awal, Markup, Waspada
- Filter market cap (min–max Triliun Rp)
- Filter skor sinyal (1–10)
- Parameter intensity bisa disesuaikan
- Download hasil sebagai CSV

## Cara Deploy ke Streamlit Cloud

1. Fork atau upload repo ini ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Login dengan akun GitHub
4. Klik **New app** → pilih repo ini → `app.py`
5. Klik **Deploy** — selesai, dapat link permanen

## Cara Jalankan Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Disclaimer
Indikator ini tidak selalu benar dan bukan rekomendasi investasi.
Gunakan sebagai alat bantu analisis teknikal. DYOR.
