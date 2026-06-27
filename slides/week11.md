---
marp: true
theme: default
paginate: true
header: "Software Security · Week 11"
---

# Week 11
## Memory-Safety & Exploitation
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- The C/C++ memory model & the stack
- Finding bugs with **fuzzing**
- Stack overflow → control hijack
- Mitigations + the **memory-safe language** shift
- 🎮 Game: **Fuzzing Race → Pwn the Binary**

---

## Why this still matters

- C/C++ runs the world's critical infrastructure
- Memory bugs = ~70% of severe CVEs historically
- Now a national-policy issue (CISA/ONCD roadmaps)

---

## The stack frame

```text
[ buffer ][ saved registers ][ return address ]
                                    ↑ overwrite this
```

- `gets`/`strcpy`/unchecked `memcpy` → overflow
- Overwrite return address → redirect execution

---

## Bug classes

- **CWE-121** stack overflow · **CWE-787** OOB write
- **CWE-416** use-after-free · **CWE-134** format string
- **CWE-193** off-by-one · integer overflow

---

## Fuzzing — how bugs are found today

```bash
clang -fsanitize=address,fuzzer harness.c -o fuzz && ./fuzz   # libFuzzer
afl-fuzz -i seeds -o out -- ./vuln @@                          # AFL++
```

- Coverage-guided mutation finds crashes fast
- Pair with sanitizers (ASan) for root cause

---

## Exploiting a stack overflow

1. Find offset to return address (cyclic pattern)
2. Overwrite RA → jump to `win()` / shellcode
3. Format string: `%x%x%x` leak, `%n` write

---

## Mitigations raise the bar

- **Stack canaries** — detect overwrite before return
- **ASLR** — randomize addresses
- **NX/DEP** — no code execution on the stack
- **PIE** — position-independent executables
- …each makes the same exploit harder

---

## The real fix: memory-safe languages

- **Rust / Go** remove whole bug classes by design
- CISA "Secure by Design" + ONCD: move off C/C++ for new code
- Borrow checker / bounds checks = no overflow, no UAF

---

## 💥 Game — Fuzzing Race → Pwn the Binary

1. **Round 1 (Fuzzing Race):** first team to crash the target wins
2. **Round 2 (Pwn):** exploit the overflow / format string
3. **Round 3 (Defend):** rebuild with canary+ASLR+PIE, then **rewrite in Rust**

---

## Deliverable

- Fuzzing crash + exploit script
- Annotated Ghidra/gdb analysis
- Memory-safe (Rust) rewrite + why the bug is now impossible

---

## Key takeaways

- Fuzz to find, debug to understand, mitigate to slow attackers
- Mitigations ≠ cure — memory-safe languages are the cure
- This is where the industry is moving

---

# Questions?
Next week: Software supply-chain security
