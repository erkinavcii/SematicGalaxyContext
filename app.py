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
    tag_str = str(tag_input)
    if not tag_input or tag_str.strip() == "" or tag_str.lower() == "nan":
        return "genel"
    
    tags = [t.strip().lower() for t in tag_str.split(',')]
    tags = sorted(list(set(tags)))
    return ", ".join(tags)

def get_unique_tags(dataframe):
    """Dataframe içindeki tüm benzersiz etiketleri listeler (Sidebar için)."""
    all_tags = set()
    if not dataframe.empty:
        for tags in dataframe['Tags'].fillna("").astype(str):
            # "ai, robot, tool" -> ["ai", "robot", "tool"]
            splitted = [t.strip() for t in tags.split(',')]
            all_tags.update(splitted)
    # Boş string varsa temizle ve sırala
    if "" in all_tags: all_tags.remove("")
    return sorted(list(all_tags))

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

# --- 4. VEKTÖR HESAPLAMA ---
def process_embeddings(dataframe):
    dataframe['Aciklama'] = dataframe['Aciklama'].fillna('')
    dataframe['Tags'] = dataframe['Tags'].fillna('')
    
    combined_text = dataframe['Aciklama'] + ". " + dataframe['Tags']
    embeddings = model.encode(combined_text.tolist())
    
    n_neighbors = min(15, len(dataframe) - 1) 
    if n_neighbors < 2: n_neighbors = 2
    
    umap_3d = UMAP(n_components=3, init='random', random_state=42, n_neighbors=n_neighbors)
    projections = umap_3d.fit_transform(embeddings)
    
    dataframe['x'] = projections[:, 0]
    dataframe['y'] = projections[:, 1]
    dataframe['z'] = projections[:, 2]
    return dataframe, embeddings

if not df.empty:
    df, embeddings = process_embeddings(df)
else:
    embeddings = np.array([])

# --- ARAYÜZ ---
st.title("🧠 My Semantic Brain")

# --- SIDEBAR (VERİ EKLEME & FİLTRELEME) ---
with st.sidebar:
    # --- BÖLÜM 1: FİLTRELEME (YENİ) ---
    st.header("🏷️ Filtrele")
    unique_tags_list = get_unique_tags(df)
    selected_tags = st.multiselect(
        "Etiket Seç (Hybrid Search)", 
        unique_tags_list,
        placeholder="Tümünü Göster"
    )
    
    st.divider() # Çizgi çek

    # --- BÖLÜM 2: EKLEME ---
    st.header("➕ Yeni İçerik Ekle")
    new_title = st.text_input("Başlık")
    new_link = st.text_input("Link")
    new_desc = st.text_area("Açıklama")
    raw_tags = st.text_input("Etiketler (ai, ses)")
    
    if st.button("Kaydet"):
        if new_title and new_desc: 
            final_tags = clean_tags(raw_tags)
            new_data = pd.DataFrame({
                "Baslik": [new_title], "Link": [new_link], 
                "Aciklama": [new_desc], "Tags": [final_tags]
            })
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success(f"Eklendi!")
            st.rerun() 
        else:
            st.warning("Başlık ve Açıklama zorunludur!")

# --- ANA FİLTRELEME MANTIĞI (GLOBAL) ---
# Burası uygulamanın kalbi. Arama veya Galaksi sekmelerine gitmeden önce
# veriyi burada daraltıyoruz.
filtered_df = df.copy()

# Eğer etiket seçildiyse DataFrame'i daralt
if selected_tags:
    # KRİTİK DÜZELTME: Artık hem "ai, robot" hem "ai,robot" formatları destekleniyor.
    # split(',') ile ayırıp strip() ile boşlukları temizliyoruz.
    mask = filtered_df['Tags'].apply(
        lambda row_tags: any(
            tag in [t.strip() for t in str(row_tags).split(',')] 
            for tag in selected_tags
        )
    )
    filtered_df = filtered_df[mask]

# --- ANA EKRAN SEKMELERİ ---
tab1, tab2, tab3 = st.tabs(["🔍 Liste & Arama", "🌌 Semantik Galaksi", "🛠️ Veri Yönetimi"])

# --- TAB 1: HİBRİT ARAMA ---
with tab1:
    search_query = st.text_input("Akıllı Arama (Örn: 'Ses yapan robotlar')", "")
    
    if not filtered_df.empty:
        display_df = filtered_df.copy() # Filtrelenmiş veri üzerinde çalışacağız

        if search_query:
            # 1. Önce tüm (orijinal) veri için skorları hesapla
            # (Çünkü embeddings tüm veri için var, indexler kaymasın)
            query_vec = model.encode([search_query])
            full_sim_scores = np.dot(embeddings, query_vec.T).flatten()
            
            # 2. Skorları orijinal df'ye ekle
            df['Benzerlik'] = full_sim_scores
            
            # 3. Sonra filtrelenmiş df'ye bu skorları map et (Merge/Join yerine loc ile alıyoruz)
            display_df['Benzerlik'] = df.loc[display_df.index, 'Benzerlik']
            
            # 4. Sırala
            display_df = display_df.sort_values(by='Benzerlik', ascending=False)
            st.write(f"**'{search_query}'** için sonuçlar ({len(display_df)} kayıt):")
        else:
            # Arama yoksa ama filtre varsa
            if selected_tags:
                st.write(f"🏷️ **Seçili etiketlere göre** sonuçlar ({len(display_df)} kayıt):")
            else:
                st.write("Tüm kayıtlar:")

        # SONUÇLARI GÖSTER (ORTAK ALAN)
        results = display_df.head(10) # Sayfada çok yığılma olmasın diye 10 tane
        
        if not results.empty:
            # Progress Bar Normalizasyonu
            if 'Benzerlik' in results.columns:
                min_score = results['Benzerlik'].min()
                max_score = results['Benzerlik'].max()
                denominator = max_score - min_score

            for index, row in results.iterrows():
                # Skor barı sadece arama yapıldıysa anlamlıdır
                if search_query and 'Benzerlik' in row:
                    score = row['Benzerlik']
                    if denominator == 0: normalized = score 
                    else: normalized = (score - min_score) / denominator
                    safe_progress = max(0.0, min(1.0, float(normalized)))
                    st.progress(safe_progress)
                    score_text = f"(Skor: {score:.2f})"
                else:
                    score_text = ""

                st.info(f"**{row['Baslik']}** {score_text} | 🏷️ {row['Tags']}\n\n{row['Aciklama']}\n\n[🔗 Git]({row['Link']})")
        else:
            st.warning("Bu kriterlere uygun sonuç bulunamadı.")
            
    else:
        st.write("Veri yok veya filtreleme sonucu boş.")

# --- TAB 2: GÖRSELLEŞTİRME ---
with tab2:
    if not filtered_df.empty:
        # Mesajı duruma göre değiştir
        if selected_tags:
            st.write(f"🌌 Galaksi şu an **{', '.join(selected_tags)}** etiketlerine odaklandı.")
        else:
            st.write("🌌 Benzer açıklamalar ve **benzer tagler** birbirini çeker.")
            
        fig = px.scatter_3d(
            filtered_df, # DİKKAT: Artık filtrelenmiş datayı çiziyoruz!
            x='x', y='y', z='z',
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
        st.write("Gösterilecek veri yok.")

# --- TAB 3: VERİ YÖNETİMİ ---
with tab3:
    st.header("Veri Tabanını Düzenle")
    st.warning("⚠️ Dikkat: Burada yaptığınız değişiklikler 'Değişiklikleri Kaydet' butonuna basınca kalıcı olur.")
    
    if not df.empty:
        edited_df = st.data_editor(
            df[['Baslik', 'Link', 'Aciklama', 'Tags']], 
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor"
        )
        
        if st.button("💾 Değişiklikleri Kaydet"):
            edited_df = edited_df.reset_index(drop=True)
            
            # Validation
            has_empty_title = edited_df['Baslik'].isnull().any() or (edited_df['Baslik'].astype(str).str.strip() == '').any()
            has_empty_desc = edited_df['Aciklama'].isnull().any() or (edited_df['Aciklama'].astype(str).str.strip() == '').any()

            if has_empty_title or has_empty_desc:
                st.error("❌ Hata: 'Baslik' veya 'Aciklama' alanları boş bırakılamaz!")
            else:
                # Normalizasyon
                edited_df['Tags'] = edited_df['Tags'].fillna("").astype(str).apply(clean_tags)
                
                # Kayıt
                edited_df.to_csv(DATA_FILE, index=False)
                st.success("✅ Veri tabanı güncellendi!")
                st.rerun()
    else:
        st.write("Düzenlenecek veri yok.")