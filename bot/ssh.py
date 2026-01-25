from kyt import *
import subprocess
import asyncio
import math
import time
import random
import requests
import datetime as DT
import os
from telethon.tl.custom import Button
from telethon import events
from telethon.errors import AlreadyInConversationError

# =================================================================
# FUNGSI PEMBANTU: AMBIL DATA & FORMAT PAGINATION
# =================================================================
def get_ssh_data():
    """Mengambil data raw dari script shell"""
    try:
        # Update: Tambahkan "bash" di depan agar pasti jalan
        cmd = 'bash /usr/bin/kyt/shell/bot/bot-member-ssh'
        
        # Eksekusi command
        raw_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        
        # Bersihkan output (split baris)
        data_list = [line for line in raw_output.splitlines() if line.strip() and "|" in line]
        
        return data_list
    except Exception as e:
        # Jika error, kembalikan list kosong (bisa diprint e untuk debug di journal)
        return []

def render_page(data_list, page, item_per_page=10):
    total_items = len(data_list)
    total_pages = math.ceil(total_items / item_per_page)
    
    if page < 0: page = 0
    if total_pages > 0 and page >= total_pages: page = total_pages - 1
    if total_pages == 0: page = 0 
    
    start = page * item_per_page
    end = start + item_per_page
    sliced_data = data_list[start:end]
    
    msg = f"""
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>👑 LIST MEMBER SSH & OVPN</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
"""
    if not sliced_data:
        msg += "<i>Tidak ada user ssh active.</i>"
    else:
        for row in sliced_data:
            try:
                parts = row.split("|")
                if len(parts) >= 3:
                    user = parts[0]
                    exp = parts[1]
                    status = parts[2]
                    icon_stat = "🟢" if "UNLOCKED" in status else "🔴"
                    msg += f"""
<b>👤 User   :</b> <code>{user}</code>
<b>📅 Exp    :</b> <code>{exp}</code>
<b>💎 Status :</b> {icon_stat} <code>{status}</code>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
"""
                else: continue
            except: continue

    display_page = page + 1 if total_pages > 0 else 0
    msg += f"\n📊 <b>Total:</b> {total_items} Users | 📄 <b>Page:</b> {display_page}/{total_pages}"
    return msg, total_pages

# =================================================================
# 1. CREATE SSH (INTEGRATED WITH ZIVPN)
# =================================================================
@bot.on(events.CallbackQuery(data=b'create-ssh'))
async def create_ssh(event):
    async def create_ssh_(event):
        try:
            # 1. Input Username
            async with bot.conversation(chat, timeout=120) as user_convo:
                await event.respond('**Input Username:**\n(Ketik `/cancel` untuk batal)')
                while True:
                    user_event = await user_convo.wait_event(events.NewMessage(incoming=True))
                    if user_event.sender_id == sender.id:
                        if user_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        user = user_event.raw_text.strip()
                        break 
            
            # 2. Input Password
            async with bot.conversation(chat, timeout=120) as pw_convo:
                await event.respond("**Input Password:**")
                while True:
                    pw_event = await pw_convo.wait_event(events.NewMessage(incoming=True))
                    if pw_event.sender_id == sender.id:
                        if pw_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        pw = pw_event.raw_text.strip()
                        break
    
            # 3. Input Limit IP
            async with bot.conversation(chat, timeout=120) as limit_convo:
                await event.respond("**Input Max Login/IP Limit:**\n`Contoh: 2`")
                while True:
                    limit_event = await limit_convo.wait_event(events.NewMessage(incoming=True))
                    if limit_event.sender_id == sender.id:
                        if limit_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        limit = limit_event.raw_text
                        if not limit.isdigit():
                             await event.respond("**Error:** Harap masukkan angka saja.")
                             continue
                        break

            # 4. Input Quota
            async with bot.conversation(chat, timeout=120) as quota_convo:
                await event.respond("**Input Quota (GB):**\n`Contoh: 10`")
                while True:
                    quota_event = await quota_convo.wait_event(events.NewMessage(incoming=True))
                    if quota_event.sender_id == sender.id:
                        if quota_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        quota = quota_event.raw_text
                        if not quota.isdigit():
                             await event.respond("**Error:** Harap masukkan angka saja.")
                             continue
                        break
            
            # 5. Input Expired
            async with bot.conversation(chat, timeout=120) as exp_convo:
                await event.respond("**Input Masa Aktif (Hari):**\n`Contoh: 30`")
                while True:
                    exp_event = await exp_convo.wait_event(events.NewMessage(incoming=True))
                    if exp_event.sender_id == sender.id:
                        if exp_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        exp = exp_event.raw_text
                        if not exp.isdigit():
                             await event.respond("**Error:** Harap masukkan angka saja.")
                             continue
                        break 
        
            msg_load = await event.respond("`Wait.. Setting up SSH & ZIVPN Account`")
            
            # Perintah Utama (User SSH System)
            cmd = f'useradd -e `date -d "{exp} days" +"%Y-%m-%d"` -s /bin/false -M {user} && echo "{pw}\n{pw}" | passwd {user} && echo "{user} hard maxlogins {limit}" >> /etc/security/limits.conf'
    
            try:
                subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                await msg_load.delete()
                await event.respond("**User Already Exist**", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
            else:
                # ==========================================================
                # START: INTEGRASI ZIVPN
                # ==========================================================
                try:
                    # PERBAIKAN: Gunakan tanda kutip "{variable}" agar aman
                    cmd_zivpn = f'bash /usr/local/bin/zivpn-add "{user}" "{pw}" "{exp}" "{limit}" "{quota}"'
                    
                    subprocess.check_output(cmd_zivpn, shell=True, stderr=subprocess.STDOUT)
                except Exception as e:
                    print(f"Failed to create ZIVPN user: {str(e)}")
                # ==========================================================
                # END: INTEGRASI ZIVPN
                # ==========================================================

                today = DT.date.today()
                later = today + DT.timedelta(days=int(exp))
                created_date = today.strftime("%d/%m/%Y")
                msg = f"""
========================================
🌟 <b>AKUN SSH & ZIVPN PREMIUM</b>
========================================

🔹 <b>INFORMASI AKUN</b>
Username: <code>{user.strip()}</code>
Domain: <code>{DOMAIN}</code>
Password: <code>{pw.strip()}</code>

🔹 <b>PORT INFO</b>
SSH WS: <code>80</code>
SSH SSL: <code>443</code>
ZIVPN UDP: <code>5667</code> (Game)

🔗 <b>FORMAT KONEKSI SSH</b>
<code>{DOMAIN}:443@{user.strip()}:{pw.strip()}</code>

🎮 <b>FORMAT KONEKSI ZIVPN</b>
<code>{DOMAIN}:5667@{user.strip()}:{pw.strip()}</code>
Format UDP: <code>{DOMAIN}:1-65535@{user.strip()}:{pw.strip()}</code>

📋 <b>INFORMASI TAMBAHAN</b>
Expired: <code>{later}</code>
IP Limit: <code>{limit.strip()} Device</code>
Quota: <code>{quota.strip()} GB</code>

========================================
♨ᵗᵉʳⁱᵐᵃᵏᵃˢⁱʰ ᵗᵉˡᵃʰ ᵐᵉⁿᵍᵍᵘⁿᵃᵏᵃⁿ ˡᵃʸᵃⁿᵃⁿ ᵏᵃᵐⁱ♨
Generated on {created_date}
========================================
"""
                await msg_load.delete()
                await event.respond(msg, parse_mode='html', buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

        except AlreadyInConversationError:
            await event.answer("⚠️ Sedang ada proses lain! Ketik /cancel dulu.", alert=True)
        except asyncio.TimeoutError:
            await event.respond("**Waktu Habis.**", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
        except Exception as e:
            await event.respond(f"**Error:** `{str(e)}`", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    chat = event.chat_id
    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await create_ssh_(event)
    else:
        await event.answer("Akses Ditolak", alert=True)

# =================================================================
# 2. DELETE SSH
# =================================================================
@bot.on(events.CallbackQuery(data=b'delete-ssh'))
async def delete_ssh(event):
    async def delete_ssh_(event):
        try:
            async with bot.conversation(chat, timeout=120) as user_convo:
                await event.respond("**Username To Be Deleted:**\n(Ketik `/cancel` untuk batal)")
                while True:
                    user_event = await user_convo.wait_event(events.NewMessage(incoming=True))
                    if user_event.sender_id == sender.id:
                        if user_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        user = user_event.raw_text
                        break
                
            cmd = f'printf "%s\n" "{user}" | bot-delssh'
            try:
                subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                await event.respond(f"**User** `{user}` **Not Found**", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
            else:
                subprocess.run(f'sed -i "/^{user} hard maxlogins/d" /etc/security/limits.conf', shell=True)
                # Note: Anda bisa menambahkan perintah hapus zivpn di sini jika punya script delete-nya
                # Contoh: subprocess.run(f'zivpn-del {user}', shell=True)
                await event.respond(f"**Successfully Deleted** `{user}`", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
                
        except AlreadyInConversationError:
            await event.answer("⚠️ Sedang ada proses lain! Ketik /cancel dulu.", alert=True)
        except asyncio.TimeoutError:
            await event.respond("**Timeout.**", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
        except Exception as e:
            await event.respond(f"**Error:** `{str(e)}`", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
            
    chat = event.chat_id
    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await delete_ssh_(event)
    else:
        await event.answer("Akses Ditolak", alert=True)

# =================================================================
# 3. TRIAL SSH (UPDATE: ADA UDP FORMAT & LIMIT 1)
# =================================================================
@bot.on(events.CallbackQuery(data=b'trial-ssh'))
async def trial_ssh(event):
    async def trial_ssh_(event):
        try:
            async with bot.conversation(chat, timeout=60) as exp_convo:
                await event.respond("**Input Masa Aktif (Menit):**\n`Contoh: 30`\n(Ketik `/cancel` untuk batal)")
                while True:
                    exp_event = await exp_convo.wait_event(events.NewMessage(incoming=True))
                    if exp_event.sender_id == sender.id:
                        if exp_event.raw_text == '/cancel':
                            await event.respond("❌ **Proses Dibatalkan.**")
                            return
                        exp = exp_event.raw_text
                        if not exp.isdigit():
                             await event.respond("**Error:** Harap masukkan angka saja.")
                             continue
                        break

            user = "trialX"+str(random.randint(100,1000))
            pw = "1"
            created_date = DT.date.today().strftime("%d/%m/%Y")
            msg_load = await event.respond("`Creating Trial Account...`")
            cmd = f'useradd -e "`date -d "{exp} minutes" +"%Y-%m-%d %H:%M:%S"`" -s /bin/false -M {user} && echo "{pw}\n{pw}" | passwd {user} && tmux new-session -d -s {user} "trial trialssh {user} {exp}" && echo "{user} hard maxlogins 1" >> /etc/security/limits.conf'
            try:
                subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                await msg_load.delete()
                await event.respond("**Failed to create trial.**", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
            else:
                msg = f"""
========================================
🌟 <b>AKUN TRIAL SSH</b>
========================================

🔹 <b>INFORMASI AKUN</b>
Username: <code>{user.strip()}</code>
Domain: <code>{DOMAIN}</code>
Password: <code>{pw.strip()}</code>
Limit IP: <code>1 Device</code>

🔗 <b>FORMAT KONEKSI</b>
WS Format: <code>{DOMAIN}:80@{user.strip()}:{pw.strip()}</code>
TLS Format: <code>{DOMAIN}:443@{user.strip()}:{pw.strip()}</code>
UDP Format: <code>{DOMAIN}:1-65535@{user.strip()}:{pw.strip()}</code>

📋 <b>INFORMASI TAMBAHAN</b>
Expired: <code>{exp} Minutes</code>
Quota: <code>1 GB</code>

========================================
♨ᵗᵉʳⁱᵐᵃᵏᵃˢⁱʰ ᵗᵉˡᵃʰ ᵐᵉⁿᵍᵍᵘⁿᵃᵏᵃⁿ ˡᵃʸᵃⁿᵃⁿ ᵏᵃᵐⁱ♨
Generated on {created_date}
========================================
"""
                await msg_load.delete()
                await event.respond(msg, parse_mode='html', buttons=[[Button.inline("‹ Main Menu ›", "menu")]])
        
        except AlreadyInConversationError:
            await event.answer("⚠️ Sedang ada proses lain! Ketik /cancel dulu.", alert=True)
        except Exception as e:
            await event.respond(f"**Error:** `{str(e)}`", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    chat = event.chat_id
    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await trial_ssh_(event)
    else:
        await event.answer("Akses Ditolak", alert=True)

# =================================================================
# 4. SHOW SSH
# =================================================================
@bot.on(events.CallbackQuery(data=b'show-ssh'))
async def show_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Access Denied", alert=True)
        return

    data_list = get_ssh_data()
    msg, total_pages = render_page(data_list, 0)
    
    buttons = []
    if total_pages > 1:
        buttons.append([Button.inline("Next ⏩", data=f"sshPage_1")])
    buttons.append([Button.inline("‹ Main Menu ›", "menu")])
    
    try: await event.edit(msg, buttons=buttons, parse_mode='html')
    except: await event.reply(msg, buttons=buttons, parse_mode='html')

@bot.on(events.CallbackQuery(pattern=b'sshPage_(\d+)'))
async def paginate_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Access Denied", alert=True)
        return

    try: page = int(event.data.decode().split('_')[1])
    except: page = 0
    
    data_list = get_ssh_data()
    msg, total_pages = render_page(data_list, page)
    
    nav_buttons = []
    if page > 0: nav_buttons.append(Button.inline("⏪ Prev", data=f"sshPage_{page-1}"))
    if page < total_pages - 1: nav_buttons.append(Button.inline("Next ⏩", data=f"sshPage_{page+1}"))
    
    buttons = []
    if nav_buttons: buttons.append(nav_buttons)
    buttons.append([Button.inline("‹ Main Menu ›", "menu")])
    
    try: await event.edit(msg, buttons=buttons, parse_mode='html')
    except: await event.answer("Halaman tidak berubah")

# =================================================================
# 5. LOGIN SSH
# =================================================================
@bot.on(events.CallbackQuery(data=b'login-ssh'))
async def login_ssh(event):
    async def login_ssh_(event):
        try:
            cmd = 'bot-cek-login-ssh'.strip()
            z = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
            
            if len(z) > 4000:
                nama_file = "login_ssh.txt"
                with open(nama_file, "w") as f:
                    f.write(z)
                await event.client.send_file(
                    event.chat_id,
                    nama_file,
                    caption="⚠️ **List Login Terlalu Panjang!**",
                    buttons=[[Button.inline("‹ Main Menu ›","menu")]]
                )
                os.remove(nama_file)
            else:
                await event.respond(f"{z}\n**Check Login SSH**", buttons=[[Button.inline("‹ Main Menu ›","menu")]])
        except Exception as e:
            await event.respond(f"**Error:** `{str(e)}`")

    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await login_ssh_(event)
    else:
        await event.answer("Access Denied", alert=True)

# =================================================================
# 6. MENU UTAMA SSH
# =================================================================
@bot.on(events.CallbackQuery(data=b'ssh'))
async def ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Access Denied", alert=True)
        return
        
    try:
        inline = [
            [Button.inline(" TRIAL SSH ","trial-ssh"), Button.inline(" CREATE SSH ","create-ssh")],
            [Button.inline(" DELETE SSH ","delete-ssh"), Button.inline(" CHECK Login SSH ","login-ssh")],
            [Button.inline(" SHOW All USER SSH ","show-ssh"), Button.inline(" REGIS IP ","regis")],
            [Button.inline("‹ Main Menu ›","menu")]
        ]
        try:
             isp = subprocess.check_output("curl --max-time 2 -s http://ip-api.com/json | python3 -c \"import sys, json; print(json.load(sys.stdin).get('isp', 'Unknown'))\"", shell=True).decode("utf-8").strip()
             country = subprocess.check_output("curl --max-time 2 -s http://ip-api.com/json | python3 -c \"import sys, json; print(json.load(sys.stdin).get('country', 'Unknown'))\"", shell=True).decode("utf-8").strip()
        except:
             isp = "Unknown"
             country = "Unknown"

        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━ 
** HOKAGE PREMIUM TUNNELING **
━━━━━━━━━━━━━━━━━━━━━━━ 
━━━━━━━━━━━━━━━━━━━━━━━ 
 **⚠️ MENU SSH & OVPN ⚠️**
━━━━━━━━━━━━━━━━━━━━━━━ 
🟢 **» Service:** `SSH OVPN ZIVPN`
🟢 **» Hostname/IP:** `{DOMAIN}`
🟢 **» ISP:** `{isp}`
🟢 **» Country:** `{country}`
🇮🇩 **» @HokageLegend**
━━━━━━━━━━━━━━━━━━━━━━━ 
"""
        await event.edit(msg, buttons=inline)
    except Exception as e:
        await event.respond(f"Error: {str(e)}")
