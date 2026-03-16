1. Tạo service Systemd cho bot
   `sudo nano /etc/systemd/system/binance-notification-2.service`

Dán nội dung này (đã theo đúng path bạn gửi):

```
[Unit]
Description=Binance Notification Bot 2
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/tool-air/binance-notification-2
ExecStart=/root/tool-air/binance-notification-2/venv/bin/python /root/tool-air/binance-notification-2/main.py
Restart=always
RestartSec=10
KillSignal=SIGINT
TimeoutStopSec=30

# Nếu muốn giới hạn RAM cứng (tùy chọn):
# MemoryMax=700M

[Install]
WantedBy=multi-user.target
```

2. Enable + start service

```
sudo systemctl daemon-reload
sudo systemctl enable binance-notification-2
sudo systemctl start binance-notification-2
```

Kiểm tra:

```
sudo systemctl status binance-notification-2
sudo journalctl -u binance-notification-2 -f
```

3. Lệnh vận hành hằng ngày

```
sudo systemctl restart binance-notification-2
sudo systemctl stop binance-notification-2
sudo systemctl start binance-notification-2
```
