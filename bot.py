import os
import ssl
import smtplib
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GONDEREN = os.getenv("GONDEREN_MAIL")
SIFRE = os.getenv("UYGULAMA_SIFRESI")
ALICI = os.getenv("ALICI_MAIL")

def google_dns_ile_ip_bul(alan_adi):
    cozucu = dns.resolver.Resolver(configure=False)
    cozucu.nameservers = ["8.8.8.8", "8.8.4.4"]
    yanit = cozucu.resolve(alan_adi, "A")
    return yanit[0].to_text()


def eposta_gonder(urun_adi, guncel_fiyat, hedef_fiyat, url):
    mesaj = MIMEMultipart("alternative")
    mesaj["Subject"] = f"🚨 Fiyat Düştü: {urun_adi} ({guncel_fiyat} TL)"
    mesaj["From"] = GONDEREN
    mesaj["To"] = ALICI

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #16a34a;">
          <h2 style="color: #0f172a; margin-top: 0;">🚨 Hedef Fiyat Yakalandı!</h2>
          <p><strong>Takip Edilen Ürün:</strong> {urun_adi}</p>
          <p><strong>Güncel Fiyat:</strong> <span style="color: #16a34a; font-size: 18px; font-weight: bold;">{guncel_fiyat} TL</span></p>
          <p><strong>Belirlenen Hedef:</strong> {hedef_fiyat} TL</p>
          <a href="{url}" style="display: inline-block; background: #2563eb; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px;">Ürünü İncele</a>
        </div>
      </body>
    </html>
    """
    mesaj.attach(MIMEText(html, "html"))

    # Windows DNS ayarlarına dokunmadan doğrudan 8.8.8.8 üzerinden Gmail IP'sini çözer
    gmail_ip = google_dns_ile_ip_bul("smtp." + "gmail.com")

    baglam = ssl.create_default_context()
    baglam.check_hostname = False

    with smtplib.SMTP_SSL(gmail_ip, 465, context=baglam) as sunucu:
        sunucu.login(GONDEREN, SIFRE)
        sunucu.sendmail(GONDEREN, ALICI, mesaj.as_string())

def fiyat_kontrol_et(urun_adi, url, hedef_fiyat):
    guncel_fiyat = 1450.00
    print(f"🔎 Kontrol Edildi: {urun_adi} | Güncel: {guncel_fiyat} TL | Hedef: {hedef_fiyat} TL")

    if guncel_fiyat <= hedef_fiyat:
        try:
            eposta_gonder(urun_adi, guncel_fiyat, hedef_fiyat, url)
            print("✅ E-posta bildirimi başarıyla gönderildi! Gmail gelen kutunu kontrol et.")
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    print("🤖 Otomatik Fiyat Takip & E-posta Bildirim Botu Başlatıldı...")
    fiyat_kontrol_et("Mekanik Oyuncu Klavyesi", "https://ornek-magaza.com", 1600.00)
