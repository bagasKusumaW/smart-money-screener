import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="SM Screener — HanSolo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0D1117; }
[data-testid="stSidebar"] { background: #161B22; border-right: 1px solid #21262D; }
[data-testid="stSidebar"] * { color: #C9D1D9 !important; }
.main .block-container { padding-top: 1.5rem; max-width: 1100px; }
h1 { color: #00D4FF !important; font-size: 1.6rem !important; }
.sub { color: #8B949E; font-size: 0.85rem; margin-top: -10px; margin-bottom: 20px; }
.metric-row { display: flex; gap: 12px; margin-bottom: 1.2rem; flex-wrap: wrap; }
.metric-card {
    background: #161B22; border: 1px solid #21262D; border-radius: 10px;
    padding: 14px 20px; flex: 1; min-width: 120px;
}
.metric-card .val { font-size: 1.6rem; font-weight: 700; color: #00D4FF; }
.metric-card .lbl { font-size: 0.75rem; color: #8B949E; margin-top: 2px; }
.pill {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; white-space: nowrap;
}
.pill-sm   { background: #1C2F5E; color: #64B5F6; }
.pill-awal { background: #1A2A3A; color: #42A5F5; }
.pill-mk   { background: #2A1A3A; color: #CE93D8; }
.pill-wsp  { background: #3A1A1A; color: #EF9A9A; }
.pill-nrm  { background: #1E1E1E; color: #757575; }
.stDataFrame { border: 1px solid #21262D !important; border-radius: 10px !important; }
div[data-testid="stDataFrame"] tr:hover { background: #1C2330 !important; }
.warn-box {
    background: #1A1200; border: 1px solid #F57F17; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 1rem;
    color: #F9A825; font-size: 0.82rem; line-height: 1.6;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────
st.markdown("# 📊 Smart Money Screener")
st.markdown('<p class="sub">Intensity vs Price Action &nbsp;|&nbsp; by HanSolo &nbsp;|&nbsp; Data delay ~15 menit</p>', unsafe_allow_html=True)

st.markdown("""
<div class="warn-box">
⚠️ <strong>Peringatan:</strong> Indikator ini tidak selalu benar dan bukan jaminan profit.
Dirancang untuk trader yang sudah memahami analisis teknikal.
Gunakan sebagai alat bantu konfirmasi, bukan sinyal tunggal. DYOR.
</div>
""", unsafe_allow_html=True)

# ── DAFTAR SAHAM ─────────────────────────────────────────
STOCKS = [
    {"t":"BBCA.JK","n":"BBCA","mc":1200}, {"t":"BBRI.JK","n":"BBRI","mc":780},
    {"t":"BMRI.JK","n":"BMRI","mc":580},  {"t":"TLKM.JK","n":"TLKM","mc":310},
    {"t":"ADRO.JK","n":"ADRO","mc":220},  {"t":"ASII.JK","n":"ASII","mc":260},
    {"t":"ICBP.JK","n":"ICBP","mc":145},  {"t":"UNVR.JK","n":"UNVR","mc":130},
    {"t":"INDF.JK","n":"INDF","mc":115},  {"t":"BRIS.JK","n":"BRIS","mc":90},
    {"t":"GOTO.JK","n":"GOTO","mc":95},   {"t":"ANTM.JK","n":"ANTM","mc":80},
    {"t":"KLBF.JK","n":"KLBF","mc":88},   {"t":"PGAS.JK","n":"PGAS","mc":78},
    {"t":"INKP.JK","n":"INKP","mc":72},   {"t":"PTBA.JK","n":"PTBA","mc":65},
    {"t":"TBIG.JK","n":"TBIG","mc":62},   {"t":"CPIN.JK","n":"CPIN","mc":60},
    {"t":"SMGR.JK","n":"SMGR","mc":55},   {"t":"MYOR.JK","n":"MYOR","mc":55},
    {"t":"JSMR.JK","n":"JSMR","mc":48},   {"t":"MDKA.JK","n":"MDKA","mc":42},
    {"t":"MAPI.JK","n":"MAPI","mc":40},   {"t":"EXCL.JK","n":"EXCL","mc":38},
    {"t":"INCO.JK","n":"INCO","mc":35},   {"t":"SIDO.JK","n":"SIDO","mc":30},
    {"t":"HRUM.JK","n":"HRUM","mc":28},   {"t":"ACES.JK","n":"ACES","mc":22},
    {"t":"BRMS.JK","n":"BRMS","mc":18},   {"t":"WIKA.JK","n":"WIKA","mc":12},
    {"t":"EMTK.JK","n":"EMTK","mc":55},   {"t":"BUKA.JK","n":"BUKA","mc":30},
    {"t":"FILM.JK","n":"FILM","mc":18},   {"t":"RAJA.JK","n":"RAJA","mc":22},
    {"t":"HEAL.JK","n":"HEAL","mc":25},   {"t":"MAPA.JK","n":"MAPA","mc":15},
    {"t":"ARTO.JK","n":"ARTO","mc":35},   {"t":"BBTN.JK","n":"BBTN","mc":45},
    {"t":"NISP.JK","n":"NISP","mc":28},   {"t":"MEDC.JK","n":"MEDC","mc":32},
]

# ── PARAMETER ────────────────────────────────────────────
MA_LEN = 20; SPIKE = 2.0; EARLY = 1.3; MA50 = 50

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Filter Screener")
    st.markdown("---")

    fase_opt = st.selectbox(
        "Fase yang ditampilkan",
        options=["sm", "sm_awal", "markup", "all"],
        format_func=lambda x: {
            "sm":      "🔵 Smart Money saja",
            "sm_awal": "🔵🩵 Smart Money + SM Awal",
            "markup":  "🔵🩵🟣 + Markup",
            "all":     "✅ Semua (kecuali Normal)"
        }[x],
        index=0
    )

    st.markdown("**Skor Sinyal Minimum**")
    min_skor = st.slider("", 1, 10, 5, label_visibility="collapsed")
    st.caption(f"Hanya tampilkan skor ≥ {min_skor}")

    st.markdown("**Market Cap (Triliun Rp)**")
    mc_range = st.slider("", 0, 1500, (0, 1500), step=10, label_visibility="collapsed")
    min_mc, max_mc = mc_range
    st.caption(f"Rp {min_mc}T – {'Semua' if max_mc >= 1500 else str(max_mc)+'T'}")

    st.markdown("---")
    st.markdown("**Parameter Intensity**")
    spike_mult = st.number_input("Spike Multiplier", 1.0, 5.0, 2.0, 0.1)
    early_mult = st.number_input("Early Multiplier",  1.0, 3.0, 1.3, 0.1)
    ma_len_inp = st.number_input("Intensity MA Length", 5, 50, 20, 1)

    st.markdown("---")
    scan_btn = st.button("🔍  Scan Sekarang", type="primary", use_container_width=True)

# ── FUNGSI KALKULASI ─────────────────────────────────────
def calc_fase(ticker, spike_m, early_m, ma_l):
    try:
        df = yf.download(ticker, period="6mo", interval="1d",
                         progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty or len(df) < MA50 + 5:
            return None

        df = df.copy()
        df["hl"]        = df["High"] - df["Low"]
        df["intensity"] = df.apply(
            lambda r: r["Volume"] / r["hl"] if r["hl"] > 0 else 0, axis=1)
        df["int_ma"]    = df["intensity"].rolling(ma_l).mean()
        df["ma50"]      = df["Close"].rolling(MA50).mean()

        last         = df.iloc[-1]
        int_spike    = bool(last["intensity"] > last["int_ma"] * spike_m)
        int_early    = bool(not int_spike and last["intensity"] > last["int_ma"] * early_m)
        price_above  = bool(last["Close"] > last["ma50"])
        price_rising = bool(last["Close"] > df["Close"].iloc[-6])
        ratio        = float(last["intensity"] / last["int_ma"]) if last["int_ma"] > 0 else 0

        if   int_spike and not price_above:  fase = "SMART MONEY"
        elif int_spike and price_above:      fase = "WASPADA"
        elif int_early and not price_above:  fase = "SM AWAL"
        elif int_early and price_above:      fase = "WSP AWAL"
        elif not int_spike and not int_early and price_rising: fase = "MARKUP"
        else:                                fase = "NORMAL"

        ratio_pts = min(6.0, ratio * 1.5)
        mom       = abs(float(last["Close"]) - float(df["Close"].iloc[-6])) / float(df["Close"].iloc[-6]) * 100
        score     = 0 if fase == "NORMAL" else round(max(1, min(10, ratio_pts + min(2.0, mom / 2))))

        return {
            "fase": fase, "score": score,
            "price": round(float(last["Close"])),
            "ratio": round(ratio, 2),
            "change": round((float(last["Close"]) - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100, 2)
        }
    except Exception as e:
        return None

def fase_match(fase, f):
    if f == "sm":      return fase == "SMART MONEY"
    if f == "sm_awal": return fase in ("SMART MONEY", "SM AWAL")
    if f == "markup":  return fase in ("SMART MONEY", "SM AWAL", "MARKUP")
    return fase != "NORMAL"

def fase_emoji(fase):
    return {"SMART MONEY":"🔵","SM AWAL":"🩵","WASPADA":"🔴",
            "WSP AWAL":"🩷","MARKUP":"🟣","NORMAL":"⚪"}.get(fase,"⚪")

# ── SCAN ─────────────────────────────────────────────────
if scan_btn:
    candidates = [s for s in STOCKS
                  if min_mc <= s["mc"] <= (9999 if max_mc >= 1500 else max_mc)]

    col1, col2 = st.columns([3, 1])
    with col1:
        prog_bar = st.progress(0)
        prog_txt = st.empty()

    results = []
    t_start = time.time()

    for i, s in enumerate(candidates):
        prog_txt.markdown(f"<small style='color:#8B949E'>Menganalisis **{s['n']}** ({i+1}/{len(candidates)})</small>",
                          unsafe_allow_html=True)
        prog_bar.progress((i + 1) / len(candidates))

        res = calc_fase(s["t"], spike_mult, early_mult, ma_len_inp)
        if res and fase_match(res["fase"], fase_opt) and res["score"] >= min_skor:
            results.append({
                "Saham"   : s["n"],
                "Fase"    : f"{fase_emoji(res['fase'])} {res['fase']}",
                "Harga"   : res["price"],
                "Change%" : res["change"],
                "Rasio"   : res["ratio"],
                "Skor"    : res["score"],
                "Mkt Cap" : f"{s['mc']}T",
            })
        time.sleep(0.25)

    prog_bar.empty()
    prog_txt.empty()

    elapsed = round(time.time() - t_start, 1)

    # metric cards
    total_sm  = sum(1 for r in results if "SMART MONEY" in r["Fase"] and "AWAL" not in r["Fase"])
    total_awal = sum(1 for r in results if "AWAL" in r["Fase"])
    total_mk  = sum(1 for r in results if "MARKUP" in r["Fase"])

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="val">{len(results)}</div><div class="lbl">Total ditemukan</div></div>
        <div class="metric-card"><div class="val" style="color:#64B5F6">{total_sm}</div><div class="lbl">Smart Money</div></div>
        <div class="metric-card"><div class="val" style="color:#42A5F5">{total_awal}</div><div class="lbl">SM / WSP Awal</div></div>
        <div class="metric-card"><div class="val" style="color:#CE93D8">{total_mk}</div><div class="lbl">Markup</div></div>
        <div class="metric-card"><div class="val" style="color:#8B949E">{elapsed}s</div><div class="lbl">Waktu scan</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"Scan selesai: {datetime.now().strftime('%d %b %Y %H:%M')} WIB  |  {len(candidates)} saham dianalisis")

    if not results:
        st.warning("Tidak ada saham yang terdeteksi. Coba turunkan filter skor atau ubah pilihan fase.")
    else:
        df_out = pd.DataFrame(results).sort_values(["Skor","Rasio"], ascending=False)

        st.dataframe(
            df_out,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Saham"   : st.column_config.TextColumn("Saham", width=90),
                "Fase"    : st.column_config.TextColumn("Fase", width=160),
                "Harga"   : st.column_config.NumberColumn("Harga", format="%d"),
                "Change%" : st.column_config.NumberColumn("Change%", format="%.2f%%"),
                "Rasio"   : st.column_config.ProgressColumn("Rasio", min_value=0, max_value=5, format="%.2fx"),
                "Skor"    : st.column_config.NumberColumn("Skor /10", format="%d"),
                "Mkt Cap" : st.column_config.TextColumn("Mkt Cap", width=80),
            }
        )

        csv = df_out.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️  Download CSV",
            data=csv,
            file_name=f"sm_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

else:
    st.info("👈 Atur filter di sidebar, lalu tekan **Scan Sekarang**.")
    with st.expander("ℹ️ Panduan penggunaan"):
        st.markdown("""
**Fase yang dideteksi:**
| Fase | Kondisi | Artinya |
|---|---|---|
| 🔵 Smart Money | Volume spike + harga di bawah MA50 | Akumulasi terkonfirmasi |
| 🩵 SM Awal | Volume early warning + harga di bawah MA50 | Peringatan dini akumulasi |
| 🔴 Waspada | Volume spike + harga di atas MA50 | Distribusi terkonfirmasi |
| 🩷 WSP Awal | Volume early warning + harga di atas MA50 | Peringatan dini distribusi |
| 🟣 Markup | Harga naik + intensity rendah | Supply locked, tren bersih |

**Skor 1–10:** Makin tinggi makin kuat sinyalnya. Rekomendasi: gunakan skor ≥ 7.

**Rasio:** Intensity saat ini dibanding rata-rata. Di atas 2.0x = spike terkonfirmasi.

⚠️ Data delay ±15 menit dari Yahoo Finance. Bukan rekomendasi beli/jual.
        """)
