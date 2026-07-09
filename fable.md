# 🔍 Semantic Galaxy — Genel Proje Değerlendirme Raporu

> Bu rapor, projenin mevcut durumunun (v0.8.1) bağımsız bir teknik incelemesidir.
> Kapsam: kod kalitesi, mimari, ML pipeline, deploy durumu ve CV/portfolyo perspektifi.
> Tarih: 2026-07-09 · İnceleyen: Claude (Fable 5)

---

## 1. Özet Değerlendirme

**Genel not: 7/10 — Hobi projesi olarak başarılı, portfolyo projesi olarak umut verici, birkaç kritik eksikle.**

Semantic Galaxy; sentence-transformers → UMAP → Plotly 3D zincirini uçtan uca çalıştıran,
Streamlit Cloud'da canlı yayında olan, gerçek bir problemi (kaydedip unutma) çözen bir uygulama.
Tek dosyalık bir Streamlit uygulaması için özellik yoğunluğu etkileyici: semantik arama,
hibrit tag filtresi (AND/OR), embedding tabanlı tag önerisi, 3D görselleştirme, CRUD editör,
yedekleme/geri yükleme, word cloud analitiği ve pagination.

En büyük güçlü yanı **fikir ve dokümantasyon kültürü**, en büyük zayıflığı ise
**mimari (tek dosya + CSV) ve deploy'daki veri kalıcılığı sorunu**.

---

## 2. 👍 İyi Yapılan Şeyler

### 2.1 Uçtan uca çalışan ML pipeline
Embedding üretimi, boyut indirgeme (UMAP 384D→3D), benzerlik hesabı ve görselleştirme
tek akışta ve gerçekten çalışıyor. Çoğu hobi projesi "model yükledim, print ettim"
seviyesinde kalır; burada ML çıktısı gerçek bir UX'e bağlanmış.

### 2.2 Akıllıca UX dokunuşları
- **✨ Tag Öner**: Açıklamanın embedding'ini mevcut tag'lerle karşılaştırıp öneri yapmak
  basit ama zekice bir özellik — projenin en özgün fikirlerinden.
- **🎲 Şanslıyım**: Rastgele seçilen kaydın *açıklamasıyla* arama yaparak "benzerlerini de göster"
  davranışı — düşünülmüş bir detay.
- Pagination (`Daha Fazla Göster`), toast bildirimleri, benzerlik skoru progress bar'ları,
  form temizleme (session_state ile) — hepsi kullanıcı deneyimini önemseyen dokunuşlar.

### 2.3 Doğru Streamlit pratikleri
- `@st.cache_resource` ile model, `@st.cache_data` ile embedding cache'i doğru ayrılmış.
- Veri değişince `process_embeddings.clear()` ile cache invalidation yapılıyor — bu detayı
  çoğu Streamlit geliştiricisi atlar.
- `n_neighbors = min(15, len(df)-1)` gibi küçük veri setine karşı savunma kodları var.

### 2.4 Dokümantasyon ve süreç disiplini
- README rozetli, ekran görüntülü, problem-çözüm anlatımlı — portfolyo için doğru format.
- Conventional Commits kullanımı (`feat:`, `fix:`, `perf:`) tutarlı.
- FUTURE_VISION, FUTURISTIC_UPDATES, IMPLEMENTATION_PLAN gibi dosyalarda ürün düşüncesi var:
  N-gram analizi, boşluk analizi, Instagram hibrit import fikri gibi gerçekten özgün fikirler
  yazıya dökülmüş. Bu, "kod yazan" ile "ürün düşünen" geliştirici arasındaki farkı gösterir.

### 2.5 Veri hijyeni
Tag normalizasyonu (lowercase, sort, dedup), NaN kontrolü, CSV import'ta kolon validasyonu,
boş başlık/açıklama engelleme — küçük ama olgun detaylar.

---

## 3. 👎 Sorunlu / Zayıf Yerler

### 3.1 🔴 KRİTİK: Streamlit Cloud'da veri kalıcı değil
Uygulama veriyi yerel `data.csv`'ye yazıyor. Streamlit Cloud'un dosya sistemi **geçicidir**:
uygulama uyuyup uyandığında veya yeniden deploy olduğunda **UI'dan eklenen tüm kayıtlar silinir**,
repo'daki CSV'ye geri döner. Yani canlı demo'da "Kaydet" butonu aslında kalıcı çalışmıyor.
Ayrıca uygulama herkese açık ve auth yok — **herhangi bir ziyaretçi tüm veritabanını silebilir**
(Veri Yönetimi sekmesi + yedekten yükleme herkese açık).

### 3.2 🔴 Model seçimi Türkçe veriyle uyumsuz
`all-MiniLM-L6-v2` ağırlıklı olarak **İngilizce** eğitilmiş bir model; veri setindeki açıklamalar
ise çoğunlukla Türkçe. Bu, semantik aramanın kalitesini ciddi düşürür — "müzik yapan robotlar"
gibi Türkçe sorgular İngilizce modelde zayıf temsil edilir. Çok dilli bir model
(`paraphrase-multilingual-MiniLM-L12-v2` veya `distiluse-base-multilingual-cased-v1`)
tek satırlık değişiklikle arama kalitesini gözle görülür şekilde artırır.

### 3.3 🟠 "Cosine similarity" aslında cosine değil
README cosine similarity diyor ama kod ham `np.dot()` kullanıyor ve `model.encode()`
varsayılan olarak **normalize edilmemiş** vektör döndürür. Yani skor, vektör uzunluğundan
etkileniyor — uzun açıklamalı kayıtlar haksız avantaj/dezavantaj alabiliyor.
Çözüm tek parametre: `model.encode(..., normalize_embeddings=True)`.

### 3.4 🟠 Tek dosyada 400 satır — mimari yok
`app.py` içinde veri katmanı, ML pipeline ve UI iç içe. Bu boyutta hâlâ yönetilebilir ama
roadmap'teki özellikler (LLM, FastAPI, Telegram bot) eklendikçe sürdürülemez hale gelir.
Test yazmayı da imkânsızlaştırıyor çünkü hiçbir mantık import edilebilir değil.

### 3.5 🟠 Her veri değişiminde her şey yeniden hesaplanıyor
Bir kayıt eklemek, **tüm** veri setinin embedding'ini ve UMAP projeksiyonunu sıfırdan
hesaplatıyor. 13 kayıtta sorun değil; 500+ kayıtta her ekleme 10+ saniye bekletir.
Ayrıca UMAP her seferinde yeniden fit edildiği için galaksi haritası her ekleme sonrası
tamamen değişiyor — kullanıcının uzamsal hafızası ("AI köşesi şuradaydı") her seferinde sıfırlanıyor.

### 3.6 🟡 Küçük kod sorunları
- `clean_tags` üzerinde `@st.cache_data` gereksiz — string işlemi cache maliyetinden ucuz.
- `load_stopwords` içinde çıplak `except:` — hatayı yutar, teşhisi zorlaştırır.
- Skor normalizasyonu (`min_s`, `max_s`) tüm sonuç kümesi yerine sadece görünen sayfa
  (`head(limit)`) üzerinden hesaplanıyor — "Daha Fazla Göster" dedikçe bar oranları kayar.
- 3D grafikte renk `Tags` string'inin tamamına göre: `"ai, ses"` ve `"ai, görsel"` ayrı renk.
  Tag sayısı arttıkça legend patlar; ilk tag'e veya cluster'a göre renklendirme daha doğru.
- `requirements.txt`'te bir paket `>=` diğerleri `==` — tekrarlanabilir build garanti değil.
- Hiç test, linter, CI yok. Type hint ve docstring yok.
- Repo adındaki yazım hatası: "**Sematic**GalaxyContext" → "Semantic". CV'de göze batar;
  README başlıkta doğru yazıldığı için tutarsızlık da yaratıyor.

---

## 4. 💡 Önerilen İyileştirmeler (Öncelik Sırasıyla)

### Hemen yapılabilir (1-2 saat, yüksek etki)
| # | İyileştirme | Etki |
|---|---|---|
| 1 | `normalize_embeddings=True` ekle | Arama skorları matematiksel olarak doğru olur |
| 2 | Çok dilli modele geç (`paraphrase-multilingual-MiniLM-L12-v2`) | Türkçe arama kalitesi ciddi artar |
| 3 | README'ye "demo verisi kalıcı değildir" notu + Veri Yönetimi'ne basit parola (`st.secrets`) | Canlı demo'nun herkes tarafından silinmesini önler |
| 4 | Tüm sürümleri sabitle, `except:` → `except OSError:` | Tekrarlanabilirlik + teşhis edilebilirlik |

### Orta vade (CV değerini asıl artıracak işler)
1. **Modülerleştirme**: `src/data.py` (CSV/DB katmanı), `src/engine.py` (embedding+arama),
   `app.py` (sadece UI). Bu tek başına projeyi "script" görünümünden "yazılım" görünümüne taşır.
2. **SQLite'a geçiş**: CSV yerine tek dosyalık SQLite — eşzamanlılık, tip güvenliği ve
   embedding'leri BLOB olarak saklayıp **artımlı hesaplama** (sadece yeni kaydın vektörünü üret) kapısını açar.
3. **Test + CI**: `clean_tags`, tag filtreleme, arama sıralaması için pytest testleri +
   GitHub Actions'da ruff + pytest badge'i. İşe alım gözünden en güçlü sinyallerden biri.
4. **Cluster tabanlı renklendirme**: HDBSCAN/KMeans ile otomatik konu kümeleri; 3D haritada
   renk = küme. Roadmap'teki "boşluk analizi" fikrinin de temelini oluşturur.
5. **İngilizce README** (veya iki dilli): Uluslararası başvurular için şart.

### Uzun vade (roadmap'le uyumlu)
- FastAPI backend + Telegram share bot (FUTURISTIC_UPDATES'te zaten planlanmış — plan sağlam).
- URL'den otomatik metadata çekme (başlık/açıklama otomatik dolsun).
- LLM ile otomatik açıklama zenginleştirme ve tag üretimi.

---

## 5. 🎓 CV / Portfolyo Perspektifi

**Bu proje CV'de anlatmaya değer** — çünkü şu hikâyeyi taşıyor:
*"Kişisel bir problemimi tanımladım, NLP/embedding teknolojisiyle çözdüm, buluta deploy ettim,
sürüm sürüm geliştirdim ve yol haritasını belgeledim."* Bu, junior/mid seviye için güçlü bir anlatı.

CV'de vurgulanması gerekenler:
- Semantik arama + embedding tabanlı tag önerisi (asıl teknik derinlik burada)
- UMAP ile 384 boyuttan 3D'ye interaktif görselleştirme
- Canlı deploy linki + ekran görüntüleri

Mülakatta gelecek muhtemel sorulara hazırlıklı olunmalı:
- "Neden CSV? Neden SQLite değil?" → dürüst cevap: MVP hızı; roadmap'te geçiş planı var demek yeterli.
- "Türkçe veriyle İngilizce model?" → bu rapordaki 3.2 maddesi sorulmadan düzeltilmiş olursa çok daha iyi.
- "Test nerede?" → en zayıf nokta; küçük bir test paketi bile eklemek bu soruyu kapatır.

**Sonuç**: Mevcut haliyle "ilginç hobi projesi". Modülerleştirme + testler + çok dilli model +
kalıcılık düzeltmesiyle "işe alım görüşmesi ayarlatan portfolyo projesi" olur. Aradaki mesafe
yaklaşık 2-3 hafta sonu çalışması.
