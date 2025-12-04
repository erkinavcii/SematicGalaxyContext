# 🌌 Semantic Galaxy

> Sosyal medyadan kaydettiğin içerikleri sematik ilişkilerine göre 3D uzayda görselleştir ve akıllı arama ile eriş.

**Semantic Galaxy**, yer imlerini (bookmarks) klasik liste/klasör yapısından kurtarıp, içeriklerini anlayan ve aralarındaki ilişkileri görselleştiren yeni nesil bir kişisel bilgi yönetim sistemidir.

---

## 🎯 Problem

Sosyal medyada sürekli ilginç içerikler buluyorsun:
- "Sonra bakarım" diyip kaydediyorsun
- Zamanla yüzlerce kayıt birikiyor
- Kategorize değil, ne olduğunu unutuyorsun
- "AI ile ilgili ses aracıydı" diye hatırlıyorsun ama bulamıyorsun
- Benzer içerikler dağınık, ilişkileri göremiyorsun

---

## 💡 Çözüm

Semantic Galaxy, içeriklerini **anlar** ve **ilişkilendirir**:

### 🧠 Semantik Anlama
Machine learning ile içeriklerinin ne olduğunu anlar. "AI ses değiştirici" ile "yapay zeka vokal aracı" aynı yerde kümelenir.

### 🌐 3D Görselleştirme
Benzer içerikler uzayda birbirine yakın durur. Bir yıldız kümesi gibi, her nokta bir içerik.

### 🔍 Akıllı Arama
- **Tag bazlı**: "AI + Ses" filtresi
- **Semantik**: "Müzik yapan robotlar" yazsan bile ilgili araçları bulur
- **Hybrid**: İkisini birleştir

---

## ✨ Özellikler

### Mevcut (Faz 1 - Local Prototype)
- ✅ **Manuel veri girişi**: Title, URL, description, tags
- ✅ **Otomatik vektörleştirme**: NLP ile içerik analizi
- ✅ **3D görselleştirme**: Plotly ile interaktif galaksi haritası
- ✅ **Liste görünümü**: Klasik tablo formatında görüntüleme
- ✅ **Tag filtresi**: Çoklu etiket seçimi
- ✅ **Semantik arama**: Doğal dilde sorgu ("video düzenleme araçları")
- ✅ **Hybrid search**: Tag + semantik birleşimi

### Planlanan (Faz 2 - Web Deployment)
- 🔜 **Web/mobil erişim**: Telefondan kullanım
- 🔜 **Three.js görselleştirme**: Daha performanslı 3D render
- 🔜 **Düzenleme/silme**: CRUD işlemleri
- 🔜 **Export/Import**: CSV, JSON, Markdown formatları
- 🔜 **Favoriler**: Önemli içerikleri işaretle
- 🔜 **Notlar**: Her içeriğe kişisel notlar
- 🔜 **Dark mode**: Tema desteği

---

## 🛠️ Teknoloji Stack

### Backend & ML
- **Python 3.10+**: Core dil
- **sentence-transformers**: NLP embeddings (all-MiniLM-L6-v2 modeli)
- **UMAP**: Boyut indirgeme (384D → 3D)
- **scikit-learn**: Cosine similarity hesaplamaları
- **pandas**: Veri manipülasyonu

### Frontend
- **Streamlit**: Local web arayüzü
- **Plotly**: 3D interaktif görselleştirme

### Veri Saklama
- **JSON**: Hafif ve taşınabilir (ilk aşama)
- **PostgreSQL + pgvector**: Gelecek için (Faz 2)

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.10 veya üzeri
- 4GB RAM (1000 veri için)
- İnternet bağlantısı (ilk çalıştırmada model indirimi)

### Adım Adım

1. **Projeyi klonla**
```bash
git clone <repo-url>
cd SematicGalaxyContext
```

2. **Virtual environment oluştur**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# veya
source venv/bin/activate  # macOS/Linux
```

3. **Bağımlılıkları yükle**
```bash
pip install -r requirements.txt
```

4. **İlk veri dosyasını oluştur** (opsiyonel, uygulama otomatik oluşturur)
```bash
mkdir data
echo "[]" > data/bookmarks.json
```

5. **Uygulamayı çalıştır**
```bash
streamlit run app.py
```

6. **Tarayıcıda aç**
```
http://localhost:8501
```

---

## 📖 Kullanım

### 1. Yeni İçerik Ekleme

**Sidebar** (sol panel) üzerinden:
1. **Title**: İçerik başlığı (örn: "AI Ses Değiştirici")
2. **URL**: Link (opsiyonel)
3. **Description**: Açıklama (örn: "Yapay zeka ile ses değiştirme, müzik prodüksiyonu")
4. **Tags**: Etiketler (örn: AI, Ses, Tool)
5. **"Ekle"** butonuna tıkla

Sistem otomatik olarak:
- İçeriği vektörleştirir
- 3D uzayda konumunu hesaplar
- Galaksi haritasını günceller

### 2. Liste Görünümü

**📊 Liste** sekmesinde:
- Tüm içeriklerini tablo formatında gör
- Tag'e göre filtrele
- Başlığa tıklayarak sırala
- URL'ye tıklayarak siteye git

### 3. 3D Galaksi Keşfi

**🌌 3D Galaksi** sekmesinde:
- Fareyle döndür/zoom yap
- Noktalara hover yaparak detay gör
- Renkler tag'lere göre kodlanmış
- Yakın noktalar semantically benzer içerikler

### 4. Akıllı Arama

**🔍 Arama** sekmesinde:

**Örnek 1 - Sadece Tag:**
- Tag seçimi: ["AI", "Ses"]
- Sonuç: Her iki etikete de sahip içerikler

**Örnek 2 - Sadece Semantik:**
- Arama kutusu: "video düzenleme araçları"
- Sonuç: "Video", "montaj", "editor" içeren tüm benzer içerikler

**Örnek 3 - Hybrid:**
- Tag: ["AI"]
- Arama: "görsel oluşturma"
- Sonuç: AI etiketli ve semantik olarak "görsel oluşturma"ya yakın içerikler

---

## 📊 Veri Modeli

### bookmarks.json Örneği
```json
[
  {
    "id": 1,
    "title": "Runway Gen-3 Alpha",
    "url": "https://runwayml.com/gen-3",
    "description": "Yapay zeka ile video oluşturma, metinden videoya dönüştürme",
    "tags": ["AI", "Video", "Tool"],
    "date_added": "2025-12-04T02:16:54+03:00",
    "embedding": [0.123, -0.456, ...],
    "umap_coords": [1.23, -0.45, 2.67]
  },
  {
    "id": 2,
    "title": "ElevenLabs",
    "url": "https://elevenlabs.io",
    "description": "AI ile gerçekçi ses klonlama ve text-to-speech",
    "tags": ["AI", "Ses", "Tool"],
    "date_added": "2025-12-04T02:20:15+03:00",
    "embedding": [0.234, -0.567, ...],
    "umap_coords": [1.45, -0.52, 2.58]
  }
]
```

> **Not**: `embedding` ve `umap_coords` alanları sistem tarafından otomatik oluşturulur.

---

## 🎨 Kullanım Senaryoları

### Senaryo 1: "Buna benzer toollar var mı?"
**Durum**: "AI ses değiştirici" eklemiştin, buna benzer başka araç aramak istiyorsun.

**Çözüm**:
1. **3D Galaksi** sekmesine git
2. "AI Ses Değiştirici" noktasına yakın noktalara bak
3. Veya **Arama** sekmesinde: "ses değiştirme ai"

### Senaryo 2: "AI + Video kombinasyonu"
**Durum**: Hem AI hem video ile ilgili araçları görmek istiyorsun.

**Çözüm**:
1. **Liste** sekmesinde tag filtresi: ["AI", "Video"]
2. Veya **Arama**: Tag ["AI", "Video"] seç

### Senaryo 3: "Ne olduğunu hatırlamıyorum"
**Durum**: "Müzikle alakalı bir şeydi ama adını unuttum"

**Çözüm**:
1. **Arama** sekmesi
2. Arama kutusu: "müzik yapma"
3. Sistem semantik benzerliğe göre tüm müzik araçlarını getirir

---

## 🧪 Örnek Veri Seti

İlk denemeler için örnek veri:

```bash
# data/sample_bookmarks.json oluştur
python scripts/generate_sample_data.py
```

10 örnek AI/ses/video aracı ekler:
- Runway Gen-3 (AI video)
- ElevenLabs (AI ses)
- Midjourney (AI görsel)
- CapCut (video editing)
- Audacity (ses editing)
- vb.

---

## 🔧 Yapılandırma

### UMAP Parametreleri

`src/embedding_engine.py` içinde:

```python
umap_model = umap.UMAP(
    n_components=3,        # 3D çıktı
    n_neighbors=15,        # Komşu sayısı (↑ = daha global, ↓ = daha lokal)
    min_dist=0.1,          # Minimum nokta mesafesi (↑ = dağınık, ↓ = sıkışık)
    metric='cosine',       # Vektör benzerlik metriği
    random_state=42        # Tekrarlanabilirlik için (kaldırılabilir)
)
```

### Embedding Modeli

Farklı diller için model değiştirilebilir:

```python
# İngilizce (default)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Çok dilli (Türkçe dahil, ama daha yavaş)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

---

## 📈 Performans

### Hesaplama Süreleri (1000 veri için)

| İşlem | Süre | CPU/GPU |
|-------|------|---------|
| Embedding oluşturma | ~2-3 saniye | CPU |
| UMAP hesaplama | ~1-2 saniye | CPU |
| Plotly render | ~0.5 saniye | Browser |
| Semantic search query | ~0.1 saniye | CPU |
| **TOPLAM (yeni veri ekleme)** | **~4-6 saniye** | - |

**Optimizasyon İpuçları**:
- Streamlit `@st.cache_data` kullan (otomatik)
- Batch ekleme yap (5-10 veri birden)
- UMAP random_state sabitle (aynı veri = aynı harita)

---

## 🗺️ Roadmap

### ✅ Tamamlanan
- [x] Temel veri modeli
- [x] ML pipeline (embeddings + UMAP)
- [x] Streamlit arayüzü
- [x] 3D görselleştirme
- [x] Tag filtresi
- [x] Semantik arama
- [x] Hybrid search

### 🚧 Öncelikli (Faz 1.5)
- [ ] CRUD işlemleri (edit, delete)
- [ ] Export/Import (CSV, JSON)
- [ ] Favoriler sistemi
- [ ] Notlar ekleme
- [ ] Dark mode

### 🔮 Gelecek (Faz 2)
- [ ] Web deployment (Next.js + FastAPI)
- [ ] Three.js görselleştirme
- [ ] PostgreSQL + pgvector entegrasyonu
- [ ] Mobil responsive tasarım
- [ ] PWA (offline kullanım)
- [ ] Otomatik URL scraping
- [ ] Browser extension
- [ ] Collaborative mode (çoklu kullanıcı)

---

## 🤝 Katkıda Bulunma

Proje açık kaynak değil ama öneri/hata bildirimi için:

1. Issue aç
2. Detaylı açıklama yaz
3. Ekran görüntüsü ekle (varsa)

---

## 📝 Lisans

**Kişisel kullanım** için tasarlandı. Ticari kullanım için iletişime geçin.

---

## 🙏 Teşekkürler

Bu proje şu harika kütüphaneler sayesinde mümkün:

- [sentence-transformers](https://www.sbert.net/) - NLP embeddings
- [UMAP](https://umap-learn.readthedocs.io/) - Dimensionality reduction
- [Streamlit](https://streamlit.io/) - Web framework
- [Plotly](https://plotly.com/) - 3D visualization

---

## 📧 İletişim

Sorular için: [GitHub Issues]

---

<div align="center">

**Yapım aşamasında** 🚧

İlk stable release için [Faz 1.5]'i takip edin.

</div>
