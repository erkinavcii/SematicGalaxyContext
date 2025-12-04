import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import plotly.express as px
from umap import UMAP
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="My Semantic Brain", layout="wide")

# --- 1. MODELİ YÜKLE ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# --- 2. YARDIMCI FONKSİYONLAR ---
def clean_tags(tag_input):
    """Tagleri temizler, sıralar ve duplicate'leri uçurur."""
    if not tag_input or tag_input.strip() == "":
        return "genel"
    # Virgülle ayır, boşlukları sil, küçük harfe çevir
    tags = [t.strip().lower() for t in tag_input.split(',')]
    # Set ile tekrarları kaldır, sonra alfabetik sırala
    tags = sorted(list(set(tags)))
    # Tekrar string yap
    return ", ".join(tags)

# --- 3. VERİ YÖNETİMİ ---
DATA_FILE = "data.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        # Örnek veri seti
        data = {
            "Baslik": ["ElevenLabs", "Midjourney", "Notion AI", "ChatGPT", "Blender"],
            "Link": ["https://elevenlabs.io", "#", "#", "#", "#"],
            "Aciklama": [
                "Yapay zeka ile ses kopyalama ve metinden ses üretme aracı.",
                "Metinden görsel oluşturan yapay zeka sanat aracı.",
                "Not alma uygulaması içinde yapay zeka asistanı.",
                "Sohbet edebilen, kod yazan yapay zeka asistanı.",
                "3 boyutlu modelleme ve animasyon programı."
            ],
            "Tags": ["ai, ses, tool", "ai, görsel, sanat", "ai, ofis, not", "ai, chat, bot", "tasarım, 3d, modelleme"]
        }
        df = pd.DataFrame(data)
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

df = load_data()

# --- 4. VEKTÖR HESAPLAMA (TAGLER DAHİL!) ---
def process_embeddings(dataframe):
    # BURASI KRİTİK: Açıklama + Tagleri birleştiriyoruz.
    # Böylece Tagler de konuma (x, y, z) etki ediyor.
    combined_text = dataframe['Aciklama'] + ". " + dataframe['Tags']
    
    embeddings = model.encode(combined_text.tolist())
    
    # UMAP Ayarları
    n_neighbors = min(15, len(dataframe) - 1) 
    if n_neighbors < 2: n_neighbors = 2
    
    umap_3d = UMAP(n_components=3, init='random', random_state=42, n_neighbors=n_neighbors)
    projections = umap_3d.fit_transform(embeddings)
    
    dataframe['x'] = projections[:, 0]
    dataframe['y'] = projections[:, 1]
    dataframe['z'] = projections[:, 2]
    return dataframe, embeddings

# Veri varsa işle, yoksa boş geç
if not df.empty:
    df, embeddings = process_embeddings(df)
else:
    embeddings = np.array([])

# --- ARAYÜZ ---
st.title("🧠 My Semantic Brain")

# --- SIDEBAR (VERİ EKLEME) ---
with st.sidebar:
    st.header("Yeni İçerik Ekle")
    new_title = st.text_input("Başlık")
    new_link = st.text_input("Link")
    new_desc = st.text_area("Açıklama (Ne kadar detay, o kadar iyi konum)")
    raw_tags = st.text_input("Etiketler (Virgülle ayır: ai, ses, tool)")
    
    if st.button("Kaydet"):
        if new_title and new_desc: # Boş kaydetmeyi engelle
            # 1. Tagleri temizle
            final_tags = clean_tags(raw_tags)
            
            # 2. DataFrame oluştur
            new_data = pd.DataFrame({
                "Baslik": [new_title], "Link": [new_link], 
                "Aciklama": [new_desc], "Tags": [final_tags]
            })
            
            # 3. Kaydet
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success(f"Eklendi! Tagler: {final_tags}")
            st.rerun() # Sayfayı yenile ki yeni veri haritaya düşsün
        else:
            st.warning("Başlık ve Açıklama zorunludur!")

# --- ANA EKRAN ---
tab1, tab2 = st.tabs(["🔍 Liste & Arama", "🌌 Semantik Galaksi"])

with tab1:
    search_query = st.text_input("Akıllı Arama (Örn: 'Ses yapan robotlar')", "")
    
    if search_query and not df.empty:
        # HİBRİT ARAMA (Sorguyu da vektöre çevirip kıyaslıyoruz)
        query_vec = model.encode([search_query])
        sim_scores = np.dot(embeddings, query_vec.T).flatten()
        
        df['Benzerlik'] = sim_scores
        results = df.sort_values(by='Benzerlik', ascending=False)
        
        st.write(f"**'{search_query}'** için sonuçlar:")
        for index, row in results.head(5).iterrows():
            score = row['Benzerlik']
            # Skor barı ekleyelim
            st.progress(float(score) if score > 0 else 0)
            st.info(f"**{row['Baslik']}** (Skor: {score:.2f}) | 🏷️ {row['Tags']}\n\n{row['Aciklama']}\n\n[🔗 Git]({row['Link']})")
    else:
        st.dataframe(df)

with tab2:
    if not df.empty:
        st.write("🌌 Benzer açıklamalar ve **benzer tagler** birbirini çeker.")
        
        # KOYU MOD GÖRSELLEŞTİRME
        fig = px.scatter_3d(
            df, x='x', y='y', z='z',
            color='Tags', 
            hover_name='Baslik',
            hover_data={'Aciklama': True, 'Link': True, 'Tags': True, 'x': False, 'y': False, 'z': False},
            template="plotly_dark",
            opacity=0.9,
            size_max=15
        )
        
        # Tamamen temiz, uzay görünümü
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=0, r=0, b=0, t=10),
            legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Henüz veri yok.")