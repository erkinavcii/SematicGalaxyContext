import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import plotly.express as px
from umap import UMAP
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="My Semantic Brain", layout="wide")

# --- 1. MODELİ YÜKLE (ÖNBELLEĞE ALALIM Kİ HIZLI OLSUN) ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# --- 2. VERİ YÖNETİMİ ---
DATA_FILE = "data.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        # Eğer dosya yoksa örnek veriyle oluşturalım
        data = {
            "Baslik": [
                "ElevenLabs", "Midjourney", "Notion AI", "ChatGPT", "Descript", 
                "TensorFlow", "PyTorch", "Unity", "Unreal Engine", "Blender"
            ],
            "Link": ["https://elevenlabs.io", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
            "Aciklama": [
                "Yapay zeka ile ses kopyalama ve metinden ses üretme aracı.",
                "Metinden görsel oluşturan yapay zeka sanat aracı.",
                "Not alma uygulaması içinde yapay zeka asistanı, özet çıkarma.",
                "Her türlü konuda sohbet edebilen, kod yazan yapay zeka asistanı.",
                "Ses ve video düzenleme, transkript çıkarma, ses iyileştirme.",
                "Google tarafından geliştirilen açık kaynaklı makine öğrenmesi kütüphanesi.",
                "Facebook tarafından geliştirilen derin öğrenme kütüphanesi.",
                "Oyun geliştirme motoru, 3D ve 2D oyunlar için.",
                "Yüksek grafikli oyunlar ve simülasyonlar için oyun motoru.",
                "3 boyutlu modelleme, animasyon ve render programı."
            ],
            "Tags": ["AI, Ses", "AI, Görsel", "AI, Ofis", "AI, Chat", "AI, Video", "Kod, ML", "Kod, DL", "Oyun, 3D", "Oyun, 3D", "Tasarım, 3D"]
        }
        df = pd.DataFrame(data)
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

df = load_data()

# --- 3. VEKTÖR HESAPLAMA VE 3D KOORDİNATLAR ---
def process_embeddings(dataframe):
    # Açıklamaları vektöre çevir
    embeddings = model.encode(dataframe['Aciklama'].tolist())
    
    # Boyut İndirgeme (384 Boyuttan -> 3 Boyuta)
    # Veri azsa hata vermemesi için n_neighbors ayarı
    n_neighbors = min(15, len(dataframe) - 1) 
    if n_neighbors < 2: n_neighbors = 2
    
    umap_3d = UMAP(n_components=3, init='random', random_state=42, n_neighbors=n_neighbors)
    projections = umap_3d.fit_transform(embeddings)
    
    dataframe['x'] = projections[:, 0]
    dataframe['y'] = projections[:, 1]
    dataframe['z'] = projections[:, 2]
    return dataframe, embeddings

df, embeddings = process_embeddings(df)

# --- ARAYÜZ ---
st.title("🧠 My Semantic Brain")

# Yan Panel: Yeni Veri Ekleme
with st.sidebar:
    st.header("Yeni İçerik Ekle")
    new_title = st.text_input("Başlık")
    new_link = st.text_input("Link")
    new_desc = st.text_area("Açıklama (Detaylı yaz!)")
    new_tags = st.text_input("Etiketler")
    
    if st.button("Kaydet"):
        new_data = pd.DataFrame({
            "Baslik": [new_title], "Link": [new_link], 
            "Aciklama": [new_desc], "Tags": [new_tags]
        })
        # CSV'ye ekle
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Eklendi! Listeyi güncellemek için sayfayı yenile (F5).")

# Ana Ekran: Sekmeler
tab1, tab2 = st.tabs(["🔍 Semantik Arama & Liste", "🌌 3D Uzay (Galaksi)"])

with tab1:
    search_query = st.text_input("Ne arıyorsun? (Örn: 'Müzik yapan programlar')", "")
    
    if search_query:
        # --- HİBRİT ARAMA MOTORU ---
        # 1. Sorguyu vektöre çevir
        query_vec = model.encode([search_query])
        
        # 2. Benzerlik hesapla (Cosine Similarity)
        # Basit matris çarpımı ile benzerlik skoru
        sim_scores = np.dot(embeddings, query_vec.T).flatten()
        
        # 3. Skorları dataframe'e ekle ve sırala
        df['Benzerlik'] = sim_scores
        results = df.sort_values(by='Benzerlik', ascending=False)
        
        st.write(f"**'{search_query}'** için sonuçlar:")
        # En alakalı 5 sonucu göster
        for index, row in results.head(5).iterrows():
            score = row['Benzerlik']
            st.info(f"**{row['Baslik']}** (Skor: {score:.2f})\n\n{row['Aciklama']}\n\n[Linke Git]({row['Link']})")
    else:
        st.dataframe(df[['Baslik', 'Tags', 'Aciklama', 'Link']])

with tab2:
    st.write("Benzer konular birbirine daha yakın konumlanmıştır.")
    fig = px.scatter_3d(
        df, x='x', y='y', z='z',
        color='Tags', 
        hover_name='Baslik',
        hover_data={'Aciklama': True, 'Link': True, 'x': False, 'y': False, 'z': False},
        title="İçerik Uzayı"
    )
    st.plotly_chart(fig, use_container_width=True)