# 🐚 Bash cheat sheet

> Bash is the language your terminal speaks. A script is just commands saved in a file.

## 🧱 Skeleton of every script

```bash
#!/bin/bash
# what this script does, in one line

set -euo pipefail   # stop on errors, unset variables, or failed pipes

echo "Hello, $(whoami)"
```

Run it:

```bash
chmod +x hello.sh   # make it executable (once)
./hello.sh
```

## 📦 Variables & input

```bash
name="kali"              # no spaces around =
echo "Hi $name"          # use it with $
read -p "Target IP: " ip # ask the user
echo "First argument: $1, count: $#, all: $*"
today=$(date +%F)        # $(...) puts a command's output in a variable
```

## 🔀 If / else

```bash
if [ -f notes.txt ]; then
  echo "notes.txt exists"
elif [ -d notes ]; then
  echo "notes is a folder"
else
  echo "nothing there"
fi
```

| Test | True when |
|---|---|
| `-f file` | file exists |
| `-d dir` | folder exists |
| `-z "$x"` | `$x` is empty |
| `"$a" = "$b"` | strings match |
| `$n -gt 5` | number greater than 5 (`-lt`, `-eq`, `-ge`, `-le`) |

## 🔁 Loops

```bash
for f in *.md; do echo "found $f"; done

for i in {1..5}; do echo "level $i"; done

while read -r line; do
  echo "line: $line"
done < list.txt
```

## 🧩 Functions

```bash
banner() {
  echo "=== $1 ==="
}
banner "STATUS"
```

## ✂️ Text tools

```bash
grep -i "open" scan.txt            # lines containing 'open'
cut -d: -f1 /etc/passwd            # field 1, split on ':'  → usernames
sort list.txt | uniq -c            # count duplicates
awk '{print $1}' scan.txt          # first column
sed 's/old/new/g' file.txt         # replace text (prints result)
wc -l file.txt                     # count lines
```

## 🧠 Exit codes
Every command returns a number when it finishes. `0` = success, anything else = error.

```bash
ping -c1 127.0.0.1 >/dev/null && echo "up" || echo "down"
echo $?   # exit code of the last command
```
