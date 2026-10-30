# 📡 nmap cheat sheet

> Only scan machines you own, your lab, or `scanme.nmap.org` (which the Nmap project allows for practice).

## 🧭 Reading the output

| State | Meaning |
|---|---|
| 🟢 `open` | A program is listening and accepting connections |
| 🔴 `closed` | The host answered, but nothing is listening there |
| 🟡 `filtered` | A firewall dropped the probe, so nmap can't tell |

- **SERVICE** without `-sV` is only a guess based on the port number.
- Lines starting with `|_` come from **NSE scripts** (turned on by `-sC` or `-A`).
- **OS guesses can be wrong.** Behind VirtualBox NAT, nmap fingerprints VirtualBox's relay instead of the target.

## ⚙️ Flags I use

| Flag | What it does |
|---|---|
| `-p 22` · `-p 1-1000` · `-p-` | Ports: one, a range, all 65,535 |
| `-sS` | SYN "stealth" scan (default with sudo). Sends SYN, never finishes the handshake |
| `-sT` | Full TCP connect scan (no sudo needed) |
| `-sU` | UDP scan (slow, use `--top-ports 20`) |
| `-sV` | Detect the software and version |
| `-sC` | Run the default scripts |
| `-O` | Guess the operating system |
| `-A` | `-sV -sC -O` + traceroute in one |
| `-sn` | Find live hosts only, no port scan |
| `-Pn` | Skip the "is it up?" check (for hosts that ignore ping) |
| `-T4` | Faster timing |
| `-oN file.txt` | Save normal output |
| `-oA name` | Save in all formats (.nmap, .xml, .gnmap) |
| `--script vuln` | Run the vulnerability-check scripts |

## 🧪 Recipes

```bash
# What's on my own machine?
nmap 127.0.0.1

# Which hosts are alive in my host-only lab?
nmap -sn 192.168.56.0/24

# Quick look at a lab target
nmap -sV -sC LAB-IP -oN scans/quick.txt

# Every TCP port, then versions on the open ones
nmap -p- --min-rate 1000 LAB-IP
nmap -sV -sC -p 21,22,80 LAB-IP

# Top UDP ports
sudo nmap -sU --top-ports 20 LAB-IP

# Practice target on the internet (run once, don't loop it)
sudo nmap -A -T4 scanme.nmap.org -oN scan1.txt
```

## 🧠 Lessons from day 1
1. A fresh Kali shows **1000 closed ports**. Nothing running means nothing to attack.
2. `sudo systemctl start ssh` turned port 22 **open**. `-sV` then showed `OpenSSH 10.4p1 Debian 5`.
3. Always stop services you started for testing: `sudo systemctl stop ssh`.
4. A 0.35 ms, 1-hop result for a server on the internet is impossible. Sanity-check what nmap tells you.
