# CLAUDE.md — Semantic Galaxy

Kişisel "kaydet ve unutma" aracı: kaydedilen linkleri çok dilli embedding ile anlamlandırıp semantik arama,
3D galaksi (UMAP + Plotly) ve analizle sunan Streamlit uygulaması. CV/portfolyo projesi; herkese açık demo
Streamlit Cloud'da.

## Dokümanlar: hangisi geçerli?
1. `CLAUDE.md`: çalışma kuralları (bu dosya)
2. `PLAN_ETKILESIM.md`: özellik planı (Faz 1-5, K1-K8 kararları). Çelişkide en üstün plan dokümanı.
3. `fable.md`: teknik borç backlog'u (Görev 1-8)
4. `FUTURISTIC_UPDATES_2025.md`, `RoadmapAlternative2025.md`, `FUTURE_VISION.md`, `IMPLEMENTATION_PLAN.md`,
   `TASK_PROGRESS.md`, `PROJECT_CONTEXT.txt`: **arşiv / fikir havuzu**. Yukarıdakilerle çelişirse geçersizdir.

## Komutlar (Windows, repo kökünden)
```bash
venv/Scripts/python.exe -m streamlit run app.py
venv/Scripts/python.exe -m pytest tests/ -v
```
UI açmadan uçtan uca smoke test (değişiklikten sonra çalıştır, `exceptions: 0` beklenir):
```bash
venv/Scripts/python.exe -c "from streamlit.testing.v1 import AppTest; at=AppTest.from_file('app.py', default_timeout=300); at.run(); print('exceptions:', len(at.exception))"
```

## Mimari (şu an)
- Tek dosya `app.py`: model yükleme → `data.csv` → embedding + UMAP (`process_embeddings`, cache'li) →
  kenar çubuğu (filtre, ekleme, yedek) → 4 sekme (arama, galaksi, veri yönetimi, analiz).
- `data.csv` herkese açık demo verisidir; kişisel veri buraya commit'lenmez.
- Deploy: Streamlit Community Cloud, GitHub `master` dalına bağlı. **`master`'a her push canlı demoyu otomatik
  yeniden yayınlar** (README rozetindeki link, CV'de paylaşılan adres). Python 3.10 (`.python-version`),
  `requirements.txt`. Lokal venv Python 3.11, Streamlit 1.30.
- Demo ziyaret edilmeyince uykuya geçer; ilk açılış "Yes, get this app back up" butonu + 1-2 dk sürer.
- GitHub reposu herkese açık: commit'lenen her doküman (planlar dahil) herkes tarafından görülür.

## Kurallar
- **Embedding**: model `paraphrase-multilingual-MiniLM-L12-v2` (veri Türkçe). Her `model.encode` çağrısında
  `normalize_embeddings=True` olmalı; skorlar `np.dot` ile hesaplanıyor, normalize olmazsa kosinüs değildir.
- **Cache**: veriyi yazan her kod yolundan sonra `process_embeddings.clear()` (varsa `load_data.clear()`) + `st.rerun()`.
- **session_state**: widget çizildikten sonra aynı çalıştırmada key'ini değiştirme; `on_click` callback kullan.
- **`st.secrets`**: Streamlit 1.30'da `secrets.toml` yokken erişim `FileNotFoundError` fırlatır. Her zaman
  try/except'li yardımcıyla oku.
- **Veri kaybı**: CSV'ye sabit kolon listesiyle yaz; hesaplanmış kolonları (`x, y, z, Benzerlik`) yazma.
  Otomatik doldurma kullanıcının yazdığı başlık/açıklamayı asla ezmez.
- **Sosyal medya**: resmî oEmbed/API → OpenGraph → sadece link. Kullanıcının oturum çerezi, `yt-dlp`,
  giriş duvarını aşan scraping YOK (hesap ban riski).
- **Gizli bilgiler**: sadece `.streamlit/secrets.toml` ve `.env` (git dışı). Koda/commit'e asla.
- **Git**: Conventional Commits, Türkçe mesaj (`feat(arama): ...`). Sadece kendi değiştirdiğin dosyaları
  stage'le (`git add <dosya>`, `git add -A` değil); commit'lenmemiş başka değişiklikler proje sahibine ait olabilir.
- **Canlıya çıkış**: Kod değiştiren görevler (`app.py`, `src/`, `requirements.txt`) `gelistirme` dalında yapılır.
  Kabul kriteri + smoke test geçince `master`'a birleştirilir. Push'tan sonra demo linki açılıp çalıştığı
  kontrol edilir. Sadece doküman değişiklikleri doğrudan `master`'a gidebilir. `master`'a push proje sahibinin
  onayıyla yapılır.
- **Plan görevleri**: "Kabul kriteri" doğrulanmadan görev bitmiş sayılmaz. Bitince görev başlığına
  `✅ (commit abc1234)` ekle. "Karar kapısı" / "Proje sahibi" yazan adımları kendin yapma, dur ve sor.
- UI metinleri Türkçe.

## Bilinen durumlar
- `clean_tags("ai, , ses")` → `", ai, ses"` (boş parça filtrelenmiyor). fable.md Görev 2'de düzeltilecek.
- Bu makinede HuggingFace indirmelerinde geçici SSL hataları görüldü. `load_model` başarısız olursa cache'teki
  İngilizce modele düşer ve uyarı gösterir. Çok dilli model (~470MB) lokalde henüz indirilmedi.
- Repo adındaki "Sematic" yazım hatası bilinçli olarak düzeltilmiyor (deploy ve CV linkleri kırılır).
