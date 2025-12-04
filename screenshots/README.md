# 📸 Semantic Galaxy - Ekran Görüntüleri

> **Versiyon**: v0.8.1  
> **Tarih**: 5 Aralık 2025

## 🎯 Uygulama Özellikleri

### 1️⃣ Ana Arama Ekranı
![Ana Arama](01_main_search.png)

**Özellikler:**
- Akıllı semantik arama çubuğu
- Arama sonuçları st.info kutularında
- Tag badge'leri ile kategorileme
- Progress bar ile skor gösterimi
- "Daha Fazla Göster" pagination butonu

---

### 2️⃣ "Kendimi Şanslı Hissediyorum" Butonu
![Şanslı Buton](02_lucky_button.png)

**Özellikler:**
- Rastgele bookmark keşfi (Google tarzı)
- Seçilen içeriğin başlığı arama kutusuna otomatik yazar
- Semantik olarak benzer içerikleri gösterir
- Session state ile kalıcı seçim
- Serendipity (şansa dayalı keşif) deneyimi

---

### 3️⃣ 3D Semantik Galaksi
![3D Galaksi](03_galaxy_3d.png)

**Özellikler:**
- Plotly ile interaktif 3D scatter plot
- x, y, z konumları UMAP ile hesaplanır
- Renkler tag'lere göre kategorik
- Hover ile bookmark detayları
- Dark mode tema
- Filtreli görselleştirme (sidebar tag seçimiyle)

**Teknik:**
- SentenceTransformer (all-MiniLM-L6-v2)
- UMAP dimension reduction (384D → 3D)
- Tag-aware embeddings (Açıklama + Tags combined)

---

### 4️⃣ Veri Yönetimi (CRUD)
![Veri Yönetimi](04_data_management.png)

**Özellikler:**
- Excel-like st.data_editor
- Inline düzenleme (her hücre editlenebilir)
- Checkbox ile toplu/tekli silme
- Otomatik tag normalizasyonu
- Boş değer validasyonu
- Kaydet butonu ile CSV'ye yazar

---

### 5️⃣ Analiz & Word Cloud
![Analytics](05_analytics.png)

**Özellikler:**
- Word Cloud (Tagler veya Açıklamalar)
- Türkçe stopwords temizliği
- Top 10 Pie Chart (Donut style)
- Top 10 Bar Chart (Horizontal)
- 2 kolonlu layout
- Dark mode uyumlu renkler (turbo colormap)
- Memory leak fix (plt.close)

**Analiz Kaynağı Seçimi:**
- 📊 Etiketler: Genel kategorileri gösterir
- 📝 Açıklamalar: İçerik detaylarını analiz eder

---

## 🎨 Tasarım Prensipleri

1. **Dark Mode First**: Tüm UI dark mode optimize
2. **Minimalist**: Gereksiz elementler yok, sade ve temiz
3. **Türkçe Öncelikli**: Arayüz tamamen Türkçe
4. **Streamlit Native**: Platform'un güçlü yanlarını kullanır
5. **Performans**: Cache'leme ile hızlı (embeddings, stopwords, tag cleaning)

---

## 🚀 Kullanılan Teknolojiler

**Frontend:**
- Streamlit 1.30.0
- Plotly 5.18.0 (3D grafik, charts)
- Matplotlib 3.8.2 + WordCloud 1.9.3

**Backend/ML:**
- SentenceTransformer 2.2.2 (all-MiniLM-L6-v2)
- UMAP 0.5.5 (dimension reduction)
- Scikit-learn 1.3.2 (cosine similarity)

**Data:**
- Pandas 2.1.4
- CSV persistence
- Session state management

---

## 📊 Demo Akışı

Bu ekran görüntüleri şu user flow'u gösterir:

1. **Arama** → Kullanıcı "ai" diye arar
2. **Şanslıyım** → Rastgele bir bookmark seçer, benzerlerini gösterir
3. **3D Galaksi** → Tüm bookmark'lar semantic space'te görselleştirilir
4. **Veri Yönetimi** → Kullanıcı yeni kayıt ekler veya mevcutları düzenler
5. **Analiz** → En çok kullanılan tagleri ve kelimeleri görür

---

**🎉 Tüm özellikler production-ready!**  
**Sonraki Adımlar:** [FUTURISTIC_UPDATES_2025.md](../FUTURISTIC_UPDATES_2025.md)
