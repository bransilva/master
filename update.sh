#!/bin/bash

# Pastikan lolcat terinstall untuk pewarnaan header
if ! command -v lolcat &> /dev/null; then
    apt-get install ruby -y &> /dev/null
    gem install lolcat &> /dev/null
fi

clear

# --- FUNGSI ANIMASI LOADING ---
fun_bar() {
    CMD="$1"
    (
        [[ -e $HOME/fim ]] && rm $HOME/fim
        $CMD >/dev/null 2>&1
        touch $HOME/fim
    ) >/dev/null 2>&1 &

    tput civis
    echo -ne "  \033[0;33mSedang Memproses Update \033[1;37m- \033[0;33m["
    while true; do
        for ((i = 0; i < 18; i++)); do
            echo -ne "\033[0;32m#"
            sleep 0.1s
        done
        if [[ -e $HOME/fim ]]; then
            rm $HOME/fim
            break
        fi
        echo -e "\033[0;33m]"
        sleep 1s
        tput cuu1
        tput dl1
        echo -ne "  \033[0;33mSedang Memproses Update \033[1;37m- \033[0;33m["
    done
    echo -e "\033[0;33m]\033[1;37m -\033[1;32m SUKSES !\033[1;37m"
    tput cnorm
}

# --- FUNGSI UPDATE UTAMA ---
res1() {
    # 1. Download & Install FV Tunnel (Optional/Config)
    wget -qO- fv-tunnel "https://github.com/bransilva/master/raw/refs/heads/main/config/fv-tunnel" 
    chmod +x fv-tunnel 
    bash fv-tunnel
    rm -rf fv-tunnel
    
    # 2. Bersihkan Folder sbin (Hati-hati, pastikan ZIP lengkap)
    rm -rf /usr/local/sbin/*
    
    # 3. Download & Ekstrak Menu (Berisi: menu, xp-zivpn, ssh-accountant, dll)
    wget https://github.com/bransilva/master/raw/refs/heads/main/menu/menu.zip
    unzip -o menu.zip > /dev/null 2>&1
    chmod +x menu/*
    mv menu/* /usr/local/sbin/
    rm -rf menu
    rm -rf menu.zip
    
    # 4. Download Menu Utama Spesifik (Overwrite jika perlu update terpisah)
    # Jika file 'menu' sudah ada di dalam zip, langkah ini bisa dihapus/diabaikan
    wget -q -O /usr/local/sbin/menu https://github.com/bransilva/master/raw/refs/heads/main/menu/menu
    chmod +x /usr/local/sbin/menu
    
    # 5. Buat Folder Usage (Penting untuk ssh-accountant)
    mkdir -p /etc/ssh/usage
    mkdir -p /etc/zivpn/usage
    chmod 777 /etc/ssh/usage
    chmod 777 /etc/zivpn/usage
    
    # 6. FIX WINDOWS LINE ENDING & PERMISSION
    sed -i 's/\r$//' /usr/local/sbin/*
    chmod +x /usr/local/sbin/*

    # ==========================================
    # SETTING CRON JOB (JANTUNG OTOMATISASI)
    # ==========================================

    # A. SSH ACCOUNTANT (Pencatat Kuota Realtime - Tiap 1 Menit)
    # Pastikan file ssh-accountant sudah ada di /usr/local/sbin/ dari hasil unzip
    cat >/etc/cron.d/ssh_accountant <<-END
    SHELL=/bin/sh
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
    * * * * * root /usr/local/sbin/ssh-accountant
END

    # B. XP-ZIVPN (Auto Expired & Sync - Jam 00:00 Malam)
    cat >/etc/cron.d/xp_zivpn <<-END
    SHELL=/bin/sh
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
    0 0 * * * root /usr/local/sbin/xp-zivpn
END

    # C. LIMIT QUOTA (Auto Lock User Over Quota - Tiap 10 Menit)
    # Menghapus jadwal lama (cleanup)
    rm -f /etc/cron.d/limit_quota
    sed -i "/limit-quota/d" /etc/crontab
    
    # Membuat jadwal baru
    cat >/etc/cron.d/limit_quota <<-EOF
    SHELL=/bin/sh
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
    */10 * * * * root /usr/local/sbin/limit-quota
EOF

    # Restart Cron agar semua jadwal berjalan
    service cron restart
}

# --- EKSEKUSI ---
rm -rf update.sh
clear
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | lolcat
echo -e " \e[1;97;101m UPDATE SCRIPT SEDANG BERJALAN !             \e[0m"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | lolcat
echo -e ""
echo -e "  \033[1;91m Update Script Service & Menu\033[1;37m"

fun_bar 'res1'

echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | lolcat
echo -e ""
echo -e " \033[1;32m Update Selesai! Silakan cek menu.\033[0m"
echo -e ""
read -n 1 -s -r -p "Tekan [ Enter ] untuk kembali ke menu"
menu
