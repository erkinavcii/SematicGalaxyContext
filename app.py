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
    # Gelen veri bazen float(nan) olabilir, stringe çevirip kontrol edelim
    tag_str = str(tag_input)
    if not tag_input or tag_str.strip() == "" or tag_str.lower() == "nan":
        return "genel"
    
    # Virgülle ayır, boşlukları sil, küçük harfe çevir
    tags = [t.strip().lower() for t in tag_str.split(',')]
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
    # NaN değerleri string ' ' ile doldurarak hata almayı önlüyoruz
    dataframe['Aciklama'] = dataframe['Aciklama'].fillna('')
    dataframe['Tags'] = dataframe['Tags'].fillna('')
    
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

# --- ANA EKRAN (GÜNCELLENDİ) ---
# Artık 3 sekmemiz var: Arama, Galaksi, Yönetim
tab1, tab2, tab3 = st.tabs(["🔍 Liste & Arama", "🌌 Semantik Galaksi", "🛠️ Veri Yönetimi"])

# --- TAB 1: ARAMA ---
with tab1:
    search_query = st.text_input("Akıllı Arama (Örn: 'Ses yapan robotlar')", "")
    
    if search_query and not df.empty:
        query_vec = model.encode([search_query])
        sim_scores = np.dot(embeddings, query_vec.T).flatten()
        
        df['Benzerlik'] = sim_scores
        results = df.sort_values(by='Benzerlik', ascending=False)
        display_results = results.head(5)

        st.write(f"**'{search_query}'** için sonuçlar:")
        
        if not display_results.empty:
            min_score = display_results['Benzerlik'].min()
            max_score = display_results['Benzerlik'].max()
            denominator = max_score - min_score

            for index, row in display_results.iterrows():
                score = row['Benzerlik']
                if denominator == 0:
                    normalized_score = score 
                else:
                    normalized_score = (score - min_score) / denominator
                
                safe_progress = max(0.0, min(1.0, float(normalized_score)))
                st.progress(safe_progress)
                st.info(f"**{row['Baslik']}** (Skor: {score:.2f}) | 🏷️ {row['Tags']}\n\n{row['Aciklama']}\n\n[🔗 Git]({row['Link']})")
    else:
        st.info("Arama yapmak için yukarıya bir şeyler yazın veya tüm listeyi aşağıda görün.")
        st.dataframe(df) # Varsayılan olarak tüm listeyi göster

# --- TAB 2: GÖRSELLEŞTİRME ---
with tab2:
    if not df.empty:
        st.write("🌌 Benzer açıklamalar ve **benzer tagler** birbirini çeker.")
        fig = px.scatter_3d(
            df, x='x', y='y', z='z',
            color='Tags', 
            hover_name='Baslik',
            hover_data={'Aciklama': True, 'Link': True, 'Tags': True, 'x': False, 'y': False, 'z': False},
            template="plotly_dark",
            opacity=0.9,
            size_max=15
        )
        fig.update_layout(
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=0, r=0, b=0, t=10),
            legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Henüz veri yok.")

# --- TAB 3: VERİ YÖNETİMİ (GÜNCELLENMİŞ & GÜVENLİ) ---
with tab3:
    st.header("Veri Tabanını Düzenle")
    st.warning("⚠️ Dikkat: Burada yaptığınız değişiklikler 'Değişiklikleri Kaydet' butonuna basınca kalıcı olur.")
    
    if not df.empty:
        # num_rows="dynamic" sayesinde satır ekleyip silebilirsin
        edited_df = st.data_editor(
            df[['Baslik', 'Link', 'Aciklama', 'Tags']], # x,y,z'yi göstermiyoruz, onları arkada biz hesaplıyoruz
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor"
        )
        
        if st.button("💾 Değişiklikleri Kaydet"):
            # 1. Index Reset
            edited_df = edited_df.reset_index(drop=True)
            
            # 2. BOŞ DEĞER KONTROLÜ (Validation)
            # Başlık veya Açıklama boşsa veya sadece boşluktan ibaretse hata ver
            # Pandas'ta string kolonlar bazen None, bazen NaN, bazen "" olabilir. Hepsini kapsayalım.
            has_empty_title = edited_df['Baslik'].isnull().any() or (edited_df['Baslik'].astype(str).str.strip() == '').any()
            has_empty_desc = edited_df['Aciklama'].isnull().any() or (edited_df['Aciklama'].astype(str).str.strip() == '').any()

            if has_empty_title or has_empty_desc:
                st.error("❌ Hata: 'Baslik' veya 'Aciklama' alanları boş bırakılamaz! Lütfen boş satırları silin veya doldurun.")
            else:
                # 3. TAG NORMALİZASYONU
                # Kullanıcı " AI , tool" yazmış olabilir, bunu "ai, tool" formatına çevirelim
                # fillna("") ile olası NaN hatalarını önlüyoruz
                edited_df['Tags'] = edited_df['Tags'].fillna("").astype(str).apply(clean_tags)
                
                # 4. KAYDET
                edited_df.to_csv(DATA_FILE, index=False)
                
                st.success("✅ Veri tabanı başarıyla güncellendi, etiketler düzenlendi! Uygulama yeniden başlatılıyor...")
                st.rerun()
    else:
        st.write("Düzenlenecek veri yok.")