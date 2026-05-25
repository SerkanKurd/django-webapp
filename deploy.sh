#!/bin/bash

# 1. Hataları durdur (Herhangi bir adım hata verirse süreci durdurur)
set -e

echo "🚀 Dağıtım süreci başlıyor..."

# 2. Docker imajlarını derle ve ayağa kaldır
# --build: Kod değişikliklerini algılar
# -d: Arka planda çalıştırır
echo "🐳 Docker konteynerları paketleniyor ve başlatılıyor..."
docker compose up --build -d

# 3. Gereksiz/Eski imajları temizle (Disk alanını korumak için)
echo "🧹 Eski Docker imajları temizleniyor..."
docker image prune -f

echo "✅ İşlem tamamlandı! Uygulama http://localhost adresinde yayında."

# 4. GitHub Container Registry'ye imajı gönder (Opsiyonel)
docker tag django-webapp ghcr.io/serkankurd/django-webapp:latest
docker push ghcr.io/serkankurd/django-webapp:latest