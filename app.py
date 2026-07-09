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

# --- 1. MODELİ YÜKLE ---
@st.cache_resource
def load_model():
    # Çok dilli model Türkçe açıklamalarda çok daha iyi sonuç verir.
    # İndirilemezse (ağ/SSL kısıtı) cache'teki İngilizce modele düşülür.
    try:
        return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    except Exception:
        st.warning("⚠️ Çok dilli model indirilemedi; cache'teki all-MiniLM-L6-v2 kullanılıyor (Türkçe arama kalitesi düşük olabilir).")
        # local_files_only: ağa hiç çıkmadan HF cache'inden yükler (SSL/proxy kısıtlarında da çalışır)
        return SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)

model = load_model()

# --- 2. YARDIMCI FONKSİYONLAR ---
@st.cache_data
def clean_tags(tag_input):
    tag_str = str(tag_input)
    if not tag_input or tag_str.strip() == "" or tag_str.lower() == "nan":
        return "genel"
    tags = [t.strip().lower() for t in tag_str.split(',')]
    tags = sorted(list(set(tags)))
    return ", ".join(tags)

def get_unique_tags(dataframe):
    all_tags = set()
    if not dataframe.empty:
        for tags in dataframe['Tags'].fillna("").astype(str):
            splitted = [t.strip() for t in tags.split(',')]
            all_tags.update(splitted)
    if "" in all_tags: all_tags.remove("")
    return sorted(list(all_tags))

@st.cache_data
def load_stopwords():
    default_stops = {"ve", "ile", "bir", "bu", "için", "ama", "fakat", "o", "şu", "da", "de"}
    if os.path.exists("stopwords.txt"):
        try:
            with open("stopwords.txt", "r", encoding="utf-8") as f:
                file_stops = set(f.read().splitlines())
            return file_stops
        except OSError:
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
@st.cache_data
def process_embeddings(dataframe):
    dataframe['Aciklama'] = dataframe['Aciklama'].fillna('')
    dataframe['Tags'] = dataframe['Tags'].fillna('')
    combined_text = dataframe['Aciklama'] + ". " + dataframe['Tags']
    embeddings = model.encode(combined_text.tolist(), normalize_embeddings=True)
    
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

    if st.session_state.get("data_saved", False):
        st.session_state.new_title_input = ""
        st.session_state.new_link_input = ""
        st.session_state.new_desc_input = ""
        st.session_state.new_tags_input = ""
        st.session_state.data_saved = False 

    new_title = st.text_input("Başlık", key="new_title_input")
    new_link = st.text_input("Link", key="new_link_input")
    new_desc = st.text_area("Açıklama", key="new_desc_input")
    
    if "new_tags_input" not in st.session_state:
        st.session_state.new_tags_input = ""

    if st.button("✨ Tag Öner"):
        if new_desc and not df.empty:
            all_existing_tags = get_unique_tags(df)
            if all_existing_tags:
                desc_vec = model.encode([new_desc], normalize_embeddings=True)
                tags_vec = model.encode(all_existing_tags, normalize_embeddings=True)
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
            process_embeddings.clear()
            clean_tags.clear()
            st.success(f"Eklendi!")
            st.rerun() 
        else:
            st.warning("Başlık ve Açıklama zorunludur!")
    
    st.divider()
    st.header("💾 Yedekleme")
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Veri Setini İndir (CSV)", csv, 'my_semantic_brain_backup.csv', 'text/csv')
    
    uploaded_file = st.file_uploader("📤 Yedekten Yükle (CSV)", type="csv")
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            required_cols = ["Baslik", "Link", "Aciklama", "Tags"]
            if all(col in uploaded_df.columns for col in required_cols):
                uploaded_df['Tags'] = uploaded_df['Tags'].fillna("").astype(str).apply(clean_tags)
                uploaded_df.to_csv(DATA_FILE, index=False)
                process_embeddings.clear()
                st.success("✅ Yüklendi! Yenileniyor...")
                st.rerun()
            else:
                st.error("❌ Hatalı CSV formatı.")
        except Exception as e:
            st.error(f"Hata: {e}")

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
    # Session state başlangıcı (Şanslı seçim için)
    if 'lucky_selection' not in st.session_state:
        st.session_state.lucky_selection = None

    # Arama çubuğu ve Şanslı Butonu
    col_search, col_lucky = st.columns([5, 1])
    
    with col_search:
        # Varsayılan değeri belirle: Eğer şanslı seçim varsa onun başlığı gelsin
        default_query = ""
        if st.session_state.lucky_selection is not None:
            default_query = st.session_state.lucky_selection['Baslik']
            
        search_query = st.text_input("Akıllı Arama", value=default_query)
        
    with col_lucky:
        # CSS Spacer ile hizalama
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🎲 Şanslıyım"):
            if not filtered_df.empty:
                # Rastgele seçim yap ve state'e kaydet
                st.session_state.lucky_selection = filtered_df.sample(1).iloc[0]
                st.rerun() # UI'ı yenile ki input dolsun
    
    # Pagination Logic
    if 'result_limit' not in st.session_state: st.session_state.result_limit = 10
    if 'last_query' not in st.session_state: st.session_state.last_query = ""
    
    # Arama Metni Belirleme Mantığı
    # Eğer input'taki yazı şanslı seçimin başlığına eşitse, arama için açıklamayı kullan (daha iyi sonuç için)
    # Değilse (kullanıcı elle bir şey yazdıysa), yazdığını kullan.
    query_text_for_model = search_query
    
    if st.session_state.lucky_selection is not None and search_query == st.session_state.lucky_selection['Baslik']:
        query_text_for_model = st.session_state.lucky_selection['Aciklama']
        st.success(f"🎲 **Şansına bu çıktı:** {st.session_state.lucky_selection['Baslik']}")

    # Limit Sıfırlama
    # Eğer sorgu değişirse limiti başa al (Sorgu değişti mi kontrolü)
    if query_text_for_model != st.session_state.last_query:
        st.session_state.result_limit = 10
        st.session_state.last_query = query_text_for_model

    if not filtered_df.empty:
        display_df = filtered_df.copy()
        
        if query_text_for_model:
            query_vec = model.encode([query_text_for_model], normalize_embeddings=True)
            full_sim_scores = np.dot(embeddings, query_vec.T).flatten()
            df['Benzerlik'] = full_sim_scores
            display_df['Benzerlik'] = df.loc[display_df.index, 'Benzerlik']
            display_df = display_df.sort_values(by='Benzerlik', ascending=False)
            
            # Şanslı butonuna basıldıysa başlık farklı olsun
            if st.session_state.lucky_selection is not None and search_query == st.session_state.lucky_selection['Baslik']:
                 st.write(f"**'{st.session_state.lucky_selection['Baslik']}'** ve benzerleri:")
            else:
                 st.write(f"**'{search_query}'** için sonuçlar ({len(display_df)} kayıt):")

        else:
            label = "VE" if use_and_logic else "VEYA"
            msg = f"🏷️ **Seçili etiketlere ({label}) göre**" if selected_tags else "Tüm kayıtlar:"
            st.write(f"{msg} ({len(display_df)} kayıt)")

        total_results = len(display_df)
        results = display_df.head(st.session_state.result_limit)
        
        if not results.empty:
            if 'Benzerlik' in results.columns and query_text_for_model:
                # Normalizasyon tüm sonuç kümesi üzerinden; sayfa değişince bar oranları kaymaz
                min_s, max_s = display_df['Benzerlik'].min(), display_df['Benzerlik'].max()
                denom = max_s - min_s
            else:
                denom = 1 

            for index, row in results.iterrows():
                score_text = ""
                if query_text_for_model and 'Benzerlik' in row:
                    sc = row['Benzerlik']
                    norm = (sc - min_s) / denom if denom != 0 else sc
                    st.progress(max(0.0, min(1.0, float(norm))))
                    score_text = f"(Skor: {sc:.2f})"
                
                st.info(f"**{row['Baslik']}** {score_text} | 🏷️ {row['Tags']}\n\n{row['Aciklama']}\n\n[🔗 Git]({row['Link']})")

            if st.session_state.result_limit < total_results:
                if st.button(f"👇 Daha Fazla Göster ({st.session_state.result_limit} / {total_results})", use_container_width=True):
                    st.session_state.result_limit += 10
                    st.rerun()
        else:
            st.warning("Sonuç yok.")
    else:
        st.write("Veri yok.")

with tab2:
    if not filtered_df.empty:
        label = "VE" if use_and_logic else "VEYA"
        msg = f"🌌 Galaksi **{', '.join(selected_tags)}** ({label})" if selected_tags else "🌌 Galaksi Görünümü"
        st.write(msg)
        
        # GÖRSELLEŞTİRME NOTU:
        # Renkler (Tags) kategorik olarak ayrışsa da, 
        # x,y,z konumları içerik benzerliğine göre belirlenir.
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
    st.info("Silmek için kutucuğu işaretleyip Kaydet'e basın.")
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
                process_embeddings.clear()
                clean_tags.clear()
                st.success("✅ Güncellendi!")
                st.rerun()
    else:
        st.write("Veri yok.")

with tab4:
    st.header("☁️ İçerik Analizi")
    target_df = filtered_df if not filtered_df.empty else pd.DataFrame()

    if not target_df.empty:
        analysis_type = st.radio("Analiz Kaynağı:", ["Etiketler", "Açıklamalar"], horizontal=True)
        stopwords = load_stopwords()
        words_list = []
        
        if analysis_type == "Etiketler":
            raw_series = target_df['Tags'].fillna("").astype(str).str.split(',')
            words_list = [item.strip() for sublist in raw_series for item in sublist if item.strip()]
        else:
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
                st.subheader("🥧 Dağılım")
                fig_pie = px.pie(top_10, values='Frekans', names='Kelime', template="plotly_dark", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col2:
                st.subheader("📊 Sıralama")
                fig_bar = px.bar(top_10, x='Frekans', y='Kelime', orientation='h', template="plotly_dark", color='Frekans')
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader(f"☁️ {analysis_type} Bulutu")
            text_for_cloud = " ".join(words_list)
            wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='turbo', min_font_size=10).generate(text_for_cloud)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig) 
        else:
            st.warning("Yeterli kelime yok.")
    else:
        st.info("Veri yok.")