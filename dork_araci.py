#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🛡️ Google Dork & Hassas Veri Sızıntı Denetim Aracı (OSINT & Security Auditor)
================================================================================
Genişletilmiş Hassas Dosya ve Zafiyet Şablonları:
- passwords.txt, credentials.csv, users.bak
- config.php.bak, .env dosyaları
- veritabanı yedekleri (.sql, .dump)
- log dosyaları (error.log, access.log)
- eski yedekler (backup.zip, site.tar.gz vb.)
- Hassas içerik anahtar kelimeleri: password, passwd, username, login, pwd, secret

Özellikler:
- Modern & Karanlık Temalı Tkinter GUI
- Çift Arama Motoru: Varsayılan Sistem Tarayıcısı (Webbrowser) & Opsiyonel Selenium
- Kapsamlı Savunma ve Önleme Rehberi (.htaccess, Nginx, robots.txt, Google URL Removal)
- Panoya Kopyalama, Canlı Önizleme ve Hızlı Filtreleme
- CLI Modu (--cli) Desteği
================================================================================
"""

import sys
import os
import time
import urllib.parse
import webbrowser
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Windows High DPI Desteği
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Opsiyonel Selenium Desteği
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


# ==============================================================================
# 1. HASSAS VERİ & DORK VERİTABANI
# ==============================================================================

SENSITIVE_KEYWORDS = [
    "password", "passwd", "username", "login", 
    "pwd", "secret", "DB_PASSWORD", "admin", "api_key"
]

SENSITIVE_CATEGORIES = {
    "🔑 Kimlik & Parola Dosyaları": [
        {
            "name": "passwords.txt / passwd.txt",
            "dork": 'filetype:txt inurl:password | inurl:passwords | inurl:passwd intext:password',
            "keywords": ["password", "passwd", "login"],
            "desc": "Açıkta bırakılan düz metin parola ve kullanıcı listeleri."
        },
        {
            "name": "credentials.csv / login.csv",
            "dork": 'filetype:csv inurl:credential | inurl:credentials | inurl:login intext:username | intext:password',
            "keywords": ["username", "password", "secret"],
            "desc": "Kullanıcı adı, e-posta ve parola içeren açık CSV tabloları."
        },
        {
            "name": "users.bak / passwd.bak",
            "dork": 'ext:bak inurl:users | inurl:user | inurl:passwd intext:password | intext:passwd',
            "keywords": ["users", "passwd", "password"],
            "desc": "Kullanıcı veritabanı veya kimlik bilgisi içeren .bak yedekleri."
        },
        {
            "name": "Hassas Kimlik İfadeleri İçeren TXT",
            "dork": 'filetype:txt intext:"password" | intext:"pwd" | intext:"secret" | intext:"username"',
            "keywords": ["password", "pwd", "secret", "username"],
            "desc": "Metin içerisinde doğrudan parola ve kimlik bilgisi geçen dosyalar."
        }
    ],
    "📹 IP Kameralar & Canlı Yayın Arayüzleri (Device Fingerprinting)": [
        {
            "name": "🏢 Hikvision IP Kamera & NVR (doc/page/login.asp)",
            "dork": 'intitle:"Hikvision" | inurl:"doc/page/login.asp" | inurl:"/doc/page/preview.asp"',
            "keywords": [],
            "desc": "Türkiye genelindeki üniversite ve kampüslerde en yaygın kullanılan Hikvision IP kamera ve NVR web panelleri."
        },
        {
            "name": "🏢 Dahua Web Service & IPC (WEB SERVICE / RPC2)",
            "dork": 'intitle:"WEB SERVICE" (inurl:"/RPC2_Login" | inurl:"login.html" | intext:"Dahua")',
            "keywords": [],
            "desc": "Üniversite ihalelerinde ve kampüs çevre güvenliğinde yaygın Dahua IP kamera ve kayıt cihazı panelleri."
        },
        {
            "name": "🏢 Uniview (UNV) Akıllı Kampüs Kameraları",
            "dork": '(intitle:"Uniview" | intitle:"UNV") (inurl:"login" | inurl:"/LAPI/V1.0/System/DeviceInfo")',
            "keywords": [],
            "desc": "Büyük kampüslerin yüksek veri depolama ve akıllı video analiz projelerinde tercih edilen Uniview (UNV) sistemleri."
        },
        {
            "name": "🏢 Axis Communications Premium Güvenlik",
            "dork": 'intitle:"Live View / - AXIS" | (intitle:"AXIS" inurl:"/view/viewer_index.shtml") | inurl:axis-cgi/mjpg',
            "keywords": [],
            "desc": "Köklü devlet ve lider vakıf üniversitelerinin kritik merkezlerinde yüksek siber güvenlik için kullanılan Axis sistemleri."
        },
        {
            "name": "🏢 Bosch Security Systems IP Video & VIP X",
            "dork": '(intitle:"Bosch Security Systems" | intitle:"BOSCH IP Camera" | intitle:"VIP X") (inurl:"/rcp.xml" | inurl:"/index.html")',
            "keywords": [],
            "desc": "Üniversite hastaneleri, tıp fakülteleri ve entegre kampüs tesislerinde kullanılan Bosch gözetim ve encoder cihazları."
        },
        {
            "name": "🎓 Kampüs & Üniversite Lider Markalar Taraması (5 Marka)",
            "dork": '(intitle:"Hikvision" | inurl:"doc/page/login.asp" | (intitle:"WEB SERVICE" "Dahua") | intitle:"Uniview" | intitle:"Live View / - AXIS" | intitle:"Bosch Security Systems")',
            "keywords": [],
            "desc": "Üniversitelerde en çok tercih edilen 5 lider markanın (Hikvision, Dahua, UNV, Axis, Bosch) ortak tarama dorku. (Hedef kutusuna site:edu.tr yazarak kullanabilirsiniz)."
        },
        {
            "name": "1. Axis Canlı Arayüz (Live View / - AXIS)",
            "dork": 'intitle:"Live View / - AXIS"',
            "keywords": [],
            "desc": "Axis marka IP kameraların varsayılan arayüz başlığı (Title Fingerprinting)."
        },
        {
            "name": "2. Genel Ağ Kameraları (Network Camera Live View)",
            "dork": 'intitle:"Network Camera" "Live View"',
            "keywords": [],
            "desc": "Çeşitli üreticilerin web arayüzlerinde varsayılan olarak gelen genel ağ kamerası başlıkları."
        },
        {
            "name": "3. webcamXP 5 Canlı Video Sunucusu",
            "dork": 'intitle:"webcamXP 5"',
            "keywords": [],
            "desc": "webcamXP canlı video akış ve gözetim yazılımı çalışan açık web panelleri."
        },
        {
            "name": "4. Toshiba Ağ Kameraları (TOSHIBA Network Camera)",
            "dork": 'intitle:"TOSHIBA Network Camera"',
            "keywords": [],
            "desc": "Toshiba marka ağ ve güvenlik kameralarının standart web arayüz başlığı."
        },
        {
            "name": "5. Panasonic Canlı Yenileme (ViewerFrame?Mode=Refresh)",
            "dork": 'inurl:ViewerFrame?Mode=Refresh',
            "keywords": [],
            "desc": "Panasonic IP kameraların canlı görüntü yenileme ve kontrol CGI sayfası (URL Fingerprinting)."
        },
        {
            "name": "6. Axis MJPG & JPG Akış Yolları (axis-cgi)",
            "dork": 'inurl:axis-cgi/jpg | inurl:axis-cgi/mjpg',
            "keywords": [],
            "desc": "Axis kameralarında canlı video akışı (MJPG) veya anlık resmi (JPG) servis eden CGI yolları."
        },
        {
            "name": "7. Standart Kamera Akış Yolu (view/index.shtml)",
            "dork": 'inurl:view/index.shtml',
            "keywords": [],
            "desc": "Gömülü Linux kamera sunucularında yaygın kullanılan standart canlı izleme URL'i."
        },
        {
            "name": "8. Misafir Görüntü Arayüzü (guestimage.html)",
            "dork": 'inurl:"/cgi-bin/guestimage.html"',
            "keywords": [],
            "desc": "Kimlik doğrulaması olmaksızın doğrudan anlık görüntü veren CGI betik sayfası."
        },
        {
            "name": "9. Donanımsal PTZ Kontrolleri (Pan / Tilt / Zoom)",
            "dork": 'intext:"Pan / Tilt / Zoom"',
            "keywords": [],
            "desc": "Kamera arayüzünde donanımsal yön ve zoom butonları barındıran kontrol panelleri (intext)."
        },
        {
            "name": "10. Kamera Kanal ve Ön Ayar (Camera 1 Preset)",
            "dork": 'intext:"Camera 1" "Preset"',
            "keywords": [],
            "desc": "Çoklu kamera izleme panellerinde kamera seçimi ve ön ayar (preset) kontrol butonları."
        },
        {
            "name": "11. Şifresiz Doğrudan Açık Kameralar (No Login / Auth Exclude)",
            "dork": 'intitle:"Live View / - AXIS" -inurl:login -intext:login',
            "keywords": [],
            "desc": "Giriş ekranı (login/auth) sormadan doğrudan canlı görüntü veren kameraları ayıklar."
        },
        {
            "name": "12. Panasonic Şifresiz Canlı Yayın (No Login)",
            "dork": 'inurl:ViewerFrame?Mode=Refresh -inurl:login -intext:login',
            "keywords": [],
            "desc": "Kimlik doğrulama ekranı olmadan doğrudan Panasonic kamera akışını filtreler."
        },
        {
            "name": "13. Kombine Kapsamlı Kamera Parmak İzi (Tüm Üreticiler)",
            "dork": '(intitle:"Live View / - AXIS" | inurl:view/index.shtml | inurl:ViewerFrame?Mode=Refresh | inurl:"/cgi-bin/guestimage.html") -inurl:login -intext:login',
            "keywords": [],
            "desc": "Başlık, URL ve CGI parmak izlerini birleştiren, giriş ekranlarını eleyen geniş kapsamlı denetim dorku."
        }
    ],
    "⚙️ Konfigürasyon & .env Dosyaları": [
        {
            "name": ".env Dosyaları (Çevre Değişkenleri)",
            "dork": 'filetype:env "DB_PASSWORD" | "SECRET_KEY" | "APP_KEY"',
            "keywords": ["DB_PASSWORD", "SECRET_KEY", "secret", "password"],
            "desc": "Açıkta kalan .env dosyaları (DB şifreleri, API secret tokenları)."
        },
        {
            "name": "config.php.bak / wp-config.bak",
            "dork": 'ext:bak inurl:config.php | inurl:wp-config | inurl:database intext:password',
            "keywords": ["password", "DB_PASSWORD", "secret"],
            "desc": "PHP veya CMS yapılandırma yedekleri (veritabanı bağlantı bilgileri)."
        },
        {
            "name": "Sunucu & Web Ayar Dosyaları",
            "dork": '(filetype:config | filetype:conf | filetype:ini) intext:connectionString | intext:password | intext:secret',
            "keywords": ["connectionString", "password", "secret"],
            "desc": "web.config, database.yml, server.conf gibi gizli anahtar içeren ayar dosyaları."
        }
    ],
    "🗄️ Veritabanı Yedekleri (.sql, .dump)": [
        {
            "name": "SQL Veritabanı Dökümleri",
            "dork": 'filetype:sql "INSERT INTO" intext:password | intext:passwd | intext:username',
            "keywords": ["password", "passwd", "username", "INSERT INTO"],
            "desc": "INSERT INTO komutları ve açık kullanıcı tabloları barındıran SQL dosyaları."
        },
        {
            "name": "Yedek SQL & Dump Dosyaları",
            "dork": '(ext:sql | ext:dump | ext:db) inurl:backup | inurl:dump | inurl:database intext:password | intext:secret',
            "keywords": ["backup", "dump", "database", "password"],
            "desc": "Sunucu kökünde unutulmuş .sql, .dump veya .db uzantılı yedekler."
        }
    ],
    "📦 Eski Arşiv & Yedekler (zip, tar.gz)": [
        {
            "name": "Sıkıştırılmış Web Sitesi Yedekleri",
            "dork": 'inurl:backup.zip | inurl:site.tar.gz | inurl:backup.tar.gz | inurl:www.zip | inurl:dump.zip',
            "keywords": ["backup.zip", "site.tar.gz", "backup", "site"],
            "desc": "Tüm web sitesi kaynak kodunu ve şifrelerini barındıran unutulmuş arşivler."
        },
        {
            "name": "Yedek Kod Dosyaları (.bak / .old / .save)",
            "dork": '(ext:bak | ext:old | ext:backup | ext:save) inurl:config | inurl:db | inurl:user intext:password',
            "keywords": ["config", "db", "user", "password"],
            "desc": "Geliştiricilerin düzenleme sonrası sunucuda unuttuğu .bak, .old dosyaları."
        }
    ],
    "📜 Sistem & Hata Log Dosyaları": [
        {
            "name": "Sistem Log Dosyaları (.log)",
            "dork": 'filetype:log intext:password | intext:login | intext:error | intext:exception',
            "keywords": ["password", "login", "error", "debug"],
            "desc": "Login denemeleri, şifre sıfırlama veya istisna kayıtlarında sızan bilgiler."
        },
        {
            "name": "Web Sunucu Logları (error_log / access_log)",
            "dork": '(inurl:access.log | inurl:error.log | inurl:debug.log) intext:password | intext:login',
            "keywords": ["password", "login", "secret"],
            "desc": "Doğrudan webden erişilebilen Apache/Nginx hata ve erişim logları."
        }
    ],
    "📂 Açık Dizinler (Directory Listing)": [
        {
            "name": "Index of / Kimlik & Yedek Belgeleri",
            "dork": 'intitle:"index of" "passwords.txt" | "credentials.csv" | "backup.zip" | "users.bak"',
            "keywords": ["index of", "passwords", "backup"],
            "desc": "Dizin listelemesi kapatılmamış sunucularda açıkta duran hassas belgeler."
        },
        {
            "name": "Index of / .env & Config Yedekleri",
            "dork": 'intitle:"index of" ".env" | "config.php.bak" | "backup.sql"',
            "keywords": ["index of", ".env", "config"],
            "desc": "Klasör görünümünde listelenen .env dosyaları ve yapılandırma yedekleri."
        }
    ],
    "🌐 Giriş ve Yönetim Panelleri": [
        {
            "name": "Admin / Yönetici Portalları",
            "dork": 'inurl:admin | inurl:cpanel | inurl:administrator intitle:"admin login" | intitle:"giriş"',
            "keywords": ["admin", "login", "cpanel"],
            "desc": "Yetkisiz erişim riski barındıran veya kamuya açık unutulmuş yönetim panelleri."
        }
    ]
}

OPERATORS = {
    "site": "site:",
    "filetype": "filetype:",
    "ext": "ext:",
    "intitle": "intitle:",
    "allintitle": "allintitle:",
    "inurl": "inurl:",
    "allinurl": "allinurl:",
    "intext": "intext:",
    "allintext": "allintext:",
    "inanchor": "inanchor:",
    "cache": "cache:",
    "related": "related:",
    "info": "info:",
    "before": "before:",
    "after": "after:",
}


# ==============================================================================
# 2. SELENIUM DRIVER YARDIMCILARI
# ==============================================================================

def create_selenium_driver(browser: str = "chrome"):
    if not SELENIUM_AVAILABLE:
        raise RuntimeError("Selenium kütüphanesi yüklü değil.")
    
    browser = browser.lower()
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--start-maximized")
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    elif browser == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument("--start-maximized")
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    else:
        raise ValueError(f"Desteklenmeyen tarayıcı: {browser}")


def search_google_selenium(driver, query: str):
    driver.get("https://www.google.com")
    time.sleep(1.2)
    try:
        buttons = driver.find_elements(By.XPATH, '//button')
        for btn in buttons:
            if any(x in btn.text.lower() for x in ["accept", "kabul", "agree", "tamam"]):
                btn.click()
                time.sleep(0.5)
                break
    except Exception:
        pass

    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)


# ==============================================================================
# 3. MODERN TKINTER GUI UYGULAMASI
# ==============================================================================

class DorkAuditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ Google Dork & Hassas Veri Sızıntı Denetim Aracı")
        self.geometry("1100x780")
        self.minsize(980, 680)

        # Renk Paleti (Modern Siber Güvenlik Konsolu - Obsidian / Cyan / Indigo)
        self.colors = {
            "bg_dark": "#0d1117",
            "card_bg": "#161b22",
            "card_secondary": "#21262d",
            "border": "#30363d",
            "accent_cyan": "#58a6ff",
            "accent_purple": "#8957e5",
            "accent_green": "#238636",
            "accent_green_hover": "#2ea043",
            "accent_amber": "#d29922",
            "accent_red": "#da3633",
            "text_primary": "#f0f6fc",
            "text_muted": "#8b949e",
            "text_bright": "#ffffff",
            "input_bg": "#0d1117"
        }

        self.configure(bg=self.colors["bg_dark"])

        # Seçili anahtar kelimeler kümesi
        self.selected_keywords = set()

        self._setup_styles()
        self._build_header()
        self._build_tabs()
        self._build_query_console()
        self._build_status_bar()

        # İlk şablonu yükle
        self._on_template_selected_default()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Notebook Sekme Stili
        style.configure("TNotebook", background=self.colors["bg_dark"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background=self.colors["card_bg"], 
                        foreground=self.colors["text_muted"],
                        padding=[18, 8],
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("TNotebook.Tab", 
                  background=[("selected", self.colors["card_secondary"])],
                  foreground=[("selected", self.colors["accent_cyan"])])

        # Treeview Stili
        style.configure("Treeview",
                        background=self.colors["card_bg"],
                        foreground=self.colors["text_primary"],
                        fieldbackground=self.colors["card_bg"],
                        font=("Segoe UI", 9),
                        rowheight=26,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=self.colors["card_secondary"],
                        foreground=self.colors["accent_cyan"],
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", self.colors["accent_purple"])],
                  foreground=[("selected", self.colors["text_bright"])])

        # Scrollbar Stili
        style.configure("Vertical.TScrollbar",
                        background=self.colors["card_secondary"],
                        troughcolor=self.colors["card_bg"],
                        borderwidth=0,
                        arrowsize=12)

    def _build_header(self):
        header_frame = tk.Frame(self, bg=self.colors["card_bg"], height=85, relief="flat", bd=0)
        header_frame.pack(fill="x", padx=14, pady=(12, 6))

        # Başlık ve Açıklama
        title_box = tk.Frame(header_frame, bg=self.colors["card_bg"])
        title_box.pack(side="left", padx=16, pady=10)

        title_lbl = tk.Label(
            title_box, 
            text="🛡️ Google Dork Hassas Veri & Güvenlik Denetim Aracı", 
            font=("Segoe UI", 14, "bold"), 
            fg=self.colors["accent_cyan"], 
            bg=self.colors["card_bg"]
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_box, 
            text="passwords.txt | .env | .sql | backup.zip | 📹 IP Kameralar & IoT | log & sızıntı denetimi", 
            font=("Segoe UI", 9), 
            fg=self.colors["text_muted"], 
            bg=self.colors["card_bg"]
        )
        subtitle_lbl.pack(anchor="w")

        # Hedef Site Kapsamı (Scope Entry)
        scope_box = tk.Frame(header_frame, bg=self.colors["card_bg"])
        scope_box.pack(side="right", padx=16, pady=10)

        scope_lbl = tk.Label(
            scope_box, 
            text="🎯 Hedef Alan Adı (site:)", 
            font=("Segoe UI", 9, "bold"), 
            fg=self.colors["text_primary"], 
            bg=self.colors["card_bg"]
        )
        scope_lbl.pack(anchor="w")

        entry_subframe = tk.Frame(scope_box, bg=self.colors["card_bg"])
        entry_subframe.pack(anchor="w", pady=(2, 0))

        self.site_entry = tk.Entry(
            entry_subframe, 
            font=("Segoe UI", 10), 
            bg=self.colors["input_bg"], 
            fg=self.colors["accent_cyan"],
            insertbackground=self.colors["accent_cyan"],
            relief="solid", 
            bd=1, 
            width=24
        )
        self.site_entry.pack(side="left", ipady=3)
        self.site_entry.insert(0, "")
        self.site_entry.bind("<KeyRelease>", lambda e: self._refresh_current_dork())

        clear_btn = tk.Button(
            entry_subframe,
            text="✖",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["card_secondary"],
            fg=self.colors["text_muted"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["accent_red"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._clear_site_entry
        )
        clear_btn.pack(side="left", padx=(4, 0))

    def _clear_site_entry(self):
        self.site_entry.delete(0, tk.END)
        self._refresh_current_dork()

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=6)

        # Sekme 1: Hazır Hassas Dosya Şablonları
        self.tab_templates = tk.Frame(self.notebook, bg=self.colors["card_bg"])
        self.notebook.add(self.tab_templates, text="  📁 Hazır Hassas Dosya Şablonları  ")
        self._init_tab_templates()

        # Sekme 2: Özel Gelişmiş Dork Oluşturucu
        self.tab_builder = tk.Frame(self.notebook, bg=self.colors["card_bg"])
        self.notebook.add(self.tab_builder, text="  🛠️ Özel Dork Oluşturucu  ")
        self._init_tab_builder()

        # Sekme 3: Güvenlik & Önleme Rehberi
        self.tab_defense = tk.Frame(self.notebook, bg=self.colors["card_bg"])
        self.notebook.add(self.tab_defense, text="  🔒 Savunma & Önleme Rehberi  ")
        self._init_tab_defense()

    # --------------------------------------------------------------------------
    # TAB 1: HAZIR ŞABLONLAR
    # --------------------------------------------------------------------------
    def _init_tab_templates(self):
        paned = tk.PanedWindow(self.tab_templates, orient="horizontal", bg=self.colors["border"], bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=8, pady=8)

        # Sol Panel: Kategori ve Şablon Listesi (Treeview)
        left_frame = tk.Frame(paned, bg=self.colors["card_bg"])
        paned.add(left_frame, minsize=380, width=430)

        tree_header = tk.Label(
            left_frame,
            text="🔍 Hassas Dosya & Sızıntı Kategorileri",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["accent_cyan"],
            bg=self.colors["card_bg"]
        )
        tree_header.pack(anchor="w", padx=6, pady=(4, 4))

        # Arama ve Hızlı Filtre Çubuğu
        search_box = tk.Frame(left_frame, bg=self.colors["card_bg"])
        search_box.pack(fill="x", padx=6, pady=(0, 6))

        search_lbl = tk.Label(
            search_box,
            text="🔎",
            font=("Segoe UI", 10),
            fg=self.colors["accent_cyan"],
            bg=self.colors["card_bg"]
        )
        search_lbl.pack(side="left", padx=(2, 4))

        self.filter_entry = tk.Entry(
            search_box,
            font=("Segoe UI", 9),
            bg=self.colors["input_bg"],
            fg=self.colors["accent_cyan"],
            insertbackground=self.colors["accent_cyan"],
            relief="solid",
            bd=1
        )
        self.filter_entry.pack(side="left", fill="x", expand=True)
        self.filter_entry.bind("<KeyRelease>", lambda e: self._on_filter_changed())

        clear_filter_btn = tk.Button(
            search_box,
            text="✖",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors["card_secondary"],
            fg=self.colors["text_muted"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["accent_red"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._clear_filter
        )
        clear_filter_btn.pack(side="left", padx=(4, 0))

        tree_container = tk.Frame(left_frame, bg=self.colors["card_bg"])
        tree_container.pack(fill="both", expand=True, padx=4, pady=2)

        self.tree = ttk.Treeview(tree_container, columns=("name",), show="tree", selectmode="browse")
        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Sağ Panel: Şablon Detayı ve Anahtar Kelime Filtresi
        right_frame = tk.Frame(paned, bg=self.colors["card_bg"])
        paned.add(right_frame, minsize=420)

        # Şablon Bilgisi
        self.template_title_lbl = tk.Label(
            right_frame, 
            text="Seçili Şablon", 
            font=("Segoe UI", 12, "bold"), 
            fg=self.colors["text_bright"], 
            bg=self.colors["card_bg"],
            wraplength=480,
            justify="left"
        )
        self.template_title_lbl.pack(anchor="w", padx=12, pady=(8, 2))

        self.template_desc_lbl = tk.Label(
            right_frame, 
            text="Açıklama...", 
            font=("Segoe UI", 9), 
            fg=self.colors["text_muted"], 
            bg=self.colors["card_bg"],
            wraplength=480,
            justify="left"
        )
        self.template_desc_lbl.pack(anchor="w", padx=12, pady=(0, 10))

        # Anahtar Kelimeler (Keyword Chips)
        kw_frame = tk.LabelFrame(
            right_frame,
            text="🔑 Hassas İçerik Filtresi (Dorka Otomatik Dahil Et)",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["accent_cyan"],
            bg=self.colors["card_bg"],
            relief="solid",
            bd=1
        )
        kw_frame.pack(fill="x", padx=12, pady=6)

        kw_note = tk.Label(
            kw_frame,
            text="Google, bu kelimeleri indekslediği için hassas dosyalar kolayca bulunur. İstediklerini seç:",
            font=("Segoe UI", 8),
            fg=self.colors["text_muted"],
            bg=self.colors["card_bg"]
        )
        kw_note.pack(anchor="w", padx=8, pady=(4, 6))

        chips_box = tk.Frame(kw_frame, bg=self.colors["card_bg"])
        chips_box.pack(fill="x", padx=6, pady=(0, 8))

        self.kw_check_vars = {}
        row, col = 0, 0
        for kw in SENSITIVE_KEYWORDS:
            var = tk.BooleanVar(value=False)
            self.kw_check_vars[kw] = var
            chk = tk.Checkbutton(
                chips_box,
                text=kw,
                variable=var,
                font=("Consolas", 9, "bold"),
                fg=self.colors["text_primary"],
                bg=self.colors["card_secondary"],
                selectcolor=self.colors["card_bg"],
                activebackground=self.colors["card_secondary"],
                activeforeground=self.colors["accent_cyan"],
                relief="flat",
                bd=0,
                padx=6,
                pady=2,
                command=self._on_keyword_toggle
            )
            chk.grid(row=row, column=col, padx=4, pady=4, sticky="w")
            col += 1
            if col > 2:
                col = 0
                row += 1

        # Hızlı Butonlar
        kw_btn_row = tk.Frame(kw_frame, bg=self.colors["card_bg"])
        kw_btn_row.pack(anchor="w", padx=8, pady=(0, 6))

        sel_all_btn = tk.Button(
            kw_btn_row,
            text="Tümünü Seç",
            font=("Segoe UI", 8),
            bg=self.colors["card_secondary"],
            fg=self.colors["accent_cyan"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._select_all_keywords
        )
        sel_all_btn.pack(side="left", padx=(0, 6))

        clear_all_btn = tk.Button(
            kw_btn_row,
            text="Temizle",
            font=("Segoe UI", 8),
            bg=self.colors["card_secondary"],
            fg=self.colors["text_muted"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._clear_all_keywords
        )
        clear_all_btn.pack(side="left")

        # Ağaç Verisini Doldur
        self._populate_tree()

    def _populate_tree(self, filter_text=""):
        self.tree.delete(*self.tree.get_children())
        filter_lower = filter_text.lower().strip()

        for cat_name, items in SENSITIVE_CATEGORIES.items():
            matching_items = []
            cat_matches = filter_lower in cat_name.lower()

            for item in items:
                if not filter_lower or cat_matches or filter_lower in item["name"].lower() or filter_lower in item["desc"].lower() or filter_lower in item["dork"].lower():
                    matching_items.append(item)

            if matching_items:
                cat_node = self.tree.insert("", "end", text=cat_name, open=True)
                for item in matching_items:
                    self.tree.insert(cat_node, "end", text=item["name"], values=(item["name"], cat_name))

    def _on_filter_changed(self):
        self._populate_tree(self.filter_entry.get())

    def _clear_filter(self):
        self.filter_entry.delete(0, tk.END)
        self._populate_tree("")

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        item_text = self.tree.item(item_id, "text")

        # Kategori başlığına tıklandıysa ilk alt öğesini otomatik seç
        for cat_name, items in SENSITIVE_CATEGORIES.items():
            if item_text == cat_name and items:
                children = self.tree.get_children(item_id)
                if children:
                    self.tree.selection_set(children[0])
                    self.tree.focus(children[0])
                    self._on_tree_select(None)
                return

        # Alt öğe (şablon) seçimi
        for cat_name, items in SENSITIVE_CATEGORIES.items():
            for item in items:
                if item["name"] == item_text:
                    self.current_template = item
                    self.template_title_lbl.config(text=item["name"])
                    self.template_desc_lbl.config(text=item["desc"])
                    
                    # Şablonun varsayılan anahtar kelimelerini işaretle
                    for kw, var in self.kw_check_vars.items():
                        var.set(kw in item.get("keywords", []))
                    
                    self._refresh_current_dork()
                    return

    def _on_template_selected_default(self):
        children = self.tree.get_children()
        if children:
            first_cat = children[0]
            cat_children = self.tree.get_children(first_cat)
            if cat_children:
                self.tree.selection_set(cat_children[0])
                self.tree.focus(cat_children[0])
                self._on_tree_select(None)

    def _select_all_keywords(self):
        for var in self.kw_check_vars.values():
            var.set(True)
        self._refresh_current_dork()

    def _clear_all_keywords(self):
        for var in self.kw_check_vars.values():
            var.set(False)
        self._refresh_current_dork()

    def _on_keyword_toggle(self):
        self._refresh_current_dork()

    # --------------------------------------------------------------------------
    # TAB 2: GELİŞMİŞ ÖZEL DORK OLUŞTURUCU
    # --------------------------------------------------------------------------
    def _init_tab_builder(self):
        main_frame = tk.Frame(self.tab_builder, bg=self.colors["card_bg"])
        main_frame.pack(fill="both", expand=True, padx=12, pady=10)

        # Sol Sütun ve Sağ Sütun için Grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Hızlı Uzantı / Dosya Butonları
        quick_frame = tk.Frame(main_frame, bg=self.colors["card_secondary"], relief="flat", bd=0)
        quick_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 10))

        q_lbl = tk.Label(
            quick_frame,
            text="⚡ Hızlı Dosya Türü / Uzantı Ekle:",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["accent_cyan"],
            bg=self.colors["card_secondary"]
        )
        q_lbl.pack(side="left", padx=8, pady=6)

        extensions = [".env", ".sql", ".bak", ".log", "passwords.txt", "credentials.csv", "backup.zip", "site.tar.gz"]
        for ext in extensions:
            b = tk.Button(
                quick_frame,
                text=ext,
                font=("Consolas", 8, "bold"),
                bg=self.colors["card_bg"],
                fg=self.colors["text_primary"],
                activebackground=self.colors["accent_purple"],
                activeforeground=self.colors["text_bright"],
                relief="flat",
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda e=ext: self._insert_quick_ext(e)
            )
            b.pack(side="left", padx=3, pady=6)

        # Operatör Girişleri
        self.builder_entries = {}
        fields_left = [
            ("filetype", "filetype: (örn: env, sql, log, txt)"),
            ("ext", "ext: (örn: bak, zip, gz, old)"),
            ("inurl", "inurl: (örn: backup, config, secret)"),
            ("allinurl", "allinurl: (birden fazla url kelimesi)"),
            ("intitle", 'intitle: (örn: "index of")'),
            ("allintitle", "allintitle: (başlık kelimeleri)"),
        ]

        fields_right = [
            ("intext", 'intext: (örn: password, secret)'),
            ("allintext", 'allintext: (metin kelimeleri)'),
            ("exact", 'Tam İfade / Tırnak İçinde ("...")'),
            ("keyword", "Serbest Anahtar Kelime"),
            ("after", "after: (YYYY-MM-DD)"),
            ("before", "before: (YYYY-MM-DD)"),
        ]

        # Sol Form
        row_idx = 1
        for key, label_text in fields_left:
            lbl = tk.Label(main_frame, text=label_text, font=("Segoe UI", 8, "bold"), fg=self.colors["text_muted"], bg=self.colors["card_bg"])
            lbl.grid(row=row_idx, column=0, sticky="w", padx=8, pady=(4, 1))
            ent = tk.Entry(main_frame, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground=self.colors["accent_cyan"], relief="solid", bd=1)
            ent.grid(row=row_idx+1, column=0, sticky="ew", padx=8, pady=(0, 4))
            ent.bind("<KeyRelease>", lambda e: self._generate_from_builder())
            self.builder_entries[key] = ent
            row_idx += 2

        # Sağ Form
        row_idx = 1
        for key, label_text in fields_right:
            lbl = tk.Label(main_frame, text=label_text, font=("Segoe UI", 8, "bold"), fg=self.colors["text_muted"], bg=self.colors["card_bg"])
            lbl.grid(row=row_idx, column=1, sticky="w", padx=8, pady=(4, 1))
            ent = tk.Entry(main_frame, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground=self.colors["accent_cyan"], relief="solid", bd=1)
            ent.grid(row=row_idx+1, column=1, sticky="ew", padx=8, pady=(0, 4))
            ent.bind("<KeyRelease>", lambda e: self._generate_from_builder())
            self.builder_entries[key] = ent
            row_idx += 2

        # Form Butonları
        b_frame = tk.Frame(main_frame, bg=self.colors["card_bg"])
        b_frame.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=8, pady=(10, 0))

        clr_btn = tk.Button(
            b_frame,
            text="🔄 Tüm Alanları Temizle",
            font=("Segoe UI", 9),
            bg=self.colors["card_secondary"],
            fg=self.colors["accent_red"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._clear_builder
        )
        clr_btn.pack(side="left")

    def _insert_quick_ext(self, ext_val):
        if ext_val.startswith("."):
            clean_ext = ext_val.replace(".", "")
            self.builder_entries["ext"].delete(0, tk.END)
            self.builder_entries["ext"].insert(0, clean_ext)
        else:
            self.builder_entries["inurl"].delete(0, tk.END)
            self.builder_entries["inurl"].insert(0, ext_val)
        self.notebook.select(self.tab_builder)
        self._generate_from_builder()

    def _clear_builder(self):
        for ent in self.builder_entries.values():
            ent.delete(0, tk.END)
        self._generate_from_builder()

    def _generate_from_builder(self):
        parts = []
        site = self.site_entry.get().strip()
        if site:
            clean_site = site.replace("https://", "").replace("http://", "").rstrip("/")
            parts.append(f"site:{clean_site}")

        for key, entry in self.builder_entries.items():
            val = entry.get().strip()
            if not val:
                continue
            if key in OPERATORS:
                op = OPERATORS[key]
                if key in ["intitle", "allintitle", "intext", "allintext"]:
                    parts.append(f'{op}"{val}"')
                else:
                    parts.append(f"{op}{val}")
            elif key == "exact":
                parts.append(f'"{val}"')
            elif key == "keyword":
                parts.append(val)

        generated = " ".join(parts)
        self.dork_text.delete("1.0", tk.END)
        self.dork_text.insert("1.0", generated)

    # --------------------------------------------------------------------------
    # TAB 3: GÜVENLİK & ÖNLEME REHBERİ (DEFENSIVE SECURITY & REMEDIATION)
    # --------------------------------------------------------------------------
    def _init_tab_defense(self):
        scroll_container = tk.Frame(self.tab_defense, bg=self.colors["card_bg"])
        scroll_container.pack(fill="both", expand=True, padx=12, pady=10)

        txt = tk.Text(
            scroll_container,
            bg=self.colors["card_bg"],
            fg=self.colors["text_primary"],
            font=("Segoe UI", 10),
            wrap="word",
            relief="flat",
            bd=0
        )
        scroll_y = ttk.Scrollbar(scroll_container, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scroll_y.set)

        txt.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        guide_content = """🛡️ WEB GÜVENLİĞİ VE HASSAS DOSYA SIZINTILARINI ÖNLEME REHBERİ

❓ Neden Google Bu Dosyaları İndeksler?
--------------------------------------------------------------------------------
1. Yanlış Web Kök Dizini (Web Root) Yapılandırması:
   - Geliştiriciler .env, veritabanı yedekleri (.sql) ve arşivleri (backup.zip) doğrudan 
     kamuya açık 'public_html' veya 'www' klasöründe unutur.
2. Açık Dizin Listeleme (Directory Browsing / Listing):
   - Web sunucusunda dizin listelemesi kapatılmadığında botlar tüm klasör ağacını tarar.
3. robots.txt Yanılgısı:
   - robots.txt dosyasına "Disallow: /admin" veya "Disallow: /passwords.txt" yazmak o 
     dosyayı korumaz! Aksine saldırganlara dosyanın varlığını ifşa eder ve harici bir link 
     varsa arama motorları içeriği yine de indeksleyebilir.

================================================================================
🛠️ 1. ADIM: NGINX SUNUCUSUNDA HASSAS DOSYALARI TAMAMEN ENGELLEME
================================================================================
Nginx konfigürasyonunuza (`/etc/nginx/sites-available/default`) aşağıdaki kuralları ekleyin:

location ~* \.(env|git|sql|bak|old|save|cfg|ini|log|tar|gz|zip)$ {
    deny all;
    return 404;
}

# Dizin listelemeyi kapatma:
autoindex off;

================================================================================
🛠️ 2. ADIM: APACHE (.htaccess) ERİŞİM ENGELLEME
================================================================================
Web sitenizin ana dizinindeki `.htaccess` dosyasına şu satırları ekleyin:

# Dizin listelemeyi kapat
Options -Indexes

# Hassas uzantılara ve dosyalara erişimi yasakla
<FilesMatch "(^\.env|passwords\.txt|credentials\.csv|\.sql|\.bak|\.log|backup\.zip)$">
    Order allow,deny
    Deny from all
</FilesMatch>

================================================================================
🛠️ 3. ADIM: .ENV VE GİZLİ VERİLERİN İDEAL MİMARİSİ
================================================================================
- .env ve veritabanı bağlantı dosyalarını web sunucusunun servis ettiği dizinin (public/www) 
  BIR ÜST DİZİNİNDE tutun.
- Versiyon kontrolüne (.git) asla şifre yüklemeyin. `.gitignore` içine şunları ekleyin:
  .env
  *.sql
  *.bak
  *.log
  backup.zip

================================================================================
🚨 4. ADIM: GOOGLE'DAN SIZAN VERİYİ HIZLICA KALDIRMA
================================================================================
Eğer sitenizden bir dosya Google tarafından indekslendiyse:
1. Dosyayı sunucudan silin veya 404/403 döndürecek şekilde erişimini kapatın.
2. Google Search Console paneline gidin -> 'Kaldırılanlar' (Removals) sekmesini açın.
3. 'Yeni İstek' diyerek sızan URL'yi arama sonuçlarından anında temizleyin.

================================================================================
📹 5. ADIM: IP KAMERALARIN İNDEKSLENMESİ (DEVICE FINGERPRINTING) VE SAVUNMA
================================================================================
İnternete açık veya yetkisiz erişime açık kalan IP kameraların arama motorları 
tarafından indekslenmesi, temelde 'cihaz parmak izi' (device fingerprinting) prensibine dayanır.

IP kameralar genellikle gömülü Linux sistemleri ve minik web sunucuları (GoAhead, Boa, 
lighttpd vb.) çalıştırır. Arama motorlarının bu cihazları bulabilmesinin 3 temel nedeni:
1. Sabit Sayfa Başlıkları (intitle:): Üreticiler arayüz başlıklarında model adı veya 
   standart terimleri kullanır ('Live View', 'Network Camera', 'webcamXP' vb.).
2. Standart Akış Yolları (inurl:): Video yayını veya kontrol paneli belirli dosya 
   yollarına (/view/index.shtml, /axis-cgi/mjpg/, /snap.jpg) sabitlenmiştir.
3. Standart Sayfa İçi İfadeler (intext:): Canlı izleme sayfalarında kamera kontrol 
   paneline ait buton yazıları ('Pan / Tilt / Zoom', 'Camera 1', 'Preset') yer alır.

🛡️ IP Kameraların İndekslenmesini Önleme (Savunma & Sıkılaştırma):
1. UPnP (Universal Plug and Play) Kapatılmalıdır:
   - Modem veya router üzerinde UPnP açık olduğunda, IP kameralar otomatik olarak 
     modemde dış porta yönlendirme açar ve cihazı internete (WAN) ifşa eder.
2. Kamera Asla Doğrudan İnternete Açılmamalıdır:
   - Kameralara 80, 554 (RTSP), 8080 gibi portlar üzerinden doğrudan port yönlendirme 
     yapılmamalıdır. Dış erişim mutlaka bir VPN (WireGuard, OpenVPN, Tailscale) tüneli 
     üzerinden sağlanmalıdır.
3. Varsayılan Kimlik Bilgileri Değiştirilmelidir:
   - Fabrika çıkışlı kullanıcı adı ve şifreler (admin / admin, admin / 12345 vb.) 
     güçlü ve tahmin edilemez parolalarla değiştirilmelidir.
4. Anonim / Misafir (Guest) Erişimi Kapatılmalıdır:
   - Birçok kamerada canlı izleme için 'Anonim Görüntülemeye İzin Ver' seçeneği 
     varsayılan olarak açık gelebilir; bu ayar kesinlikle devre dışı bırakılmalıdır.

⚠️ HUKUKİ VE ETİK HATIRLATMA:
Arama motorları tarafından indekslenmiş veya şifresiz bırakılmış olsa dahi, size ait 
olmayan bir IP kamerasına veya özel görüntü akışına erişmek, kaydetmek veya izlemek:
- Türk Ceza Kanunu Madde 243 (Bilişim sistemine yetkisiz erişim)
- Türk Ceza Kanunu Madde 134 (Özel hayatın gizliliğini ihlal)
- Uluslararası siber güvenlik ve veri koruma (KVKK / GDPR) kanunları uyarınca SUÇ TEŞKİL EDER.
Bu sorgular yalnızca kendi ağınızdaki veya yetkili olduğunuz sistemlerdeki güvenlik açıklarını 
ve internete sızan cihazları denetlemek (OSINT audit) amacıyla kullanılmalıdır.
"""
        txt.insert("1.0", guide_content)
        txt.config(state="disabled")

    # --------------------------------------------------------------------------
    # ORTAK DORK KONSOLU & AKSİYON BUTONLARI (ALT PANEL)
    # --------------------------------------------------------------------------
    def _build_query_console(self):
        console_frame = tk.Frame(self, bg=self.colors["card_bg"], relief="flat", bd=0)
        console_frame.pack(fill="x", padx=14, pady=(0, 6))

        # Başlık ve Düzenleme Uyarısı
        c_head = tk.Frame(console_frame, bg=self.colors["card_bg"])
        c_head.pack(fill="x", padx=12, pady=(8, 2))

        c_title = tk.Label(
            c_head,
            text="⚡ Oluşturulan Arama Dorku (Doğrudan Düzenlenebilir):",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["accent_cyan"],
            bg=self.colors["card_bg"]
        )
        c_title.pack(side="left")

        # Metin Kutusu
        self.dork_text = tk.Text(
            console_frame,
            height=3,
            font=("Consolas", 10, "bold"),
            bg=self.colors["input_bg"],
            fg="#00f0ff",
            insertbackground="#00f0ff",
            relief="solid",
            bd=1,
            wrap="word"
        )
        self.dork_text.pack(fill="x", padx=12, pady=(0, 8))

        # Butonlar Satırı
        btn_bar = tk.Frame(console_frame, bg=self.colors["card_bg"])
        btn_bar.pack(fill="x", padx=12, pady=(0, 10))

        # 1. Varsayılan Tarayıcıda Aç
        self.search_btn = tk.Button(
            btn_bar,
            text="🚀 Google'da Ara (Varsayılan Tarayıcı)",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["accent_green"],
            fg=self.colors["text_bright"],
            activebackground=self.colors["accent_green_hover"],
            activeforeground=self.colors["text_bright"],
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._launch_webbrowser
        )
        self.search_btn.pack(side="left", padx=(0, 8))

        # 2. Panoya Kopyala
        self.copy_btn = tk.Button(
            btn_bar,
            text="📋 Panoya Kopyala",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["accent_purple"],
            fg=self.colors["text_bright"],
            activebackground=self.colors["border"],
            activeforeground=self.colors["text_bright"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._copy_to_clipboard
        )
        self.copy_btn.pack(side="left", padx=(0, 8))

        # 3. Selenium Seçeneği
        if SELENIUM_AVAILABLE:
            self.selenium_btn = tk.Button(
                btn_bar,
                text="🌐 Selenium ile Aç",
                font=("Segoe UI", 9),
                bg=self.colors["card_secondary"],
                fg=self.colors["text_primary"],
                relief="flat",
                bd=0,
                padx=10,
                pady=6,
                cursor="hand2",
                command=self._launch_selenium
            )
            self.selenium_btn.pack(side="left", padx=(0, 8))

            self.browser_combo = ttk.Combobox(btn_bar, values=["Chrome", "Firefox", "Edge"], state="readonly", width=8)
            self.browser_combo.current(0)
            self.browser_combo.pack(side="left", ipady=3)
        else:
            sel_info = tk.Label(
                btn_bar,
                text="💡 Selenium kurulu değil (Doğrudan sistem tarayıcınız kullanılmaktadır)",
                font=("Segoe UI", 8),
                fg=self.colors["text_muted"],
                bg=self.colors["card_bg"]
            )
            sel_info.pack(side="left", padx=10)

        # 4. Temizle
        self.reset_btn = tk.Button(
            btn_bar,
            text="🗑️ Temizle",
            font=("Segoe UI", 9),
            bg=self.colors["card_secondary"],
            fg=self.colors["accent_red"],
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._clear_all
        )
        self.reset_btn.pack(side="right")

    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self,
            text="Hazır. Bir şablon seçin veya hedef alan adı girip aramayı başlatın.",
            font=("Segoe UI", 8),
            fg=self.colors["text_muted"],
            bg=self.colors["bg_dark"],
            anchor="w",
            padx=16,
            pady=4
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _set_status(self, msg: str, color=None):
        self.status_bar.config(text=msg, fg=color or self.colors["text_muted"])

    # --------------------------------------------------------------------------
    # DORK YENİLEME VE OLUŞTURMA MANTIĞI
    # --------------------------------------------------------------------------
    def _refresh_current_dork(self):
        # Aktif sekme Builder ise oradan üret
        curr_tab = self.notebook.index(self.notebook.select())
        if curr_tab == 1:
            self._generate_from_builder()
            return

        if not hasattr(self, "current_template") or not self.current_template:
            return

        base_dork = self.current_template["dork"]
        parts = []

        # Hedef alan adı
        site = self.site_entry.get().strip()
        if site:
            clean_site = site.replace("https://", "").replace("http://", "").rstrip("/")
            parts.append(f"site:{clean_site}")

        parts.append(base_dork)

        # Seçili hassas anahtar kelimeleri ekle
        active_kws = [kw for kw, var in self.kw_check_vars.items() if var.get()]
        if active_kws:
            kw_query = " | ".join([f'intext:"{kw}"' for kw in active_kws])
            # Eğer base_dork zaten intext içeriyorsa parantezle bağlayabiliriz
            parts.append(f"({kw_query})")

        final_query = " ".join(parts)
        self.dork_text.delete("1.0", tk.END)
        self.dork_text.insert("1.0", final_query)
        self._set_status(f"Dork güncellendi: {self.current_template['name']}")

    def _copy_to_clipboard(self):
        q = self.dork_text.get("1.0", tk.END).strip()
        if not q:
            self._set_status("Kopyalanacak dork bulunamadı!", self.colors["accent_red"])
            return
        self.clipboard_clear()
        self.clipboard_append(q)
        self.update()
        self._set_status("✅ Dork başarıyla panoya kopyalandı!", self.colors["accent_cyan"])

    def _launch_webbrowser(self):
        q = self.dork_text.get("1.0", tk.END).strip()
        if not q:
            messagebox.showwarning("Uyarı", "Lütfen önce bir arama sorgusu oluşturun.")
            return

        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}"
        try:
            webbrowser.open_new_tab(url)
            self._set_status(f"🚀 Arama varsayılan tarayıcıda açıldı: {q[:60]}...", self.colors["accent_green"])
        except Exception as e:
            messagebox.showerror("Hata", f"Tarayıcı açılamadı: {e}")

    def _launch_selenium(self):
        if not SELENIUM_AVAILABLE:
            messagebox.showwarning("Uyarı", "Selenium kütüphanesi yüklü değil. Varsayılan tarayıcı kullanılacak.")
            self._launch_webbrowser()
            return

        q = self.dork_text.get("1.0", tk.END).strip()
        if not q:
            messagebox.showwarning("Uyarı", "Lütfen önce bir arama sorgusu oluşturun.")
            return

        browser = self.browser_combo.get().lower()
        self._set_status(f"🌐 {browser.capitalize()} Selenium başlatılıyor, lütfen bekleyin...", self.colors["accent_amber"])

        def run_thread():
            try:
                driver = create_selenium_driver(browser)
                search_google_selenium(driver, q)
                self._set_status(f"✅ Selenium aramayı tamamladı. Tarayıcı penceresini inceleyebilirsiniz.", self.colors["accent_green"])
            except Exception as e:
                self._set_status(f"❌ Selenium Hatası: {e}", self.colors["accent_red"])

        threading.Thread(target=run_thread, daemon=True).start()

    def _clear_all(self):
        self.site_entry.delete(0, tk.END)
        self.dork_text.delete("1.0", tk.END)
        self._clear_all_keywords()
        self._set_status("Tüm alanlar temizlendi.")


# ==============================================================================
# 4. ESKİ CLI MODU (GEREKTİĞİNDE --cli İLE KULLANILABİLİR)
# ==============================================================================

def run_cli_mode():
    print("=" * 65)
    print("🛡️ Genişletilmiş Yasal OSINT Dork & Hassas Dosya Aracı (CLI Modu)")
    print("=" * 65)

    print("\n--- Hassas Dosya ve Zafiyet Kategorileri ---")
    cat_list = list(SENSITIVE_CATEGORIES.items())
    idx = 1
    item_map = {}
    for cat_name, items in cat_list:
        print(f"\n{cat_name}:")
        for item in items:
            print(f"  [{idx:2}] {item['name']}")
            print(f"       Dork: {item['dork']}")
            item_map[idx] = item
            idx += 1

    print("\n[0] Özel Dork Oluştur")
    choice = input("\nSeçiminiz (Numara): ").strip()

    if choice.isdigit() and int(choice) in item_map:
        selected_item = item_map[int(choice)]
        dork = selected_item["dork"]
        site = input("Hedef alan adı (örn: example.com, boş bırakılabilir): ").strip()
        if site:
            clean_site = site.replace("https://", "").replace("http://", "").rstrip("/")
            dork = f"site:{clean_site} {dork}"
        
        kw_add = input("Hassas anahtar kelimeler eklensin mi? (password, login, secret vb.) [e/h]: ").strip().lower()
        if kw_add == "e":
            dork += ' ("password" | "passwd" | "secret" | "username")'
        
        query = dork
    else:
        # Standart CLI girişleri
        print("\nOperatörleri doldurun (boş bırakabilirsiniz):")
        inputs = {
            "site": input("site: ").strip(),
            "filetype": input("filetype / ext: ").strip(),
            "inurl": input("inurl: ").strip(),
            "intitle": input("intitle: ").strip(),
            "intext": input("intext (password, secret vb.): ").strip(),
        }
        parts = []
        for k, v in inputs.items():
            if v:
                parts.append(f"{k}:{v}")
        query = " ".join(parts)

    if not query.strip():
        print("[!] Sorgu oluşturulamadı.")
        return

    print(f"\n[+] Oluşturulan Dork: \n{query}\n")
    open_choice = input("Aramayı Google'da açmak istiyor musunuz? (e/h) [e]: ").strip().lower()
    if open_choice != "h":
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
        webbrowser.open_new_tab(url)
        print("[*] Tarayıcınızda arama sayfası açıldı.")


# ==============================================================================
# 5. GİRİŞ NOKTASI
# ==============================================================================

def main():
    # Eğer terminalden --cli argümanı verilirse CLI modunda çalıştır
    if "--cli" in sys.argv:
        run_cli_mode()
    else:
        # Varsayılan olarak modern Tkinter GUI'yi başlat
        app = DorkAuditorApp()
        app.mainloop()


if __name__ == "__main__":
    main()