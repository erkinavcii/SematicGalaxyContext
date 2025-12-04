---

# 🧠 Anlam Karşaması: İleri Seviye Anlamlandırma Vizyonu

> **Not**: Bu bölüm gelecek geliştirmeler için beyin fırtınası notlarıdır. 
> Mevcut MVP'de uygulanmamıştır, ancak roadmap için referans olarak saklanmıştır.

---

## 🎯 "Anlamlandırma" (Sense-making) Katmanları

Veri setimiz (Başlık, Link, Açıklama, Tagler) üzerinden hangi katmanlarda anlam çıkarabiliriz?

### 1️⃣ Frekans Analizi (Ne hakkında biriktiriyorum?)

**Basit Soru**: En çok hangi kelime geçiyor? (Örn: "AI")

**Derin Soru (N-Grams)**: Hangi kelime öbekleri yan yana geliyor?
- Sadece "Veri" kelimesi tek başına zayıftır
- "Veri Analizi" veya "Veri Görselleştirme" ise bir konsepttir
- **Fikir**: WordCloud yaparken sadece tek kelimeleri (unigram) değil, ikilileri (bigrams) de analiz edebiliriz

**Ayrışma**: Etiketlerim ile yazdığım açıklamalar uyuşuyor mu?
- Etikete "Yazılım" demişim ama açıklamada sürekli "Tasarım, Renk, UI" geçiyorsa
- Belki de o etiketi "Frontend" olarak güncellemeliyim

**Teknik İhtiyaç**:
- Türkçe Stop Words listesi (NLTK veya spaCy)
- N-Gram extraction (scikit-learn CountVectorizer)
- Tag-Description consistency checker

---

### 2️⃣ Eylem Odaklı Analiz (Ne yapmak istiyorum?)

Açıklamalardaki **fiillere** (verbs) odaklanmak.

**İçeriklerin genellikle ne işe yarıyor?**
- **Üretmek**: Generate, Create, Write
- **Yönetmek**: Manage, Organize, Store
- **Öğrenmek**: Learn, Course, Tutorial

**İçgörü**: 
> Eğer arşivinin %80'i "Üretmek" üzerineyse ama "Yönetmek" üzerine araç yoksa, 
> belki de üretkenlik sorununun kaynağı budur: Çok üretiyorsun ama yönetemiyorsun.

**Teknik İhtiyaç**:
- POS Tagging (Part-of-Speech)
- spaCy Türkçe model: `tr_core_news_lg`
- Verb extraction ve kategorileme

**Görselleştirme**:
- Pie Chart: Eylem dağılımı
- Radar Chart: Beceri haritası (Üretme vs Öğrenme vs Yönetme)

---

### 3️⃣ Boşluk Analizi (Neyim eksik?)

Var olanı değil, **olmayanı** bulmak.

**Tag'lerin birbirleriyle ilişkisine bakarak "köprüleri" veya "adaları" bulmak:**
- Örnek: "Yapay Zeka" kümen çok büyük, "Video" kümen çok büyük
- Ama ikisinin kesiştiği (AI + Video) alan boş mu?
- Oraya odaklanman gerekebilir

**Görselleştirme**:
- Pie Chart: Ana kategoriler
- Sunburst Chart: İç içe halkalar (hiyerarşik tag ilişkileri)
- Venn Diagram: Tag kesişimleri

**Teknik İhtiyaç**:
- Co-occurrence matrix (Tag kombinasyonları)
- Graph analysis (NetworkX)
- Plotly Sunburst Chart

---

### 4️⃣ Duygu/Kalite Analizi (Nitelik)

Bu biraz daha ileri seviye ama fikir olarak dursun.

**Açıklamaların dili nasıl?**
- **Nesnel mi?** "Bu araç ses kopyalar."
- **Öznel mi?** "Harika bir araç, çok hızlı çalışıyor."

Eğer açıklamalarına kendi yorumlarını da katıyorsan (Notion mantığı):
- "Pozitif" ve "Negatif" kelime bulutları oluşturulabilir
- Sentiment score: -1.0 (kötü) → +1.0 (iyi)
- "Bu kötü çalışıyor" vs "Mükemmel performans"

**Teknik İhtiyaç**:
- Sentiment Analysis library (TextBlob, VADER)
- Türkçe için: `zemberek-nlp` veya `turkish-sentiment`
- Dual Word Cloud (Positive/Negative)

---

## 🛠️ Somut Uygulama Önerileri

Bu beyin fırtınasından yola çıkarak, sıradaki kodlama adımlarında hedefler:

### 🔥 Öncelikli (Kolay Kazanımlar)

#### 1. Stop Words Temizliği (Şart)
**Sorun**: "Anlamlandırma"nın düşmanı gürültüdür.
- "ve, ile, bir, için, ama, fakat" gibi kelimeleri temizlemezsek analiz çöp olur

**Çözüm**:
```python
from nltk.corpus import stopwords
turkish_stopwords = stopwords.words('turkish')
# Veya manuel liste: ["ve", "ile", "bir", "için", ...]
```

**Ek**: İngilizce stop words da ekle (çünkü teknik terimler İngilizce)

---

#### 2. Kaynak Ayrımı (Radio Button)
Kullanıcıya soralım: "Neyin haritasını görmek istiyorsun?"

**Seçenekler**:
- **A) Etiketler** (Kuş bakışı): Genel kategorileri gösterir
- **B) Açıklamalar** (Derin bakış): İçerikteki gizli detayları (fiilleri, sıfatları) gösterir

```python
source = st.radio("Analiz Kaynağı:", ["Etiketler", "Açıklamalar"])
if source == "Etiketler":
    text = df['Tags'].str.cat(sep=' ')
else:
    text = df['Aciklama'].str.cat(sep=' ')
```

---

#### 3. Görsel Hiyerarşi
**Pie Chart**: Pastanın büyük dilimlerini (Ana Konuları) görmek için
- Plotly: `px.pie()`
- İnteraktif: Dilime tıklayınca detay

**Word Cloud**: Detaylardaki ince kelimeleri (Micro Konuları) keşfetmek için
- Şu an var ama stop words temizliği lazım

---

### 🟡 Orta Öncelik (Daha Gelişmiş)

#### 4. N-Grams Analizi
**Bigrams** (2'li kelime grupları):
- "veri analizi", "yapay zeka", "web tasarım"
- Daha anlamlı konseptler

**Trigrams** (3'lü kelime grupları):
- "makine öğrenmesi modeli", "kullanıcı arayüz tasarımı"

**Implementasyon**:
```python
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(ngram_range=(2, 2))  # Bigrams
bigrams = vectorizer.fit_transform(df['Aciklama'])
```

---

#### 5. Tag Consistency Checker
Etiketime "Backend" demişim ama açıklamada "Renk, Font, UI" geçiyor → Uyumsuzluk!

**Algoritma**:
1. Her tag için o tag'li içeriklerin açıklamalarını birleştir
2. TF-IDF ile en önemli kelimeleri bul
3. Tag adı ile top keywords'ü karşılaştır
4. Benzerlik düşükse → Uyarı ver

---

### 🟢 Düşük Öncelik (Araştırma Gerektir)

#### 6. Verb Extraction (Eylem Analizi)
spaCy ile fiil çıkarma:
```python
import spacy
nlp = spacy.load("tr_core_news_lg")  # Türkçe model

verbs = []
for desc in df['Aciklama']:
    doc = nlp(desc)
    verbs.extend([token.lemma_ for token in doc if token.pos_ == "VERB"])
```

**Kategorileme**:
- CREATE verbs: yapmak, üretmek, oluşturmak
- MANAGE verbs: yönetmek, düzenlemek, organize etmek
- LEARN verbs: öğrenmek, anlamak, keşfetmek

---

#### 7. Co-occurrence Network (İlişki Ağı)
Hangi tag'ler birlikte kullanılıyor?

**Görselleştirme**:
- NetworkX + Plotly
- Node: Her tag
- Edge: Birlikte kullanılma sıklığı (edge weight)
- Cluster detection: Modular tag grupları

---

#### 8. Sentiment Analysis (Duygu Analizi)
Açıklamalarımda kendi görüşlerimi de ekliyorsam:
- "Harika bir araç" → Pozitif
- "Karmaşık, anlaşılması zor" → Negatif

**Use Case**:
- Sevdiğim araçlar vs Zorlandığım araçlar
- İki ayrı word cloud

---

## 📊 Görselleştirme Roadmap

| Görsel | Amaç | Öncelik | Teknik |
|--------|------|---------|--------|
| **Word Cloud** | Mevcut ✅ | - | WordCloud lib |
| **Word Cloud (Stop Words cleaned)** | Temiz analiz | 🔴 Yüksek | NLTK stopwords |
| **Bigram Word Cloud** | Konseptler | 🟡 Orta | CountVectorizer |
| **Pie Chart (Tag Distribution)** | Genel dağılım | 🟡 Orta | Plotly pie |
| **Sunburst Chart (Tag Hierarchy)** | İç içe kategoriler | 🟢 Düşük | Plotly sunburst |
| **Verb Distribution Pie** | Eylem analizi | 🟢 Düşük | spaCy + Plotly |
| **Co-occurrence Network** | Tag ilişkileri | 🟢 Düşük | NetworkX |
| **Sentiment Dual Cloud** | Pozitif/Negatif | 🟢 Düşük | TextBlob |

---

## 💡 Tartışma Sorusu

> **Özellikle "Eylem Odaklı Analiz" (fiiller) veya "N-Grams" (kelime öbekleri) ilgini çekti mi, yoksa şimdilik temel frekans analizi (kelime sayımı) ile mi ilerleyelim?**

### Öneri: Kademeli Yaklaşım

**Faz 1** (Hemen yapılabilir):
1. Stop words temizliği ekle
2. Radio button: Tag vs Description seçimi
3. Pie chart ekle (tag dağılımı)

**Faz 2** (Sonraki sprint):
4. Bigrams word cloud
5. Tag consistency checker
6. Verb extraction

**Faz 3** (Araştırma projesi):
7. Co-occurrence network
8. Sentiment analysis
9. Sunburst chart

---

**Son Güncelleme**: 2025-12-04 21:50
**Durum**: Beyin fırtınası / Roadmap taslağı
**Kararlar**: TBD (To Be Decided)
