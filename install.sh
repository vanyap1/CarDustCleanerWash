#!/bin/bash

set -e

echo "🔧 Встановлення системних залежностей..."
sudo apt-get update
sudo apt-get install -y python3-kivy python3-smbus python3-requests

echo "📦 Встановлення Python-пакетів..."
python3 -m pip install --break-system-packages kivy_garden.graph --extra-index-url https://kivy-garden.github.io/simple/

echo "📝 Створення systemd сервісу..."
SERVICE_FILE="/etc/systemd/system/project-launcher.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=SmartHomeInfoCenter Launcher
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=vanya
WorkingDirectory=/home/vanya/
ExecStart=/home/vanya/project-launcher.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Дозвіл на запуск сервісу..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable project-launcher.service
sudo systemctl restart project-launcher.service

echo "🚀 Установка завершена. Сервіс запущено."
