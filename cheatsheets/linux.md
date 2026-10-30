# 🐧 Linux cheat sheet

> Filling this in as I go through OverTheWire Bandit.

## 📂 Moving around
| Command | What it does |
|---|---|
| `pwd` | Where am I? |
| `ls -la` | List everything, including hidden files |
| `cd ~` · `cd ..` · `cd -` | Home · up one folder · back to previous |
| `cat file` · `less file` | Print a file · scroll through it (`q` to quit) |
| `find / -name "*.conf" 2>/dev/null` | Search the whole system, hide errors |
| `grep -ri "password" .` | Search inside files, case-insensitive |

## 🔐 Permissions
| Command | What it does |
|---|---|
| `whoami` · `id` | Which user am I, and my groups |
| `sudo -l` | What am I allowed to run as root? |
| `chmod +x script.sh` | Make a file executable |
| `ls -l` → `-rwxr-xr--` | owner · group · everyone (read/write/execute) |

## 🌐 Network
| Command | What it does |
|---|---|
| `ip a` | My IP addresses |
| `ping -c 3 host` | Is it reachable? |
| `ss -tulpn` | Which ports is my machine listening on? |
| `curl -I http://site` | Fetch just the HTTP headers |

## 🔧 Services & packages
```bash
sudo apt update && sudo apt full-upgrade -y   # update Kali
sudo systemctl start ssh                      # start a service
sudo systemctl stop ssh                       # stop it again
systemctl status ssh                          # is it running?
```

## 🪄 Pipes & tricks
```bash
cat file | sort | uniq -c     # count unique lines
history | grep nmap           # find a command I ran before
command > out.txt             # save output (overwrite)
command >> out.txt            # append
```
