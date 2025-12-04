import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import plotly.express as px
from umap import UMAP
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="My Semantic Brain", layout="wide")

# --- CUSTOM CSS (KART TASARIMI) ---
st.markdown("""
<style>
    .result-card {
        background-color: #262730;
        border: 1px solid #464b5c;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.5);
        border-color: #ff4b4b;
    }
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .favicon {
        width: 24px;
        height: 24px;
        margin-right: 10px;
        border-radius: 4px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ffffff;
        text-decoration: none;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .card-body {
        color: #c0c0c0;
        font-size: 0.9rem;
        margin-bottom: 15px;
        line-height: 1.5;
        flex-grow: 1;
    }
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 10px;
    }
    .tag-badge {
        background-color: #31333F;
        color: #ff4b4b;
        border: 1px solid #ff4b4b;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .progress-bg {
        width: 100%;
        background-color: #31333F;
        height: 6px;
        border-radius: 3px;
        margin-bottom: 15px;
    }
    .progress-fill {
        height: 100%;
        background-color: #4CAF50;
        border-radius: 3px;
        transition: width 0.5s ease-in-out;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #464b5c;
        padding-top: 10px;
        margin-top: auto;
    }
    .score-badge {
        font-size: 0.8rem;
        color: #4CAF50;
        font-weight: bold;
    }
    .visit-btn {
        background-color: #ff4b4b;
        color: white !important;
        padding: 6px 12px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
        transition: background 0.3s;
    }
    .visit-btn:hover {
        background-color: #ff2b2b;
    }
</style>
""", unsafe_allow_html=True)

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
    """Dataframe içindeki tüm benzersiz etiketleri listeler."""
    all_tags = set()
    if not dataframe.empty:
        for tags in dataframe['Tags'].fillna("").astype(str):
            splitted = [t.strip() for t in tags.split(',')]
            all_tags.update(splitted)
    if "" in all_tags: all_tags.remove("")
    return sorted(list(all_tags))

def load_stopwords():
    """stopwords.txt dosyasını yükler, yoksa default liste döner."""
    default_stops = {"ve", "ile", "bir", "bu", "için", "ama", "fakat", "o", "şu", "da", "de"}
    if os.path.exists("stopwords.txt"):
        try:
            with open("stopwords.txt", "r", encoding="utf-8") as f:
                file_stops = set(f.read().splitlines())
            return file_stops
        except:
            return default_stops
    return default_stops

# --- 3. VERİ YÖNETİMİ ---
DATA_FILE = "data.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "Baslik": ["ElevenLabs", "Midjourney", "Notion AI", "ChatGPT", "Blender"],
            "Link": ["https://elevenlabs.io", "https://midjourney.com", "https://notion.so", "https://chat.openai.com", "https://blender.org"],
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏷️ Filtrele")
    unique_tags_list = get_unique_tags(df)
    selected_tags = st.multiselect("Etiket Seç (Hybrid Search)", unique_tags_list, placeholder="Tümünü Göster")
    use_and_logic = st.checkbox("Sadece tüm etiketleri içerenleri getir (AND)", value=False)
    
    st.divider()

    st.header("➕ Yeni İçerik Ekle")

    # --- HATA DÜZELTME & FORM TEMİZLEME MANTIĞI ---
    if st.session_state.get("data_saved", False):
        st.session_state.new_title_input = ""
        st.session_state.new_link_input = ""
        st.session_state.new_desc_input = ""
        st.session_state.new_tags_input = ""
        st.session_state.data_saved = False 

    new_title = st.text_input("Başlık", key="new_title_input")
    new_link = st.text_input("Link", key="new_link_input")
    new_desc = st.text_area("Açıklama", key="new_desc_input")
    
    # --- AUTO-TAGGING ---
    if "new_tags_input" not in st.session_state:
        st.session_state.new_tags_input = ""

    if st.button("✨ Tag Öner"):
        if new_desc and not df.empty:
            all_existing_tags = get_unique_tags(df)
            if all_existing_tags:
                desc_vec = model.encode([new_desc])
                tags_vec = model.encode(all_existing_tags)
                sims = np.dot(tags_vec, desc_vec.T).flatten()
                
                top_indices = np.argsort(sims)[::-1][:5]
                suggested_tags = [all_existing_tags[i] for i in top_indices if sims[i] > 0.25]
                
                if suggested_tags:
                    result_str = ", ".join(suggested_tags)
                    st.session_state.new_tags_input = result_str
                    st.toast(f"Önerilen Etiketler: {result_str}", icon="🤖")
                else:
                    st.toast("Yeterince benzer bir etiket bulunamadı.", icon="🤷‍♂️")
            else:
                st.warning("Henüz hiç etiket yok.")
        elif not new_desc:
            st.warning("Lütfen önce bir açıklama yaz.")

    raw_tags = st.text_input("Etiketler (ai, ses)", key="new_tags_input")
    
    if st.button("Kaydet"):
        if new_title and new_desc: 
            final_tags = clean_tags(raw_tags)
            new_data = pd.DataFrame({
                "Baslik": [new_title], "Link": [new_link], 
                "Aciklama": [new_desc], "Tags": [final_tags]
            })
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            
            st.session_state.data_saved = True 
            
            st.success(f"Eklendi!")
            st.rerun() 
        else:
            st.warning("Başlık ve Açıklama zorunludur!")
    
    # --- YEDEKLEME (YENİ ÖZELLİK) ---
    st.divider()
    st.header("💾 Yedekleme")
    
    # 1. İndirme (Export)
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Veri Setini İndir (CSV)",
            data=csv,
            file_name='my_semantic_brain_backup.csv',
            mime='text/csv',
            help="Tüm veri tabanını bilgisayarına indir."
        )
    
    # 2. Yükleme (Import)
    uploaded_file = st.file_uploader("📤 Yedekten Yükle (CSV)", type="csv", help="Daha önce indirdiğin yedeği geri yükle.")
    
    if uploaded_file is not None:
        try:
            # CSV'yi oku
            uploaded_df = pd.read_csv(uploaded_file)
            
            # Kolon kontrolü (Veri bozulmasını önlemek için şart)
            required_cols = ["Baslik", "Link", "Aciklama", "Tags"]
            if all(col in uploaded_df.columns for col in required_cols):
                # Mevcut tagleri temizle ve kaydet
                uploaded_df['Tags'] = uploaded_df['Tags'].fillna("").astype(str).apply(clean_tags)
                uploaded_df.to_csv(DATA_FILE, index=False)
                
                st.success("✅ Yedek başarıyla yüklendi! Sayfa yenileniyor...")
                st.rerun()
            else:
                st.error(f"❌ Hatalı format! CSV dosyasında şu kolonlar olmalı: {', '.join(required_cols)}")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# --- ANA FİLTRELEME ---
filtered_df = df.copy()
if selected_tags:
    def check_tags(row_tags):
        row_tag_list = [t.strip() for t in str(row_tags).split(',')]
        if use_and_logic:
            return all(tag in row_tag_list for tag in selected_tags)
        else:
            return any(tag in row_tag_list for tag in selected_tags)
    mask = filtered_df['Tags'].apply(check_tags)
    filtered_df = filtered_df[mask]

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Liste & Arama", "🌌 Semantik Galaksi", "🛠️ Veri Yönetimi", "☁️ Analiz"])

with tab1:
    search_query = st.text_input("Akıllı Arama (Örn: 'Ses yapan robotlar')", "")
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        
        # Skorlama Mantığı
        if search_query:
            query_vec = model.encode([search_query])
            full_sim_scores = np.dot(embeddings, query_vec.T).flatten()
            df['Benzerlik'] = full_sim_scores
            display_df['Benzerlik'] = df.loc[display_df.index, 'Benzerlik']
            display_df = display_df.sort_values(by='Benzerlik', ascending=False)
            st.write(f"**'{search_query}'** için sonuçlar ({len(display_df)} kayıt):")
        else:
            label = "VE" if use_and_logic else "VEYA"
            msg = f"🏷️ **Seçili etiketlere ({label}) göre**" if selected_tags else "Tüm kayıtlar:"
            st.write(f"{msg} ({len(display_df)} kayıt)")

        results = display_df.head(20) # Daha çok sonuç gösterelim, kartlar şık duruyor
        
        if not results.empty:
            # Skor Normalizasyonu (Progress bar için)
            if 'Benzerlik' in results.columns and search_query:
                min_s, max_s = results['Benzerlik'].min(), results['Benzerlik'].max()
                denom = max_s - min_s
            
            # --- CARD UI LOOP ---
            # 2 Sütunlu Grid Oluşturuyoruz
            cols = st.columns(2)
            
            for index, row in results.iterrows():
                # Hangi kolona koyacağımızı seçiyoruz
                col = cols[index % 2]
                
                with col:
                    # 1. Skor Hesaplama
                    score_percent = 0
                    score_val = 0.0
                    if search_query and 'Benzerlik' in row:
                        score_val = row['Benzerlik']
                        norm = (score_val - min_s) / denom if denom != 0 else score_val
                        score_percent = max(0.0, min(1.0, float(norm))) * 100
                    
                    # 2. Tag HTML Hazırlama
                    tags_html = ""
                    if row['Tags']:
                        for t in str(row['Tags']).split(','):
                            tags_html += f'<span class="tag-badge">{t.strip()}</span>'

                    # 3. Favicon Linki
                    # Google'ın favicon servisini kullanıyoruz
                    link = row['Link']
                    favicon_url = f"https://www.google.com/s2/favicons?domain_url={link}&sz=64"
                    
                    # 4. HTML Kartı Render Et
                    # Not: f-string içinde süslü parantez kullanmak için {{ }} kullanılır.
                    st.markdown(f"""
                    <div class="result-card">
                        <div>
                            <div class="card-header">
                                <img src="{favicon_url}" class="favicon" onerror="this.style.display='none'">
                                <a href="{link}" target="_blank" class="card-title" title="{row['Baslik']}">{row['Baslik']}</a>
                            </div>
                            <div class="card-body">
                                {row['Aciklama']}
                            </div>
                        </div>
                        <div>
                            {f'''
                            <div class="progress-bg">
                                <div class="progress-fill" style="width: {score_percent}%;"></div>
                            </div>
                            ''' if search_query else ''}
                            
                            <div class="tag-container">
                                {tags_html}
                            </div>
                            
                            <div class="card-footer">
                                <span class="score-badge">{f'Skor: {score_val:.2f}' if search_query else ''}</span>
                                <a href="{link}" target="_blank" class="visit-btn">Siteye Git ➜</a>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Sonuç yok.")
    else:
        st.write("Veri yok.")

with tab2:
    if not filtered_df.empty:
        label = "VE" if use_and_logic else "VEYA"
        msg = f"🌌 Galaksi **{', '.join(selected_tags)}** ({label}) etiketlerine odaklandı." if selected_tags else "🌌 Galaksi Görünümü"
        st.write(msg)
        fig = px.scatter_3d(
            filtered_df, x='x', y='y', z='z', color='Tags', hover_name='Baslik',
            hover_data={'Aciklama': True, 'Link': True, 'Tags': True, 'x': False, 'y': False, 'z': False},
            template="plotly_dark", opacity=0.9, size_max=15
        )
        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='rgba(0,0,0,0)'), margin=dict(l=0,r=0,b=0,t=10), legend=dict(yanchor="top",y=0.9,xanchor="left",x=0.1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Veri yok.")

with tab3:
    st.header("Veri Tabanını Düzenle")
    st.info("ℹ️ Silmek için kutucuğu işaretleyip Kaydet'e basın.")
    if not df.empty:
        edit_data = df.copy()
        edit_data.insert(0, "Sil", False)
        edited_df = st.data_editor(
            edit_data[['Sil', 'Baslik', 'Link', 'Aciklama', 'Tags']], 
            num_rows="dynamic", use_container_width=True, key="data_editor",
            column_config={"Sil": st.column_config.CheckboxColumn("Sil?", width="small")}
        )
        if st.button("💾 Değişiklikleri Kaydet"):
            edited_df = edited_df.reset_index(drop=True)
            rows_del = edited_df[edited_df['Sil'] == True]
            if not rows_del.empty:
                st.toast(f"{len(rows_del)} kayıt silindi.", icon="🗑️")
                edited_df = edited_df[edited_df['Sil'] == False]
            edited_df = edited_df.drop(columns=['Sil'])
            
            err_title = edited_df['Baslik'].isnull().any() or (edited_df['Baslik'].astype(str).str.strip() == '').any()
            err_desc = edited_df['Aciklama'].isnull().any() or (edited_df['Aciklama'].astype(str).str.strip() == '').any()
            
            if err_title or err_desc:
                st.error("❌ Hata: Başlık veya Açıklama boş olamaz!")
            else:
                edited_df['Tags'] = edited_df['Tags'].fillna("").astype(str).apply(clean_tags)
                edited_df.to_csv(DATA_FILE, index=False)
                st.success("✅ Güncellendi!")
                st.rerun()
    else:
        st.write("Veri yok.")

# --- TAB 4: ANALİZ ---
with tab4:
    st.header("☁️ İçerik Analizi")
    target_df = filtered_df if not filtered_df.empty else pd.DataFrame()

    if not target_df.empty:
        analysis_type = st.radio(
            "Analiz Kaynağı:", 
            ["Etiketler", "Açıklamalar"], 
            horizontal=True,
            help="'Etiketler' genel kategorileri, 'Açıklamalar' ise içerik detaylarını analiz eder."
        )
        
        stopwords = load_stopwords()
        words_list = []
        
        if analysis_type == "Etiketler":
            raw_series = target_df['Tags'].fillna("").astype(str).str.split(',')
            words_list = [item.strip() for sublist in raw_series for item in sublist if item.strip()]
            
        else: # Açıklamalar
            full_text = " ".join(target_df['Aciklama'].fillna("").astype(str)).lower()
            for char in [".", ",", "!", "?", ":", ";", "(", ")", "\"", "'"]:
                full_text = full_text.replace(char, " ")
            
            raw_words = full_text.split()
            words_list = [w for w in raw_words if w not in stopwords and len(w) > 2]

        if words_list:
            word_counts = pd.Series(words_list).value_counts().reset_index()
            word_counts.columns = ['Kelime', 'Frekans']
            top_10 = word_counts.head(10)

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("🥧 Dağılım (Pie Chart)")
                fig_pie = px.pie(
                    top_10, values='Frekans', names='Kelime', 
                    title=f"En Çok Geçen {analysis_type} (Top 10)",
                    template="plotly_dark", hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.subheader("📊 Sıralama (Bar Chart)")
                fig_bar = px.bar(
                    top_10, x='Frekans', y='Kelime', orientation='h',
                    template="plotly_dark", color='Frekans'
                )
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader(f"☁️ {analysis_type} Bulutu")
            text_for_cloud = " ".join(words_list)
            
            wordcloud = WordCloud(
                width=800, height=400, background_color='black',
                colormap='turbo', min_font_size=10
            ).generate(text_for_cloud)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig) 
        else:
            st.warning("Analiz edilecek yeterli kelime bulunamadı.")
    else:
        st.info("Analiz için veri yok veya filtreleme sonucu boş.")