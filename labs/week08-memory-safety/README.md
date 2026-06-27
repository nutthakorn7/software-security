# Week 8 — Memory-Safety Vulnerabilities

**CWE:** CWE-787 (out-of-bounds write), CWE-121 (stack overflow), CWE-416 (use-after-free)

## Objectives
- Explain the C/C++ memory model and the stack frame.
- Exploit a classic stack buffer overflow to redirect control flow.
- Understand modern mitigations: ASLR, stack canaries, NX/DEP — and why memory-safe languages (Rust/Go) help.

## Lab (isolated sandbox VM)
A small vulnerable C binary is provided.
```bash
gcc -fno-stack-protector -z execstack -no-pie vuln.c -o vuln   # teaching build
```
1. Find the offset to the return address (pattern/cyclic).
2. Overwrite the return address to reach a `win()` function.
3. Re-compile **with** canaries + ASLR + PIE and observe how the exploit breaks.
4. Rewrite the routine with bounds-safe APIs.

## Deliverable
Exploit script + explanation of how each mitigation changes the attack.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Memory_Management_Cheat_Sheet.html
