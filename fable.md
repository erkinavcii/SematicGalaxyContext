# 🔍 Semantic Galaxy — Fable Raporu (Yürütülebilir Format)

> **Bu raporun amacı**: Daha ucuz/zayıf bir model (veya proje sahibi) bu dosyayı tek başına
> okuyup, başka hiçbir bağlama ihtiyaç duymadan Backlog'daki görevleri uygulayabilsin.
> Yargı (mimari seçimler, öncelikler) bu raporda verilmiştir; görevler sadece icra gerektirir.
>
> **Rapor tarihi**: 2026-07-09 · **İnceleyen**: Claude (Fable 5)
> **Analiz edilen durum**: commit `14aee84` · **Quick-win'ler sonrası durum**: commit `487258d`
> ⚠️ Backlog'daki satır numaraları `487258d` anına aittir; dosya değiştiyse fonksiyon adına göre bul.

---

## 1. Snapshot

**Genel not: 7/10** — Uçtan uca çalışan ML pipeline'lı (sentence-transformers → UMAP → Plotly 3D),
Streamlit Cloud'da canlı, tek dosyalık (`app.py`, ~410 satır) bookmark yönetim uygulaması.

**Yığın**: Python 3.10 (deploy) / 3.11 (lokal venv), Streamlit, pandas, sentence-transformers 5.x (venv),
umap-learn, Plotly, WordCloud. Depolama: `data.csv` (repo içinde).

**Güçlü**: embedding tabanlı tag önerisi, hibrit arama (tag AND/OR + semantik), cache yönetimi,
CRUD editör, yedekleme, conventional commits, ekran görüntülü README.

**Zayıf**: tek dosya mimarisi, CSV depolama, test/CI yok, canlı demoda auth yok
(herkes veri silebilir), her veri değişiminde tüm embeddings + UMAP yeniden hesaplanıyor.

**Bilinen ortam sorunu (lokal makine)**: Bu bilgisayarda huggingface.co'ya SSL doğrulamalı erişim
engelli (`CERTIFICATE_VERIFY_FAILED`, muhtemelen ağ/proxy TLS araya girmesi). Yeni model lokalde
indirilemez; kodda `local_files_only` fallback var, uygulama cache'teki modelle çalışır.
Streamlit Cloud'da sorun yok. Kalıcı çözüm: farklı ağda bir kez
`python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"`
çalıştırıp modeli cache'e almak.
> **Güncelleme 2026-09-14**: Sorun geçiciymiş; aynı makineden huggingface.co model dosyası uç noktası 200 döndü.
> Yukarıdaki komut artık bu makinede de çalışmalı (~470MB indirir).

---

## 2. Hemen Uygulandı ✅

Bu düzeltmeler rapor yazılırken uygulandı, doğrulandı ve commit'lendi:

| Değişiklik | Commit | Doğrulama |
|---|---|---|
| Çok dilli modele geçiş (`paraphrase-multilingual-MiniLM-L12-v2`) + indirilemezse cache'teki `all-MiniLM-L6-v2`'ye `local_files_only=True` fallback | `07e9771` | Fallback lokalde tetiklenip model yüklendi; AppTest ile uygulama 0 exception ile çalıştı |
| Tüm `model.encode` çağrılarına `normalize_embeddings=True` — yeni modelde `np.dot` skorunun kosinüs olması için şart | `07e9771` | Vektör normları 1.0000 ölçüldü |
| Benzerlik bar normalizasyonu sayfa dilimi (`results`) yerine tüm sonuç kümesi (`display_df`) üzerinden — "Daha Fazla Göster" dedikçe barlar kaymaz | `07e9771` | Kod incelemesi |
| `load_stopwords` içindeki çıplak `except:` → `except OSError:` | `07e9771` | Kod incelemesi |
| README: model bilgisi güncellendi + "demo verisi kalıcı değildir" uyarısı eklendi | `487258d` | — |

> **Düzeltme (2026-09-14)**: İlk raporda "eski kod kosinüs hesaplamıyordu" denmişti; **yanlıştı**. Eski
> `all-MiniLM-L6-v2` modelinin `modules.json`'unda `Normalize` katmanı var (normalize parametresi olmadan da
> normlar 1.0 ölçüldü). Yeni `paraphrase-multilingual-MiniLM-L12-v2`'de bu katman **yok**; bu yüzden değişiklik
> yeni model için gerekliydi. Commit `07e9771` mesajındaki gerekçe de bu açıdan eksik.
>
> **Canlı doğrulama (2026-09-14)**: Streamlit Cloud demosu (GitHub `master`'dan otomatik deploy) uykudan
> uyandırıldı; yeni modelle hatasız açıldı, yedek model uyarısı çıkmadı, "bilgisayar oyunu yapmak istiyorum"
> araması Unreal Engine (0.66) ve Unity (0.64) sonuçlarını getirdi.
>
> **Not**: Streamlit Cloud ilk deploy'da yeni modeli (~470MB) indirecek; ilk açılış birkaç dakika
> sürebilir, sonrası normaldir. Model 384D çıktı verdiği için UMAP/arama kodu değişikliği gerekmedi.

---

## 3. Uygulanabilir Backlog

Görevler **bağımlılık sırasına** göredir. Her görev kendi kendine yeter.

---

### Görev 1: Canlı demoya yönetici parolası

- **Neden**: Uygulama herkese açık; herhangi bir ziyaretçi Veri Yönetimi sekmesinden tüm veriyi
  silebilir veya yedekten yükleme ile üzerine yazabilir. En acil güvenlik açığı bu.
- **Bağımlılık**: yok
- **Adımlar**:
  1. `app.py` içinde `DATA_FILE = "data.csv"` satırının (satır ~60) hemen altına ekle:
     ```python
     def secret(key, default=""):
         # Streamlit 1.30: secrets.toml yokken st.secrets erişimi FileNotFoundError fırlatır (2026-09-14'te doğrulandı)
         try:
             return st.secrets.get(key, default)
         except FileNotFoundError:
             return default

     def is_admin():
         # Parola tanımlı değilse (lokal kullanım) herkes admindir
         expected = secret("admin_password")
         if not expected:
             return True
         entered = st.session_state.get("admin_pw_input", "")
         return entered == expected
     ```
  2. Sidebar'da `st.header("🏷️ Filtrele")` satırının üstüne ekle:
     ```python
     if secret("admin_password"):
         st.text_input("🔑 Yönetici Parolası", type="password", key="admin_pw_input")
     ```
  3. Şu üç yazma noktasını `if not is_admin(): st.error("Bu işlem için yönetici parolası gerekli."); st.stop()` benzeri korumayla sarmala (buton bloklarının en başına koy):
     - `if st.button("Kaydet"):` bloğu (satır ~158)
     - `uploaded_file is not None` bloğu (satır ~182 sonrası)
     - `if st.button("💾 Değişiklikleri Kaydet"):` bloğu (satır ~339)
  4. Streamlit Cloud → App settings → Secrets kısmına `admin_password = "GÜÇLÜ_BİR_PAROLA"` ekle.
     Lokalde `.streamlit/secrets.toml` **git'e commit etme** (zaten .gitignore'da).
- **Kabul kriteri**: Parola secrets'ta tanımlıyken parolasız "Kaydet" hata verip durmalı;
  doğru parola girilince kayıt çalışmalı. Lokalde (secrets yokken) her şey eskisi gibi çalışmalı.
- **Süre**: 30-45 dk

---

### Görev 2: Modülerleştirme (UI / veri / ML katmanlarını ayır)

- **Neden**: 410 satırlık tek dosya test yazmayı imkânsız kılıyor ve roadmap'teki her özellik
  (FastAPI, Telegram bot, LLM) bu ayrımı gerektiriyor. Sonraki tüm görevlerin temeli.
- **Bağımlılık**: Görev 1'den sonra (aynı dosyada çakışma olmasın)
- **Adımlar**:
  1. `src/` klasörü oluştur, içine boş `__init__.py` koy.
  2. `src/data.py` oluştur — `app.py`'den şunları **aynen taşı** (streamlit import'u OLMASIN):
     `clean_tags` (st.cache_data dekoratörünü SİL, gerek yok), `get_unique_tags`,
     `load_stopwords` (st.cache_data'yı sil), `DATA_FILE`, `load_data`.
     **Tek istisna, bilinen hatayı taşırken düzelt**: `clean_tags("ai, , ses")` şu an `", ai, ses"` döndürüyor.
     `tags = [t.strip().lower() for t in tag_str.split(',')]` → `tags = [t.strip().lower() for t in tag_str.split(',') if t.strip()]`
     ve sonuç boş kalırsa `"genel"` döndür.
  3. `src/engine.py` oluştur — şunları taşı: `load_model` içindeki model yükleme mantığı
     (`get_model()` adıyla, st.warning yerine `logging.warning` + fallback aynı kalsın),
     `process_embeddings`'in gövdesi (`compute_embeddings(df, model)` adıyla, cache dekoratörsüz),
     tag önerisi mantığı (`suggest_tags(desc, existing_tags, model) -> list[str]` fonksiyonu olarak),
     benzerlik hesabı (`search_scores(embeddings, query_vec) -> np.ndarray`).
  4. `app.py`'de cache'i sarmalayıcı olarak tut:
     ```python
     from src import data, engine

     @st.cache_resource
     def load_model():
         return engine.get_model()

     @st.cache_data
     def process_embeddings(df):
         return engine.compute_embeddings(df, model)
     ```
     Geri kalan UI kodu aynen kalır, sadece fonksiyon çağrıları `data.clean_tags(...)` gibi olur.
  5. Davranış DEĞİŞMEMELİ — bu görev saf taşımadır, mantık düzeltmesi yapma.
- **Kabul kriteri**: `streamlit run app.py` açılmalı; arama, tag önerisi, kayıt ekleme,
  3D grafik ve analiz sekmesi eskisi gibi çalışmalı. `python -c "from src import data, engine"`
  streamlit YÜKLÜ OLMAYAN bir ortamda bile hata vermemeli (data.py için).
- **Süre**: 45-60 dk

---

### Görev 3: pytest testleri + GitHub Actions CI

- **Neden**: CV'ye "test edilmiş, CI'lı proje" sinyali işe alım gözünden en güçlü farklardan biri;
  ayrıca sonraki refactor'ları (SQLite) güvenle yapmayı sağlar.
- **Bağımlılık**: Görev 2 (import edilebilir modüller gerekli)
- **Adımlar**:
  1. `tests/test_data.py` oluştur:
     ```python
     from src.data import clean_tags, get_unique_tags
     import pandas as pd

     def test_clean_tags_normalizes():
         assert clean_tags("  AI , ses, AI ") == "ai, ses"
         assert clean_tags("ai, , ses") == "ai, ses"
         assert clean_tags(" , ") == "genel"

     def test_clean_tags_empty_returns_genel():
         assert clean_tags("") == "genel"
         assert clean_tags(None) == "genel"
         assert clean_tags("nan") == "genel"

     def test_get_unique_tags():
         df = pd.DataFrame({"Tags": ["ai, ses", "ai, kod", None]})
         assert get_unique_tags(df) == ["ai", "kod", "ses"]
     ```
  2. `tests/test_engine.py` oluştur — model indirmeden test et (embedding'i mock'la ya da
     sadece saf fonksiyonları test et): `search_scores`'a elle verilmiş küçük numpy dizileriyle
     sıralamanın doğru çıktığını doğrula.
  3. `requirements-dev.txt`: `pytest`, `ruff`.
  4. `.github/workflows/ci.yml`:
     ```yaml
     name: CI
     on: [push, pull_request]
     jobs:
       test:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v4
           - uses: actions/setup-python@v5
             with: { python-version: "3.11" }
           - run: pip install pandas numpy pytest ruff
           - run: ruff check src/ tests/
           - run: pytest tests/ -v
     ```
     (Bilinçli karar: CI'da sentence-transformers/umap KURMA — ağır; sadece saf mantık test edilir.)
  5. README'ye CI badge ekle: `![CI](https://github.com/erkinavcii/SematicGalaxyContext/actions/workflows/ci.yml/badge.svg)`
- **Kabul kriteri**: Lokalde `pytest tests/ -v` yeşil; GitHub'da Actions sekmesinde workflow yeşil.
- **Süre**: 45-60 dk

---

### Görev 4: CSV → SQLite geçişi

> ⚠️ **2026-09-14 revizyonu**: `PLAN_ETKILESIM.md` Faz 2 (Telegram botu) uygulanacaksa bu görevi **ATLA**.
> Bot ve Streamlit farklı süreçlerde çalışacağı için yerel SQLite paylaşılamaz; yerine PLAN_ETKILESIM.md
> P2.1-P2.3 (Supabase) uygulanır. Gerekçe: PLAN_ETKILESIM.md K3-K4. Faz 2 hiç yapılmayacaksa bu görev geçerlidir.

- **Neden**: Bilinçli karar — SQLite seçildi (Postgres değil: tek kullanıcı, sunucusuz, tek dosya;
  JSON değil: tip güvenliği + SQL sorgu gücü + embedding BLOB saklama imkânı).
  CSV'nin sorunları: eşzamanlı yazmada bozulma riski, tip kaybı, embedding saklayamama.
- **Bağımlılık**: Görev 2 ve 3 (veri katmanı izole ve test edilebilir olmalı)
- **Adımlar**:
  1. `src/data.py`'ye sqlite3 tabanlı katman ekle (`DB_FILE = "galaxy.db"`):
     ```sql
     CREATE TABLE IF NOT EXISTS bookmarks (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         baslik TEXT NOT NULL,
         link TEXT DEFAULT '',
         aciklama TEXT NOT NULL,
         tags TEXT DEFAULT 'genel',
         embedding BLOB,            -- np.float32 bytes; np.frombuffer ile geri okunur
         created_at TEXT DEFAULT (datetime('now'))
     );
     ```
  2. Fonksiyonlar: `init_db()`, `get_all() -> pd.DataFrame` (`pd.read_sql`),
     `add_bookmark(baslik, link, aciklama, tags, embedding: np.ndarray | None)`,
     `update_bookmarks(df)` (editör kaydı için: sil + toplu insert kabul edilebilir),
     `migrate_from_csv()` — `data.csv` varsa ve tablo boşsa satırları aktarır.
  3. Uygulama açılışında `init_db(); migrate_from_csv()` çağır. `data.csv`'yi repo'da bırak
     (ilk tohum verisi olarak), ama `galaxy.db`'yi `.gitignore`'a ekle.
  4. Yedekleme butonları çalışmaya devam etmeli: indirme `get_all().to_csv()`, yükleme ise
     CSV'yi okuyup tabloyu değiştirir.
- **Kabul kriteri**: Uygulama açılır, mevcut CSV verisi otomatik migrate olur, kayıt
  ekleme/silme/düzenleme çalışır, `pytest` yeşil kalır. `galaxy.db` git'e girmez.
- **Süre**: 60 dk (gerekirse "şema+migrasyon" ve "UI bağlama" diye ikiye böl)

---

### Görev 5: Artımlı embedding (her eklemede her şeyi yeniden hesaplama)

- **Neden**: Şu an 1 kayıt eklemek tüm veri setinin embedding'ini + UMAP'i sıfırdan hesaplatıyor;
  500+ kayıtta her ekleme 10+ saniye olur. Ayrıca UMAP her seferinde yeniden fit edildiği için
  harita tamamen değişiyor ve kullanıcının uzamsal hafızası sıfırlanıyor.
- **Bağımlılık**: Görev 4 (embedding'ler DB'de saklanabilmeli)
- **Adımlar**:
  1. `add_bookmark` çağrılırken sadece YENİ kaydın embedding'ini hesapla
     (`model.encode([aciklama + ". " + tags], normalize_embeddings=True)`) ve BLOB olarak yaz.
  2. `compute_embeddings` artık DB'den hazır embedding'leri okur; embedding'i NULL olan
     satırlar için (düzenlenmiş kayıtlar) yeniden hesaplayıp DB'ye geri yazar.
     Düzenleme kaydında değişen satırların embedding kolonunu NULL'a çek.
  3. UMAP: her açılışta yeniden fit etmek yerine fit edilmiş modeli `joblib.dump` ile
     `umap_model.joblib`'e kaydet; yeni kayıtları `umap_model.transform(new_embeddings)` ile
     mevcut haritaya yerleştir. Kayıt sayısı son fit'ten beri %20'den fazla arttıysa yeniden fit et
     (eşik bilinçli karar: harita stabilitesi vs güncellik dengesi). `umap_model.joblib` .gitignore'a.
- **Kabul kriteri**: Yeni kayıt eklemek 2 saniyeden kısa sürmeli (model yüklü haldeyken) ve
  mevcut noktaların 3D konumu değişmemeli. Kayıt düzenlenince araması güncel içeriğe göre çalışmalı.
- **Süre**: 60 dk

---

### Görev 6: 3D haritada küme tabanlı renklendirme

> ℹ️ `PLAN_ETKILESIM.md` P1.4 bu görevi kapsar (ana etiket + kaynak renk seçimi). P1.4 yapılacaksa bunu ayrıca yapma.

- **Neden**: Şu an renk `Tags` string'inin TAMAMINA göre: "ai, ses" ile "ai, görsel" ayrı renk
  alıyor; tag kombinasyonu arttıkça legend patlıyor. Bilinçli karar: KMeans yerine ilk adımda
  **ilk tag'e göre** renklendirme (basit, açıklanabilir); kümeleme ayrı bir "keşif" özelliği olarak sonra.
- **Bağımlılık**: yok (Görev 2 yapıldıysa `app.py`'deki 3D grafik bloğunda)
- **Adımlar**:
  1. 3D grafik bloğunda (`px.scatter_3d` çağrısından önce, `app.py` satır ~318 civarı) ekle:
     ```python
     plot_df = filtered_df.copy()
     plot_df['AnaEtiket'] = plot_df['Tags'].astype(str).str.split(',').str[0].str.strip()
     ```
  2. `px.scatter_3d(...)` çağrısında `filtered_df` → `plot_df`, `color='Tags'` → `color='AnaEtiket'`.
     `hover_data`'da `Tags: True` kalsın (tam etiketler hover'da görünmeye devam etsin).
- **Kabul kriteri**: Legend'da kombinasyonlar değil tekil ana etiketler görünmeli;
  hover'da tam tag listesi hâlâ görünmeli.
- **Süre**: 15 dk

---

### Görev 7: Sürümleri sabitle

- **Neden**: `sentence-transformers>=2.7.0` açık uçlu; deploy her seferinde farklı sürüm
  çekebilir ve bir gün sessizce kırılır. Bilinçli karar: Streamlit Cloud'un O AN kurduğu
  sürüme sabitle (tahmin etme).
- **Bağımlılık**: yok — ama Görev 1-6'dan SONRA yap ki sabitlenen ortam son halin olsun.
- **Adımlar**:
  1. Streamlit Cloud'da app'i aç → "Manage app" → loglardan kurulmuş sürümleri oku
     (veya app içine geçici `st.caption(sentence_transformers.__version__)` koyup oku, sonra sil).
  2. `requirements.txt`'te `sentence-transformers>=2.7.0` satırını okunan sürümle
     `sentence-transformers==X.Y.Z` olarak sabitle. Diğer paketler zaten sabit.
- **Kabul kriteri**: Reboot sonrası deploy loglarında tam o sürümün kurulduğu görünmeli, app açılmalı.
- **Süre**: 15 dk

---

### Görev 8: İngilizce README (iki dilli yapı)

- **Neden**: Uluslararası başvurularda Türkçe README engel. Bilinçli karar: Türkçe'yi silme,
  `README.md` İngilizce olsun (GitHub varsayılanı), Türkçe `README.tr.md`'ye taşınsın.
- **Bağımlılık**: yok (içerik değişiklikleri bittikten sonra en son yap)
- **Adımlar**:
  1. Mevcut `README.md`'yi `README.tr.md` olarak kopyala.
  2. `README.md`'yi İngilizce'ye çevir (aynı yapı: badges, screenshots, problem/solution,
     features, tech stack, setup). En üste dil linkleri: `🇬🇧 English | [🇹🇷 Türkçe](README.tr.md)`.
  3. Ekran görüntüsü yolları aynı kalır (`screenshots/`).
- **Kabul kriteri**: GitHub repo ana sayfası İngilizce açılmalı, TR link çalışmalı,
  tüm görseller iki dosyada da görünmeli.
- **Süre**: 45 dk

---

## Bilinçli olarak YAPILMAYACAKLAR (kararlar)

Executor bunları önerirse reddet — kararı verilmiş konulardır:
- ~~**Postgres/Supabase'e geçiş**: Tek kullanıcılı hobi projesi için aşırı; SQLite yeterli (Görev 4).~~
  **Revize edildi (2026-09-14)**: Bu karar tek süreçli kullanım varsayımına dayanıyordu. Telegram botuyla
  çok kanallı yakalama (PLAN_ETKILESIM.md Faz 2) başlarsa Supabase kullanılır (PLAN_ETKILESIM.md K4).
- **React/Next.js frontend**: Streamlit bu projenin ölçeği için doğru; yeniden yazım değer katmaz.
- **Repo adını değiştirmek** ("Sematic" yazım hatası): Canlı deploy URL'si ve CV linkleri kırılır;
  düzeltme maliyeti faydasından büyük. README'de doğru yazım ("Semantic Galaxy") zaten kullanılıyor.
- **CI'da tam ML pipeline testi**: sentence-transformers + umap kurulumu CI'ı 10+ dk'ya çıkarır;
  saf mantık testleri yeterli sinyal verir.
