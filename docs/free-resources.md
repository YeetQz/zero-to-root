# 🆓 Free resources

Everything on this path costs **$0**. Some need a free account. Nothing here has a paywall partway through.
Checked October 2026. If a link moves, search for the name.

## 🐧 Linux & Bash

| Resource | What you get | Link |
|---|---|---|
| 🌊 **OverTheWire: Bandit** | A game played over SSH. Each level teaches a Linux trick | [overthewire.org/wargames/bandit](https://overthewire.org/wargames/bandit/) |
| 🌊 **OverTheWire: Leviathan** | The next step after Bandit: permissions and sneaky files | [overthewire.org/wargames/leviathan](https://overthewire.org/wargames/leviathan/) |
| 📕 **The Linux Command Line** (William Shotts) | A full book, free PDF from the author. Chapters 1–10 cover all the basics, and part 4 teaches Bash scripting | [linuxcommand.org/tlcl.php](https://www.linuxcommand.org/tlcl.php) |
| 📖 `man` pages | The manual is already on your Kali: `man ls`, `man bash` | your terminal |
| 🐚 This repo | [Bash cheat sheet](../cheatsheets/bash.md), [practice scripts](../scripts/practice/), `./hunter quiz bash` | here |

## 🌐 Networking

| Resource | What you get | Link |
|---|---|---|
| 🎥 **Professor Messer Network+ (N10-009)** | A complete free video course: IP addresses, ports, protocols, routing, Wi-Fi | [professormesser.com N10-009 course](https://www.professormesser.com/network-plus/n10-009/n10-009-video/n10-009-training-course/) |
| 🦈 **Wireshark docs + sample captures** | The official guide, plus real capture files to open and explore safely | [wireshark.org/docs](https://www.wireshark.org/docs/) · [wiki.wireshark.org](https://wiki.wireshark.org/) |
| 📡 **Nmap Reference Guide** | The official manual, free online | [nmap.org/book/man.html](https://nmap.org/book/man.html) |
| 🛰️ This repo | [Network tracking & privacy lesson](lessons/network-tracking.md), `./hunter quiz networking`, `./hunter quiz privacy` | here |

## 🏯 Practice grounds (CTFs & wargames)

| Resource | What you get | Link |
|---|---|---|
| 🏴 **picoCTF / picoGym** | Hundreds of beginner-friendly challenges, open all year, run by Carnegie Mellon University. Free account (now through the CyLab Security Academy) | [picoctf.org](https://picoctf.org/) |
| 🌊 **OverTheWire: Natas** | A web hacking wargame in your browser. Each level is a website hiding the next password | [overthewire.org/wargames/natas](https://overthewire.org/wargames/natas/) |
| 🕸️ **PortSwigger Web Security Academy** | Hundreds of free web hacking labs with lessons, from the makers of Burp Suite. Free account. Burp Suite Community Edition is free too | [portswigger.net/web-security](https://portswigger.net/web-security) |

## 🧪 Run-it-yourself targets (in your host-only lab)

| Resource | What you get | Link |
|---|---|---|
| 💣 **Metasploitable 2** | A deliberately vulnerable Linux VM with dozens of old services | [SourceForge](https://sourceforge.net/projects/metasploitable/) |
| 🍹 **OWASP Juice Shop** | A modern, deliberately insecure web shop with 100+ challenges and a built-in score board | [github.com/juice-shop/juice-shop](https://github.com/juice-shop/juice-shop) |
| 🕸️ **DVWA** | Damn Vulnerable Web App: SQL injection, XSS and more at Low/Medium/High difficulty | [github.com/digininja/DVWA](https://github.com/digininja/DVWA) |
| 💀 **VulnHub** | Free downloadable VMs to hack, from easy to hard | [vulnhub.com](https://www.vulnhub.com/) |
| ↳ Basic Pentesting 1 | A classic first box | [entry](https://www.vulnhub.com/entry/basic-pentesting-1,216/) |
| ↳ DC-1 | A beginner box built around a web app | [entry](https://www.vulnhub.com/entry/dc-1,292/) |

Juice Shop on Kali, in one go:

```bash
sudo apt install -y docker.io
sudo docker run -d -p 3000:3000 bkimminich/juice-shop
# then open http://localhost:3000 in Firefox inside Kali
```

> [!WARNING]
> Vulnerable VMs go on your **host-only** network only. Never NAT, never bridged, never exposed to the internet.

## 🔑 Passwords & privilege escalation

| Resource | What you get | Link |
|---|---|---|
| 🧰 **Kali tool docs** | Official pages for every tool (john, hashcat, gobuster…) | [kali.org/tools](https://www.kali.org/tools/) |
| 🐱 **Hashcat wiki** | How hash modes and attacks work | [hashcat.net/wiki](https://hashcat.net/wiki/) |
| 🧗 **GTFOBins** | A free list of how normal Linux programs can be misused for privilege escalation, the reference everyone uses | [gtfobins.github.io](https://gtfobins.github.io/) |

## 🛡️ Your own privacy

| Resource | What you get | Link |
|---|---|---|
| 🔓 **Have I Been Pwned** | Check if your own email was in a data breach | [haveibeenpwned.com](https://haveibeenpwned.com/) |
| 🧾 `exiftool` | Already on Kali. See (and remove) the hidden data in your own photos | `exiftool photo.jpg` |
