# Süper Lig İddia Simülatörü (pygame)

Bu proje, eğitim amaçlı bir iddia / bahis simülatörüdür. 20 Süper Lig takımı için rastgele eşleşmeler oluşturur, oranlar verir ve oranlara göre maç skorlarını simüle eder.

Özellikler
- 20 takımlık örnek havuzundan rastgele 10 maç oluşturma
- Her maç için rastgele oranlar (ev sahibi / berabere / deplasman)
- Oranlara göre olasılık hesaplama ve skor simülasyonu
- Pygame tabanlı basit arayüz: tümünü simüle et, maçları yeniden oluştur, tek tek simüle et
- Sorumlu kullanım mesajı

Gereksinimler
- Python 3.8+ ve `pygame` (requirements.txt içinde belirtilmiştir)

Kurulum & Çalıştırma (Windows PowerShell örneği):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bet_simulator.py
```

Notlar
- Bu uygulama gerçek bahis oynamayı teşvik etmez; yalnızca eğitim ve farkındalık amaçlıdır.
- İstediğiniz geliştirmeler varsa belirtin: istatistik takibi, bahis bütçesi simülasyonu, daha fazla takım verisi, gerçek lig verileri bağlama vb.
