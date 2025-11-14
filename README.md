
## 🚀 PANTALLA DEL MENÚ

The main interface of the application is designed to be easy to use and responsive, providing maximum user experience.

<p align="center">
  <img src="https://github.com/bransilva/master/blob/main/yeik.jpg?raw=true" alt="Tampilan Menu" width="600"/>
</p>
---

## 💾 BACKUP DATA VPS

Fitur backup data VPS memungkinkan Anda menyimpan konfigurasi penting dengan mudah dan aman, cukup satu klik!


### BEFORE INSTALL
➽ Debian 10 & 11 (recommended)   
  

1.  :    
<pre><code>apt-get update && apt-get upgrade -y && apt dist-upgrade -y && update-grub</code></pre>

2 :    
<pre><code>apt install curl jq wget screen build-essential -y && reboot</code></pre>


### UBUNTU & DEBIAN INSTALL SCRIPT 
```
apt install -y && apt update -y && apt upgrade -y && wget -q https://raw.githubusercontent.com/bransilva/master/refs/heads/main/premi.sh && chmod +x premi.sh && ./premi.sh
```

## UPDATE SCRIPT
```
wget -q https://raw.githubusercontent.com/bransilva/master/refs/heads/main/update.sh && chmod +x update.sh && ./update.sh
```

### SUPPORT OS LINUX
- UBUNTU 20.04.05
- DEBIAN 10

### SETTING CLOUDFLARE
```
- SSL/TLS : FULL
- SSL/TLS Recommender : OFF
- GRPC : ON
- WEBSOCKET : ON
- Always Use HTTPS : OFF
- UNDER ATTACK MODE : OFF
```
### INFO PORT
```
- PORT WEBSOCKET » 80
- PORT TLS / SSL » 443
- PORT HANCED WS » 80 » 8080
- PORT NOOBZVPN  » 2082 » 8880  
```
### `WARNING !`
```
If You Get Service Off Status
Please Restart Service.
If Service Status Still Off
Please Reboot your VPS
```

### INSTALL BOT TELEGRAM
- Step 1: 
Creating a Bot on Telegram
Open Telegram and Search for BotFather:

Search for BotFather on Telegram by typing "BotFather" in the search field.
Select BotFather (the official account with a blue check mark).
Creating a New Bot:

Send a message /start to BotFather to get started.
Send a message /newbot to create a new bot.
Follow the instructions to provide a name and username for your bot.
Once completed, BotFather will provide a bot API token. Save this token because it will be used in your script.

- Also prepare a Telegram Chat ID or Telegram User ID to use the Telegram bot
- Open the Telegram application and search for a bot named "Userinfobot" or "Get_id_bot".
- 

Click "Start" to start the bot.
The bot will automatically send a message containing your chat ID.




### get root access to your vps

``````

  wget -qO- -O aksesroot.sh https://raw.githubusercontent.com/bransilva/master/refs/heads/main/aksesroot.sh && bash aksesroot.sh

```````




#### REINSTALL VPS UBUNTU DEBIAN

```
curl -O https://raw.githubusercontent.com/bransilva/master/refs/heads/main/reinstall.sh
chmod +x reinstall.sh
bash reinstall.sh debian 11 --password YOUR_PASSWORD
```

INSTALL HAPROXY DEBIAN 11

```
sudo apt install -t bullseye-backports haproxy

sed -i "s#xxx#https://raw.githubusercontent.com/bransilva/master/refs/heads/main/#g" /etc/haproxy/haproxy.cfg

sudo systemctl restart haproxy

sudo systemctl status haproxy
```


## FIX V2RAY ( VMESS-VLESS-TROJAN NOT CONNECT )
### Downgrade v2ray 

### copy paste command in vps after reboot install
```
sudo systemctl stop xray
sudo mv /usr/local/bin/xray /usr/local/bin/xray.bak.v25.10
wget https://github.com/XTLS/Xray-core/releases/download/v25.1.30/Xray-linux-64.zip
unzip Xray-linux-64.zip
sudo mv xray /usr/local/bin/xray
sudo chmod +x /usr/local/bin/xray
/usr/local/bin/xray version
sudo systemctl start xray
sudo systemctl enable xray
```
