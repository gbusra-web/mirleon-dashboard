import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. EKRAN AYARLARI VE SIFIR BOŞLUK (No-Scroll Mimarisi)
st.set_page_config(page_title="Mirleon AI - dashboard", layout="wide", initial_sidebar_state="collapsed")

# Sihirli CSS: Arka planı koyu yapar, Streamlit'in varsayılan boşluklarını tıraşlar, Neon Kartlar ekler.
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 98%; }
        header {visibility: hidden;} footer {visibility: hidden;}
        .kpi-card { border-radius: 15px; padding: 15px 20px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2); height: 100%; }
        .purple-gradient { background: linear-gradient(135deg, #c471ed, #f64f59); }
        .cyan-gradient { background: linear-gradient(135deg, #059ce3, #18e6e8); }
        .green-gradient { background: linear-gradient(135deg, #28c76f, #71dd37); }
        .dark-card { background-color: #222232; border: 1px solid #383a59; }
        .kpi-title { font-size: 14px; opacity: 0.8; margin-bottom: 5px; }
        .kpi-value { font-size: 28px; font-weight: bold; margin: 0; }
        .kpi-delta { font-size: 12px; margin-top: 5px; opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

dark_template = {
    "layout": go.Layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a1acb8", family="Arial"),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=True, gridcolor="#2a2a3e", gridwidth=1),
        yaxis=dict(showgrid=True, gridcolor="#2a2a3e", gridwidth=1)
    )
}

# Veri
ana_gunler = [str(i) for i in range(1, 31)]
ana_gercek = [60, 63, 61, 60, 58, 60, 61, 61, 61, 62, 60, 60, 62, 59, 63, 60, 60, 63, 60, 63, 59, 62, 60, 64, 61, 62, 60, 59, 61, 61]
ana_hedef = [75, 79, 76, 74, 72, 76, 76, 75, 77, 77, 75, 75, 78, 74, 79, 75, 76, 78, 74, 79, 74, 78, 75, 80, 78, 78, 75, 73, 76, 76]

# Üretim & Fire verileri
uretim_ton = 7352.30
fire_ton = 11.70
fire_urunler = {"ML 150-50": 4.50, "ML 100-40": 3.20, "PL 80-30": 2.10, "Diğer": 1.90}
en_riskli = max(fire_urunler, key=fire_urunler.get)

# Kar Marjı
kar_marji = 57.2

# --- ÜST KATMAN ---
c1, c2, c3 = st.columns([1, 1, 1])
with c1: st.markdown("<div class='kpi-card purple-gradient'><div class='kpi-title'>Toplam Gelir</div><div class='kpi-value'>76.8M ₺</div></div>", unsafe_allow_html=True)
with c2: st.markdown("<div class='kpi-card cyan-gradient'><div class='kpi-title'>Toplam Gider</div><div class='kpi-value'>32.8M ₺</div></div>", unsafe_allow_html=True)
with c3: st.markdown("<div class='kpi-card green-gradient'><div class='kpi-title'>Net Kar</div><div class='kpi-value'>43.9M ₺</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ORTA KATMAN ---
row2_c1, row2_c2 = st.columns([7, 3])

with row2_c1:
    head_col, legend_col, filter_col = st.columns([2, 1.5, 1.2])
    with head_col: st.markdown("<h4 style='color:white; margin:0;'>Üretim Performansı</h4>", unsafe_allow_html=True)
    with legend_col:
        st.markdown("<div style='display:flex; gap:20px; align-items:center; margin-top:5px;'><div style='display:flex; align-items:center;'><div style='width:25px; height:3px; background:#059ce3; margin-right:8px;'></div><span style='font-size:14px; color:#a1acb8;'>Gerçekleşen</span></div><div style='display:flex; align-items:center;'><div style='width:25px; height:3px; background:#c471ed; margin-right:8px;'></div><span style='font-size:14px; color:#a1acb8;'>Hedeflenen</span></div></div>", unsafe_allow_html=True)
    with filter_col:
        zaman_secim = st.selectbox("Görünüm:", ["1 Ay", "3 Hafta", "2 Hafta", "1 Hafta"], label_visibility="collapsed")
        limit = {"1 Ay": 30, "3 Hafta": 21, "2 Hafta": 14, "1 Hafta": 7}[zaman_secim]

    fig_wave = go.Figure()
    fig_wave.add_trace(go.Scatter(x=ana_gunler[:limit], y=ana_gercek[:limit], mode='lines', fill='tozeroy', line=dict(color='#059ce3', width=3, shape='spline')))
    fig_wave.add_trace(go.Scatter(x=ana_gunler[:limit], y=ana_hedef[:limit], mode='lines', fill='tozeroy', line=dict(color='#c471ed', width=3, shape='spline')))
    fig_wave.update_layout(height=300, template=dark_template, showlegend=False, margin=dict(t=15, b=10, l=10, r=10))
    st.plotly_chart(fig_wave, use_container_width=True, config={'displayModeBar': False})

with row2_c2:
    # Varsayılan: hiçbir bilgi seçili değil (popover ilk açıldığında boş görünür)
    if "fire_view" not in st.session_state:
        st.session_state.fire_view = None

    # Başlık tek satırda (alta kaymaz), 3 nokta butonu başlığın hemen yanında
    h_col, dot_col = st.columns([3, 1])
    with h_col:
        st.markdown("<h4 style='color:white; margin-top:0px; text-align:right; white-space:nowrap;'>Üretim & Fire</h4>", unsafe_allow_html=True)
    with dot_col:
        def _toggle_view(secim):
            st.session_state.fire_view = None if st.session_state.fire_view == secim else secim

        with st.popover("⋮"):
            st.button("Tonaj", key="btn_tonaj", use_container_width=True,
                      on_click=_toggle_view, args=("Tonaj",))
            # Tonaj bilgisi kendi butonunun HEMEN ALTINDA görünür
            if st.session_state.fire_view == "Tonaj":
                st.markdown(f"<div style='font-size:14px; margin:4px 0 10px 0;'><span style='color:#00ff33;'>ÜRETİM: {uretim_ton:,.2f} TON</span><br><span style='color:#ea0707;'>FİRE: {fire_ton:,.2f} TON</span></div>", unsafe_allow_html=True)

            st.button("Risk", key="btn_risk", use_container_width=True,
                      on_click=_toggle_view, args=("Risk",))
            # Risk bilgisi kendi butonunun HEMEN ALTINDA görünür
            if st.session_state.fire_view == "Risk":
                st.markdown(f"<div style='font-size:14px; margin:4px 0 10px 0; color:#a1acb8;'>En Çok Fire Verilen Ürün<br><b style='color:#00d2ff; font-size:16px;'>{en_riskli}</b><br><span style='color:white;'>{fire_urunler[en_riskli]:.2f} TON</span></div>", unsafe_allow_html=True)

    # ANA EKRAN GRAFİĞİ — her zaman sabit, butonlarla değişmez
    fig_fire = go.Figure(data=[go.Pie(labels=['Fire', 'Üretim'], values=[0.2, 99.8], hole=0.85,
                                      marker=dict(colors=["#ea0707", "#00ff33"], line=dict(width=0)), textinfo='none')])
    fig_fire.update_layout(height=230, template=dark_template, showlegend=False,
                           margin=dict(t=5, b=5, l=10, r=10),
                           annotations=[dict(text="<b>%0.2</b>", font_size=28, font_color="white", showarrow=False)])
    st.plotly_chart(fig_fire, use_container_width=True, config={'displayModeBar': False})

# --- ALT KATMAN (Kar Marjı daire grafiği ortada) ---
row3_c1, row3_c2, row3_c3 = st.columns([1.5, 1, 1.5])

with row3_c1:
    st.markdown("<h4 style='color:white; margin-top:0px;'>Maliyet Dağılımı <span style='font-size:14px; color:#a1acb8; font-weight:normal;'>| Giderin Kaynağı (%)</span></h4>", unsafe_allow_html=True)
    maliyet_renkleri = ['#c471ed', '#a86df0', '#8c69f2', '#f64f59', '#e85b8a']
    fig_m = go.Figure(data=[go.Bar(x=['Hammadde', 'Bağlayıcı', 'Nakliye', 'Ambalaj', 'Enerji'], 
                                   y=[12376181, 6761877, 5533748, 4469858, 3720502], 
                                   marker_color=maliyet_renkleri, 
                                   text=[38, 21, 17, 14, 11], 
                                   textposition='auto')])
    fig_m.update_layout(height=240, template=dark_template, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_m, use_container_width=True, config={'displayModeBar': False})

with row3_c2:
    st.markdown("<h4 style='color:white; margin-top:0px; text-align:center;'>Kar Marjı</h4>", unsafe_allow_html=True)
    fig_kar = go.Figure(data=[go.Pie(labels=['Kar', 'Maliyet'], values=[kar_marji, 100 - kar_marji], hole=0.8,
                                     marker=dict(colors=["#03c3ec", "#2a2a3e"], line=dict(width=0)),
                                     textinfo='none', sort=False, direction='clockwise')])
    fig_kar.update_layout(height=240, template=dark_template, showlegend=False,
                          margin=dict(t=10, b=10, l=10, r=10),
                          annotations=[dict(text=f"<b>%{kar_marji}</b>", font_size=28, font_color="#03c3ec", showarrow=False)])
    st.plotly_chart(fig_kar, use_container_width=True, config={'displayModeBar': False})

with row3_c3:
    st.markdown("<h4 style='color:white; margin-top:0px;'>En İyi 6 Müşteri (M₺)<span style='font-size:14px; color:#a1acb8; font-weight:normal;'></span></h4>", unsafe_allow_html=True)
    musteri_renkleri = ['#0a6ebd', '#0784d0', '#059ce3', '#10b5e6', '#18cfe8', '#18e6e8']
    fig_mu = go.Figure(data=[go.Bar(y=[ 'İpektaş', 'KC', 'Kaizen', 'Vista', 'Grande','Özyangıncı'], x=[3.5, 4.1, 4.4, 4.4, 4.5, 5.1],
                                    orientation='h', marker_color=musteri_renkleri, text=[ 3.5, 4.1, 4.4, 4.4, 4.5, 5.1], textposition='auto')])
    fig_mu.update_layout(height=300, template=dark_template, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_mu, use_container_width=True, config={'displayModeBar': False})
