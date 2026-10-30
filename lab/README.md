# 🧪 My home lab

## 🖥️ Host
- Windows 11 Pro · AMD Ryzen 9 9950X3D · 64 GB RAM
- Oracle VirtualBox
- Hyper-V and Virtualization-based security **off** (see [hyperv-fix.md](hyperv-fix.md))

## 🐉 Attacker: Kali Linux
| Setting | Value |
|---|---|
| OS type | Debian (64-bit) |
| RAM / CPUs | 4096 MB / 2 |
| Video | VBoxSVGA, 128 MB, 3D acceleration off |
| Disk | 60 GB, dynamically allocated |
| Network | Adapter 1: NAT (internet) · Adapter 2: Host-only (lab) |

## 🎯 Targets (planned)
| Machine | Why | Network |
|---|---|---|
| 💣 Metasploitable 2 | Dozens of old, vulnerable services to scan and exploit | **Host-only only** |
| 🕸️ DVWA | Practice web attacks: SQLi, XSS, file upload | Host-only |

> [!WARNING]
> Metasploitable is deliberately vulnerable. Never put it on NAT or Bridged networking, and never expose it to the internet.

## 🔌 Host-only network setup
1. VirtualBox → **File → Tools → Network Manager → Host-only Networks → Create** (usually `192.168.56.0/24`)
2. Kali → Settings → Network → **Adapter 2**: Host-only Adapter
3. Metasploitable → Settings → Network → **Adapter 1**: Host-only Adapter
4. Boot both, then from Kali:
   ```bash
   ip a                        # find Kali's 192.168.56.x address
   nmap -sn 192.168.56.0/24    # find Metasploitable
   ```

## 📸 Snapshots
Take a snapshot of every VM right after it's set up (**Machine → Take Snapshot**). If anything breaks, roll back in seconds.
