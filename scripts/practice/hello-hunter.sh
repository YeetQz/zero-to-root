#!/bin/bash
# 🐚 Practice script #1: a tiny "who am I and where am I" report.
# Read it line by line: every line is explained. Then copy it and make your own.

set -euo pipefail                      # stop if anything fails

# --- colours (ANSI escape codes) ---
BLUE='\033[38;5;39m'
GOLD='\033[38;5;220m'
DIM='\033[2m'
RESET='\033[0m'

# --- a function: prints a label and a value on one line ---
show() {
  printf "  ${DIM}%-10s${RESET} %s\n" "$1" "$2"   # %-10s pads the label to 10 characters
}

echo -e "${BLUE}[SYSTEM]${RESET} Scanning the player..."
sleep 0.5

show "Player"   "$(whoami)"                         # $(...) runs a command and uses its output
show "Machine"  "$(hostname)"
show "Kernel"   "$(uname -r)"
show "Date"     "$(date '+%A %d %B %Y')"
show "Uptime"   "$(uptime -p)"

# ip -4 -o addr lists IPv4 addresses one per line; awk keeps column 2 (interface) and 4 (address);
# grep -v drops 'lo' (loopback); tr joins the lines; '|| true' stops set -e quitting if nothing matches
ips=$(ip -4 -o addr show | awk '{print $2": "$4}' | grep -v '^lo' | tr '\n' ' ' || true)
show "Networks" "${ips:-none}"                       # ${var:-none} = use 'none' if empty

# --- an if/else: are we root? ---
if [ "$(id -u)" -eq 0 ]; then
  echo -e "\n  ${GOLD}You are root. Use that power carefully.${RESET}"
else
  echo -e "\n  ${DIM}You are a normal user. Good habit: only sudo when you need to.${RESET}"
fi

# --- a loop: count files in a few folders ---
echo
for dir in ~/Desktop ~/Downloads ~/zero-to-root/logs; do
  if [ -d "$dir" ]; then
    show "$(basename "$dir")" "$(find "$dir" -maxdepth 1 -type f | wc -l) files"
  fi
done
echo
