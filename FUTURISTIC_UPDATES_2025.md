# 🚀 Semantic Galaxy - Gelecek Özellikler Roadmap (5 Aralık 2025)

> **Not**: Bu dokümantasyon, projenin gelecek sürümlerine eklenecek tüm planlanan özellikleri içerir.  
> Özellikler öncelik ve kategori bazında organize edilmiştir.

---

## 📑 İçindekiler

1. [🏆 Öncelikli / Kolay Eklenebilir Özellikler (Quick Wins)](#1-öncelikli--kolay-eklenebilir-özellikler-quick-wins)
2. [🤖 Yapay Zeka & LLM Entegrasyonu (Advanced)](#2-yapay-zeka--llm-entegrasyonu-advanced)
3. [🎨 Görselleştirme ve Arayüz (UI/UX)](#3-görselleştirme-ve-arayüz-uiux)
4. [🛠️ Teknik & Performans İyileştirmeleri](#4-teknik--performans-i̇yileştirmeleri)
5. [🧠 İleri Seviye Anlamlandırma (Sense-Making)](#5-i̇leri-seviye-anlamlandırma-sense-making)
6. [🎯 Kullanıcı Deneyimi İyileştirmeleri](#6-kullanıcı-deneyimi-i̇yileştirmeleri)
7. [📱 Platform Genişletmeleri](#7-platform-genişletmeleri)

---

## 1. 🏆 Öncelikli / Kolay Eklenebilir Özellikler (Quick Wins)

> **Özellik**: Mevcut veri yapısını (CSV) değiştirmeden veya çok az değiştirerek hemen ekleyebileceğimiz özellikler.

### 1.1 Domain (Site) Analizi 📊

**Nedir:**  
Analiz sekmesine eklenecek yeni bir grafik türü.

**İşlevi:**  
- Kullanıcının kaydettiği linklerin domain'lerini (site isimlerini) otomatik olarak ayıklar
- Örnek: `youtube.com`, `medium.com`, `github.com`
- "En çok hangi kaynaktan besleniyorum?" sorusuna pasta grafiği ile cevap verir

**Teknik Detaylar:**
```python
from urllib.parse import urlparse

def extract_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.replace('www.', '')

# Analiz
domains = df['Link'].apply(extract_domain)
domain_counts = domains.value_counts()
fig_domain = px.pie(domain_counts, values=domain_counts.values, names=domain_counts.index)
```

**Değer:**
- Kullanıcı hangi platformları sık kullandığını görür
- "YouTube bağımlısı mıyım?" sorusuna veri ile cevap
- Çeşitlilik analizi: Çok fazla tek kaynaktan mı besleniyorum?

**Öncelik:** 🔴 Yüksek  
**Durum:** ❌ Henüz yapılmadı  
**Tahmini Süre:** 30-45 dakika

---

### 1.2 Toplu Etiket Düzenleme (Bulk Tag Editor) 🏷️

**Nedir:**  
Veri Yönetimi sekmesine eklenecek gelişmiş bir araç.

**İşlevi:**  
Zamanla etiketler kirlenir:
- `tool`, `tools`, `araç`, `araclar` → Hepsi aynı anlama geliyor
- `ai`, `AI`, `yapay-zeka` → Normalizasyon gerekli

Toplu düzenleme ile:
- "Tüm `tool` etiketlerini `araç` yap"
- "Tüm `ai` etiketlerini `yapay-zeka` ile birleştir"
- Kullanılmayan etiketleri otomatik temizle

**Teknik Detaylar:**
```python
st.subheader("🔧 Toplu Etiket Düzenleme")

col1, col2 = st.columns(2)
with col1:
    old_tag = st.text_input("Eski Etiket (Silinecek)")
with col2:
    new_tag = st.text_input("Yeni Etiket (Yerine Gelecek)")

if st.button("Toplu Değiştir"):
    # Tüm satırlarda eski etiketi yeni ile değiştir
    df['Tags'] = df['Tags'].str.replace(old_tag, new_tag, regex=False)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"✅ {old_tag} → {new_tag} dönüştürüldü!")
```

**Değer:**
- Veri kalitesi artışı
- Manuel tek tek düzeltmekten kurtarır
- Etiket standardizasyonu

**Öncelik:** 🟡 Orta  
**Durum:** ❌ Konuşuldu ama eklenmedi  
**Tahmini Süre:** 1-2 saat

---

### 1.3 Tarih Özelliği (Zaman Tüneli) 📅

**Nedir:**  
Veri setine `Ekleme_Tarihi` sütunu eklemek ve zaman bazlı analizler yapmak.

**İşlevi:**
- Her yeni kayıt eklendiğinde otomatik tarih eklenir
- "Son eklenenler" sıralaması yapılabilir
- Analiz sekmesinde:
  - "Hangi ay ne kadar içerik kaydettim?" (Bar Chart)
  - "Zamanla ilgi alanlarım nasıl değişti?" (Tag Timeline)
  - Haftanın hangi günlerinde aktifim? (Heatmap)

**Teknik Detaylar:**
```python
from datetime import datetime

# CSV'ye yeni sütun ekle
if 'Ekleme_Tarihi' not in df.columns:
    df['Ekleme_Tarihi'] = datetime.now().strftime('%Y-%m-%d')

# Yeni kayıt eklerken
new_data = {
    ...
    "Ekleme_Tarihi": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# Timeline grafiği
df['Tarih'] = pd.to_datetime(df['Ekleme_Tarihi'])
df['Ay'] = df['Tarih'].dt.to_period('M')
monthly_counts = df.groupby('Ay').size()
fig_timeline = px.bar(x=monthly_counts.index.astype(str), y=monthly_counts.values)
```

**Değer:**
- Personal journey takibi
- "Öğrenme hızım nasıl?" sorusuna cevap
- Motivasyon tracker: "Bu ay hiç birşey eklemememişim"

**Öncelik:** 🔴 Yüksek (Veri yapısı değişikliği gerektirir)  
**Durum:** ❌ Henüz yapılmadı  
**Tahmini Süre:** 2-3 saat (Backward compatibility için eski kayıtlara default tarih ekleme)

---

## 2. 🤖 Yapay Zeka & LLM Entegrasyonu (Advanced)

> **Özellik**: Uygulamayı "akıllı bir asistan" seviyesine çıkaracak en büyük adım.

### 2.1 Verilerinle Sohbet (RAG - Chat with Data) 💬

**Nedir:**  
Bookmark veritabanınızla doğal dilde konuşabileceğiniz bir chatbot.

**İşlevi:**
**Örnek Sorular:**
- "Ses kopyalama için hangi araçlar vardı ve hangisi ücretsiz?"
- "AI ses toollarıyla Notion AI arasındaki fark nedir?"
- "Blender'ı neden kaydetmiştim?"

**Sistem Akışı:**
1. Kullanıcı soru sorar
2. Sistem:
   - Soruyu vektöre çevirir (SentenceTransformer)
   - En benzer 5-10 bookmark'ı bulur (Semantic Search)
   - Bu bookmark'ların açıklamalarını LLM'e context olarak verir
3. LLM (Gemini/GPT):
   - Context'i analiz eder
   - Doğal dilde cevap üretir
   - Kaynak olarak hangi bookmark'ları kullandığını belirtir

**Teknik Detaylar:**
```python
import google.generativeai as genai

def rag_search(query, top_k=5):
    # 1. Semantic search
    query_vec = model.encode([query])
    similarities = np.dot(embeddings, query_vec.T).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    # 2. Context hazırla
    context = ""
    for idx in top_indices:
        row = df.iloc[idx]
        context += f"Başlık: {row['Baslik']}\n"
        context += f"Açıklama: {row['Aciklama']}\n"
        context += f"Tagler: {row['Tags']}\n\n"
    
    # 3. LLM'e gönder
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    llm = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Aşağıdaki bookmark veritabanından yola çıkarak kullanıcının sorusunu cevapla.
    
    CONTEXT:
    {context}
    
    SORU: {query}
    
    CEVAP (Hangi bookmark'lardan yararlandığını belirt):
    """
    
    response = llm.generate_content(prompt)
    return response.text

# UI
with tab5:  # Yeni tab: Sohbet
    st.header("💬 Bookmark'larınla Sohbet Et")
    user_query = st.text_input("Sorunuz:")
    if st.button("Sor"):
        answer = rag_search(user_query)
        st.markdown(answer)
```

**Gereksinimler:**
- Gemini API Key (`GEMINI_API_KEY` env variable)
- Alternatif: OpenAI GPT (`OPENAI_API_KEY`)
- Maliyet: ~$0.01 - $0.05 per query (token sayısına göre)

**Değer:**
- **EN BÜYÜK ÖZELLİK!** Kullanıcı deneyimini 10x artırır
- Pasif veriden aktif bilgiye dönüşüm
- "Second brain" kavramının gerçek uygulaması

**Öncelik:** 🔴🔴 En Yüksek  
**Durum:** ❌ En büyük sonraki adım  
**Tahmini Süre:** 4-6 saat (API setup, UI, testing)

---

### 2.2 Otomatik İçerik Özeti (Auto-Summarize) 📝

**Nedir:**  
Link eklerken otomatik olarak o sitenin içeriğini okuyup açıklama alanını dolduran özellik.

**İşlevi:**
1. Kullanıcı sadece linki yapıştırır
2. Sistem:
   - Siteye HTTP request atar (BeautifulSoup/Scrapy)
   - HTML'den ana metni çıkarır
   - LLM'e gönderir: "Bu metni 2-3 cümleyle özetle"
3. Açıklama alanı otomatik doldurulur
4. Kullanıcı isterse düzenler, kayıt eder

**Teknik Detaylar:**
```python
import requests
from bs4 import BeautifulSoup

def auto_summarize(url):
    try:
        # 1. Siteyi oku
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 2. Ana metni bul (heuristic)
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs[:5]])  # İlk 5 paragraf
        
        # 3. LLM ile özetle
        prompt = f"Şu metni 2-3 cümleyle özetle:\n\n{text[:500]}"
        summary = llm.generate_content(prompt).text
        
        return summary
    except:
        return ""

# UI
new_link = st.text_input("Link")
if st.button("🤖 Otomatik Özet Getir"):
    summary = auto_summarize(new_link)
    st.session_state.new_desc_input = summary
    st.rerun()
```

**Değer:**
- Kullanıcı için zaman tasarrufu
- Daha tutarlı açıklamalar (LLM'in tonu hep aynı)
- Lazy users için mükemmel

**Öncelik:** 🟡 Orta  
**Durum:** ❌ Henüz yapılmadı  
**Tahmini Süre:** 2-3 saat (Web scraping, error handling)

**Not:** Bazı siteler bot'ları engelleyebilir. YouTube, Twitter gibi siteler için API kullanmak gerekebilir.

---

## 3. 🎨 Görselleştirme ve Arayüz (UI/UX)

### 3.1 Ağ Grafiği (Network Graph) 🕸️

**Nedir:**  
2D, birbirine çizgilerle bağlı düğümler ile görselleştirme.

**İşlevi:**
- 3D Scatter plot bazen karışık olabilir
- Ağ grafiğinde:
  - Her bookmark bir düğüm
  - Benzerlik > 0.7 olanlar çizgi ile bağlanır
  - Tag'ler farklı renkler
  - Force-directed layout (düğümler birbirini iter/çeker)

**Kullanım Senaryosu:**
- "AI" ve "Python" etiketleri birbirine sık bağlanıyorsa, grafikte yakın görünürler
- "Ses Toolları" kümesi vs "Görsel Toolları" kümesi net ayrışır
- Outlier'lar (tek başına kalan içerikler) kolayca görülür

**Teknik Detaylar:**
```python
import networkx as nx
import plotly.graph_objects as go

# 1. Benzerlik matrisi oluştur
similarity_matrix = cosine_similarity(embeddings)

# 2. Network graph oluştur
G = nx.Graph()
for i in range(len(df)):
    G.add_node(i, title=df.iloc[i]['Baslik'], tag=df.iloc[i]['Tags'])

# 3. Kenarları ekle (threshold > 0.7)
for i in range(len(df)):
    for j in range(i+1, len(df)):
        if similarity_matrix[i, j] > 0.7:
            G.add_edge(i, j, weight=similarity_matrix[i, j])

# 4. Layout hesapla
pos = nx.spring_layout(G, k=0.5, iterations=50)

# 5. Plotly ile çiz
edge_trace = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_trace.append(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines'))

node_trace = go.Scatter(
    x=[pos[k][0] for k in G.nodes()],
    y=[pos[k][1] for k in G.nodes()],
    mode='markers+text',
    text=[G.nodes[k]['title'] for k in G.nodes()]
)

fig = go.Figure(data=edge_trace + [node_trace])
st.plotly_chart(fig)
```

**Değer:**
- Alternatif görselleştirme (bazı kullanıcılar 2D'yi tercih eder)
- Cluster'ları daha net gösterir
- "Köprü" içerikleri bulur (iki farklı konuyu birleştiren)

**Öncelik:** 🟡 Orta  
**Durum:** ❌ Alternatif görselleştirme olarak eklenebilir  
**Tahmini Süre:** 3-4 saat (NetworkX, layout optimization)

---

### 3.2 Koyu/Açık Mod Desteği (Theme Toggle) 🌓

**Nedir:**  
Kullanıcının arayüz renklerini değiştirmesini sağlayan toggle.

**İşlevi:**
- Şu anda uygulama sabit dark mode
- Toggle ile:
  - ☀️ Light mode: Beyaz arka plan, siyah yazılar
  - 🌙 Dark mode: Siyah arka plan, beyaz yazılar
- Tercih `st.session_state` ile kaydedilir

**Teknik Detaylar:**
```python
# Sidebar
theme = st.sidebar.radio("🎨 Tema", ["🌙 Koyu", "☀️ Açık"])

if theme == "☀️ Açık":
    bg_color = "#FFFFFF"
    text_color = "#000000"
    card_color = "#F5F5F5"
else:
    bg_color = "#0E1117"
    text_color = "#FAFAFA"
    card_color = "#262730"

# CSS
st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .result-card {{
        background-color: {card_color};
    }}
</style>
""", unsafe_allow_html=True)
```

**Değer:**
- Accessibility (bazı kullanıcılar dark mode'u sevmez)
- Gündüz/gece kullanımı
- Profesyonel görünüm

**Öncelik:** 🟢 Düşük (Nice-to-have)  
**Durum:** ❌ Streamlit otomatik yapıyor ama özel CSS gerekli  
**Tahmini Süre:** 1-2 saat

---

## 4. 🛠️ Teknik & Performans İyileştirmeleri

### 4.1 Veritabanı Geçişi (SQLite/PostgreSQL) 🗄️

**Nedir:**  
CSV yerine gerçek bir ilişkisel veritabanı kullanmak.

**Neden Gerekli:**
- CSV Sınırları:
  - 10,000+ kayıtla yavaşlar
  - Concurrent write desteği yok (multi-user için uygun değil)
  - Index yok (arama O(n) complexity)
  - Transaction yok (veri bütünlüğü riski)

**SQLite ile Artılar:**
- Index'ler ile hızlı arama
- ACID transactions (veri güvenliği)
- SQL queries (esnek filtreleme)
- Dosya bazlı (deploy kolay)

**Teknik Detaylar:**
```python
import sqlite3

# 1. Veritabanı oluştur
conn = sqlite3.connect('semantic_galaxy.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baslik TEXT NOT NULL,
    link TEXT,
    aciklama TEXT,
    tags TEXT,
    ekleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    embedding BLOB
)
''')

# 2. CSV'den migrate et
df = pd.read_csv('data.csv')
df.to_sql('bookmarks', conn, if_exists='replace', index=False)

# 3. Query örneği
cursor.execute("SELECT * FROM bookmarks WHERE tags LIKE '%ai%' ORDER BY ekleme_tarihi DESC LIMIT 10")
results = cursor.fetchall()
```

**PostgreSQL (Production için):**
- Multi-user desteği
- Cloud deployment (Heroku, Render)
- Full-text search
- JSON support (embeddings için)

**Değer:**
- Scalability (1M+ kayıt)
- Performance (index'ler sayesinde)
- Data integrity
- Professional architecture

**Öncelik:** 🟡 Orta (Şu an veri az, acil değil)  
**Durum:** ❌ Belirtildiği gibi acil değil  
**Tahmini Süre:** 4-6 saat (Migration script, backward compatibility)

---

### 4.2 API Servisi Haline Getirmek 🌐

**Nedir:**  
FastAPI kullanarak bu sistemi bir arka uç (backend) servisine dönüştürmek.

**İşlevi:**
Streamlit UI yerine (veya ek olarak) REST API sunmak:

**API Endpoints:**
```
GET  /api/bookmarks          → Tüm bookmark'ları listele
POST /api/bookmarks          → Yeni bookmark ekle
GET  /api/bookmarks/{id}     → Tek bookmark detayı
PUT  /api/bookmarks/{id}     → Bookmark güncelle
DELETE /api/bookmarks/{id}   → Bookmark sil
POST /api/search             → Semantic search
GET  /api/tags               → Tüm tag'leri listele
POST /api/chat               → RAG chatbot
```

**Kullanım Senaryoları:**
1. **Chrome Eklentisi:**
   - Bir siteye girdiğinde "💾 Kaydet" butonu
   - API'ye POST request atar
   
2. **Mobil Uygulama:**
   - React Native/Flutter
   - API backend kullanır
   
3. **Zapier/IFTTT Entegrasyonu:**
   - "Pocket'a kaydettiğim her link Semantic Galaxy'e de eklensin"
   - Webhook ile API'ye gönderir

**Teknik Detaylar:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Semantic Galaxy API")

class Bookmark(BaseModel):
    baslik: str
    link: str
    aciklama: str
    tags: str

@app.post("/api/bookmarks")
async def create_bookmark(bookmark: Bookmark):
    # Veritabanına ekle
    new_id = db.insert(bookmark.dict())
    # Embedding hesapla
    embedding = model.encode(bookmark.aciklama)
    # Cache'i temizle
    return {"id": new_id, "status": "created"}

@app.post("/api/search")
async def semantic_search(query: str, limit: int = 10):
    query_vec = model.encode([query])
    results = vector_search(query_vec, limit)
    return results

# Streamlit ayrı çalışır, API'yi kullanır
# Frontend - Backend separation
```

**Değer:**
- Platform-agnostic (Web, Mobile, Desktop)
- Chrome Extension mümkün olur
- Third-party integrations
- Microservices architecture

**Öncelik:** 🟢 Düşük (Uzun vadeli)  
**Durum:** ❌ Henüz yapılmadı  
**Tahmini Süre:** 8-12 saat (API design, testing, documentation)

---

## 5. 🧠 İleri Seviye Anlamlandırma (Sense-Making)

> **Not:** Bu bölüm FUTURE_VISION.md'den alınmıştır.

### 5.1 N-Grams Analizi (Kelime Öbekleri) 📊

**Nedir:**  
Tek kelimeler yerine 2-3 kelimelik anlamlı öbekleri analiz etmek.

**Problem:**
- Word Cloud sadece "veri", "analizi" gösterir
- "Veri Analizi" konseptini kaçırır

**Çözüm:**
```python
from sklearn.feature_extraction.text import CountVectorizer

# Bigrams (2'li gruplar)
vectorizer = CountVectorizer(ngram_range=(2, 2), max_features=20)
bigrams = vectorizer.fit_transform(df['Aciklama'])
bigram_names = vectorizer.get_feature_names_out()

# Sonuç: "veri analizi", "yapay zeka", "ses üretimi"
```

**Değer:**
- Daha anlamlı analiz
- Konseptleri yakalama
- Research için insights

**Öncelik:** 🔴 Yüksek  
**Durum:** ❌ Planlı  
**Tahmini Süre:** 2-3 saat

---

### 5.2 Eylem Odaklı Analiz (Fiil Çıkarımı) 🎯

**Nedir:**  
Açıklamalardaki fiilleri (verbs) tespit edip analiz etmek.

**İşlevi:**
- "Generate", "Create", "Manage", "Learn" gibi fiilleri yakalar
- Kategoriler:
  - 🎨 Üretmek: Create, Generate, Build
  - 📚 Öğrenmek: Learn, Study, Tutorial
  - 🔧 Yönetmek: Manage, Organize, Track

**Teknik:**
```python
import spacy
nlp = spacy.load("tr_core_news_lg")  # Türkçe model

doc = nlp(text)
verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
```

**Çıktı:**
- Pie Chart: "Bookmark'larımın %60'ı öğrenme, %30'u üretme"

**Öncelik:** 🟡 Orta  
**Durum:** ❌ FUTURE_VISION.md'de belirtildi  
**Tahmini Süre:** 3-4 saat

---

### 5.3 Tag Co-occurrence Matrix (Etiket İlişkileri) 🔗

**Nedir:**  
Hangi tag'lerin birlikte kullanıldığını analiz etmek.

**Çıktı:**
- Heatmap: "AI" ile "Python" sıklıkla birlikte
- Venn Diagram: Kesişimler

**Değer:**
- Tag hiyerarşisi oluşturmak için veri
- Gap analysis: "AI + Video" hiç yok mu?

**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 2-3 saat

---

## 6. 🎯 Kullanıcı Deneyimi İyileştirmeleri

### 6.1 Kategoriler Sistemi 📂

**Nedir:**  
Tag üstü bir hiyerarşi katmanı.

**Örnek:**
```
📁 AI Tools
  ├─ 🎤 Ses
  │   ├─ elevenlabs
  │   └─ play.ht
  ├─ 🎨 Görsel
  │   └─ midjourney
  └─ 📝 Metin
      └─ chatgpt
```

**Teknik:**
- CSV'ye `Category` sütunu
- Manuel veya otomatik (LLM ile)

**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 2-3 saat

---

### 6.2 Notlar Sistemi 📝

**Nedir:**  
Her bookmark'a kişisel notlar eklemek.

**UI:**
```python
with st.expander(f"📝 {row['Baslik']} için notlarım"):
    note = st.text_area("Not", value=row['Notes'], key=f"note_{index}")
    if st.button("Kaydet", key=f"save_{index}"):
        df.at[index, 'Notes'] = note
```

**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 1-2 saat

---

### 6.3 Favoriler ⭐

**Nedir:**  
Önemli bookmark'ları işaretleme.

**Teknik:**
- CSV'ye `Is_Favorite` (boolean) sütunu
- UI'da ⭐ ikonu ile toggle
- Sidebar'da "Sadece Favoriler" filtresi

**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 1 saat

---

## 7. 📱 Platform Genişletmeleri

### 7.1 Chrome Extension 🌐

**Nedir:**  
Tarayıcıda herhangi bir sayfadayken "Kaydet" butonu.

**İşlevi:**
1. Sayfaya sağ tıkla → "Semantic Galaxy'e Ekle"
2. Popup açılır:
   - Başlık: Otomatik doldurulur (sayfa title)
   - Link: Mevcut URL
   - Açıklama: LLM ile özetlenir
   - Tagler: Otomatik önerilir
3. "Kaydet" → API'ye POST

**Teknik:**
- Manifest v3
- Background script
- FastAPI backend gerekli

**Öncelik:** 🟡 Orta (API sonrası)  
**Tahmini Süre:** 6-8 saat

---

### 7.2 Mobile App (PWA/React Native) 📱

**Nedir:**  
Mobil cihazlardan erişim.

**Seçenekler:**
1. **PWA (Progressive Web App):**
   - Streamlit zaten responsive
   - "Add to Home Screen" ile uygulama gibi
   - Kolay, hızlı

2. **React Native:**
   - Native app deneyimi
   - Offline support
   - Push notifications
   - Daha uzun sürer

**Öncelik:** 🟢 Düşük (Uzun vadeli)  
**Tahmini Süre:** PWA: 2-3 saat, React Native: 20+ saat

---

## 📊 Öncelik Matrisi (Özet)

| Özellik | Öncelik | Süre | Etki | Zorluk |
|---------|---------|------|------|--------|
| **RAG Chat** | 🔴🔴 En Yüksek | 4-6h | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| **Domain Analizi** | 🔴 Yüksek | 30min | ⭐⭐⭐ | ⚡ |
| **Tarih/Timeline** | 🔴 Yüksek | 2-3h | ⭐⭐⭐⭐ | ⚡⚡ |
| **N-Grams** | 🔴 Yüksek | 2-3h | ⭐⭐⭐⭐ | ⚡⚡ |
| **Toplu Tag Edit** | 🟡 Orta | 1-2h | ⭐⭐⭐ | ⚡ |
| **Auto-Summarize** | 🟡 Orta | 2-3h | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| **Network Graph** | 🟡 Orta | 3-4h | ⭐⭐⭐ | ⚡⚡⚡ |
| **Kategoriler** | 🟡 Orta | 2-3h | ⭐⭐⭐ | ⚡⚡ |
| **SQLite Migration** | 🟡 Orta | 4-6h | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| **Theme Toggle** | 🟢 Düşük | 1-2h | ⭐⭐ | ⚡ |
| **Favoriler** | 🟢 Düşük | 1h | ⭐⭐ | ⚡ |
| **Notlar** | 🟢 Düşük | 1-2h | ⭐⭐⭐ | ⚡ |
| **FastAPI** | 🟢 Düşük | 8-12h | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| **Chrome Extension** | 🟢 Düşük | 6-8h | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| **Mobile App** | 🟢 Düşük | 20+h | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ |

**Legend:**
- 🔴 Yüksek Öncelik | 🟡 Orta Öncelik | 🟢 Düşük Öncelik
- ⭐ Etki (1-5) | ⚡ Zorluk (1-5)

---

## 🎯 Önerilen İlk 3 Özellik (Quick Wins)

Hemen başlamak için:

1. **Domain Analizi** (30 dk) → Hızlı görsel kazanım
2. **RAG Chat** (4-6 saat) → En büyük değer
3. **Timeline/Tarih** (2-3 saat) → Kullanıcı engagement artışı

---

## 📅 Versiyon Roadmap Önerisi

### v0.8 - Quick Wins (1 hafta)
- [x] Şanslıyım butonu ✅
- [ ] Domain analizi
- [ ] Toplu tag düzenleme
- [ ] Tarih/Timeline

### v0.9 - Intelligence (2-3 hafta)
- [ ] RAG Chat (Ana özellik)
- [ ] Auto-Summarize
- [ ] N-Grams analizi

### v1.0 - Production Ready (1 ay)
- [ ] SQLite migration
- [ ] Network graph
- [ ] Kategoriler
- [ ] Theme toggle

### v1.1+ - Ecosystem (2-3 ay)
- [ ] FastAPI backend
- [ ] Chrome extension
- [ ] Mobile PWA

---

**🎉 Tüm detaylar kaydedildi!**  
**Son Güncelleme:** 5 Aralık 2025
