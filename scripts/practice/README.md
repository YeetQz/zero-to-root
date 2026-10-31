# 🐚 Practice scripts

Your forge for the ⚒️ **Scriptsmith** quest. Save your own bash scripts here.

| Script | What it teaches |
|---|---|
| [`hello-hunter.sh`](hello-hunter.sh) | Variables, `$(...)`, a function, an if/else, a loop, colours |

Run it:

```bash
chmod +x scripts/practice/hello-hunter.sh
./scripts/practice/hello-hunter.sh
```

**Ideas for your own:**
1. 🗂️ `new-log.sh`: copies `logs/_template.md` to today's date and opens it in nano
2. 🔄 `update-kali.sh`: runs the apt update + upgrade and prints how long it took
3. 🧪 `lab-scan.sh`: asks for a lab IP, checks it starts with `192.168.17.`, then runs your usual nmap commands and saves the output in `scans/` (ignored by git)

Number 3 has a safety check on purpose: a good tool refuses targets outside your scope.
