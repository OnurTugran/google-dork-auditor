# 🛡️ Google Dork & Hassas Veri Sızıntı Denetim Aracı (OSINT Auditor)

Modern arayüze (GUI) ve CLI desteğine sahip, web siteleri ve altyapılardaki hassas veri sızıntılarını (parola dosyaları, veritabanı yedekleri, `.env` dosyaları, açık loglar, indekslenmiş IP kameralar vb.) tespit etmek ve düzeltmek için geliştirilmiş gelişmiş bir **OSINT & Güvenlik Denetim Aracı**.

---

## ✨ Özellikler

- **Modern & Karanlık Tema (Dark Mode):** Siber güvenlik operasyonlarına uygun Obsidian/Cyan/Indigo temalı Tkinter arayüzü.
- **Kapsamlı Dork & Zafiyet Kütüphanesi:**
  - 🔑 Kimlik & Parola Dosyaları (`passwords.txt`, `credentials.csv`, `.bak`)
  - ⚙️ Konfigürasyon & Ortam Değişkenleri (`.env`, `wp-config.bak`, `server.conf`)
  - 🗄️ Veritabanı Dökümleri (`.sql`, `.dump`, `.db`)
  - 📦 Sıkıştırılmış Site Yedekleri (`backup.zip`, `site.tar.gz`)
  - 📜 Sistem ve Hata Logları (`error.log`, `access.log`, `debug.log`)
  - 📂 Açık Dizin Listeleme (`intitle:"index of"`)
  - 📹 IP Kameralar & IoT Cihaz Parmak İzi (Hikvision, Dahua, Uniview, Axis, Bosch vb.)
- **Özel Dork Oluşturucu (Query Builder):** `filetype:`, `inurl:`, `intitle:`, `intext:`, `site:`, `before:`, `after:` gibi operatörleri kolayca kombine etme.
- **Çift Tarama Motoru:**
  - Varsayılan sistem tarayıcısında anında açma (`webbrowser`).
  - Opsiyonel **Selenium** otomasyonu (Chrome, Firefox, Edge) ile otomatik arama ve çerez onayını geçme.
- **🔒 Savunma & Önleme Rehberi:** Nginx, Apache (.htaccess), robots.txt ve Google URL Kaldırma için hazır yapılandırma kuralları.
- **CLI Modu:** Sunucularda veya başlıksız (headless) ortamlarda `--cli` parametresiyle doğrudan terminal üzerinden çalışabilme.

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- (Opsiyonel) Selenium ve Web Tarayıcı Sürücüleri

```bash
git clone https://github.com/OnurTugran/google-dork-auditor.git
cd google-dork-auditor
pip install -r requirements.txt
```

---

## 💻 Kullanım

### Grafik Arayüz (GUI) ile Başlatma:
```bash
python dork_araci.py
```

### Komut Satırı (CLI) Modu ile Başlatma:
```bash
python dork_araci.py --cli
```

---

## 📦 Tek Parça .exe Haline Getirme (PyInstaller)

Uygulamayı Python yüklü olmayan Windows sistemlerde tek tıkla çalıştırmak için:

```bash
pyinstaller GoogleDorkAuditor.spec
```
Oluşturulan çalıştırılabilir dosya `dist/GoogleDorkAuditor.exe` konumunda yer alacaktır.

---

## ⚠️ Yasal ve Etik Sorumluluk Reddi (Disclaimer)

Bu araç yalnızca **yasal güvenlik testleri, penetrasyon testleri ve sistem yöneticilerinin kendi sistemlerindeki zafiyetleri ve bilgi sızıntılarını denetlemesi (OSINT Auditing)** amacıyla geliştirilmiştir. 

Yetkisiz sistemlere erişmek veya izinsiz veri toplamak TCK Madde 243 ve ilgili uluslararası siber güvenlik kanunları uyarınca suç teşkil edebilir. Aracın kullanımından doğabilecek her türlü hukuki ve cezai sorumluluk son kullanıcıya aittir.
