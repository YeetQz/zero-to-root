# 🐢 Fixing VirtualBox "turtle mode" (Hyper-V / VBS)

## 😵 Symptoms
- `watchdog: BUG: soft lockup - CPU#1 stuck for 34s!`
- `rcu: rcu_preempt self-detected stall on CPU` / `timer wakeup didn't happen for 184217 jiffies`
- Kali freezes on the dragon splash screen
- `vmwgfx ... seems to be running on an unsupported hypervisor`
- Reinstalling Kali changes nothing

## 🔎 Diagnosis
| Where | Bad 🐢 | Good 🚀 |
|---|---|---|
| `msinfo32` → Virtualization-based security | Running | Not enabled |
| `msinfo32` → bottom line | "A hypervisor has been detected" | Four "Hyper-V - ... : Yes" lines |
| VM → Machine → Session Information → Runtime | Execution Engine: **native API** | Execution Engine: **VT-x/AMD-V** |
| Nested Paging / Unrestricted Execution | Inactive | Active |

## 🛠️ Fix (Windows, admin terminal)
1. Windows Security → Device Security → Core Isolation → **Memory Integrity: Off**
2. `optionalfeatures` → untick **Hyper-V**, **Virtual Machine Platform**, **Windows Hypervisor Platform**, **Windows Sandbox**
3. In **Terminal (Admin)**:
   ```powershell
   bcdedit /set hypervisorlaunchtype off
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 0 /f
   bcdedit /enum '{current}' | findstr /i hypervisor     # should say: Off
   reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard"   # "unable to find" = good
   ```
4. **Restart** (not Shut down) and check `msinfo32` again.

## 🧠 Gotchas I hit
- The terminal must say **Administrator** in the title, or `bcdedit` silently fails.
- In PowerShell, `{current}` needs quotes: `'{current}'`.
- Unticking the features **wasn't enough**: the registry value `EnableVirtualizationBasedSecurity = 1` kept VBS on.

## ↩️ Undo
Turning this off lowers some Windows protections. To turn it back on (this breaks VirtualBox speed again):
```powershell
bcdedit /set hypervisorlaunchtype auto
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 1 /f
```
