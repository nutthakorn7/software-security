# Weekly Quiz — Week 11 (Memory Safety)

**~10 min · in-class · 6 questions · low-stakes** (drop lowest). No devices / locked browser.

**Name:** Pirisa Kitichai  **Student ID:** 6631503031

## MCQ (5 × 1)
1. A buffer overflow is caused by:
   a) too little RAM  b) writing past the bounds of a buffer  c) a slow CPU  d) a missing semicolon
   Ans. B

2. Which language is **memory-safe by default**?
   a) C  b) C++  c) Rust  d) assembly
   Ans. C

3. The mitigation that randomizes memory layout to hinder exploits is:
   a) ASLR  b) TLS  c) MFA  d) CORS
   Ans. A

4. The CWE for an out-of-bounds **write** is:
   a) CWE-79  b) CWE-787  c) CWE-89  d) CWE-352
   Ans. B

5. Which tool detects memory errors at runtime during testing?
   a) Gitleaks  b) AddressSanitizer (ASan)  c) Prettier  d) curl
   Ans. B 

## Short answer — 🔒 your own work (1 × 3)
6. In the fuzzing/exploit lab, what **input** (size or shape) crashed the target, and which **memory-safety defense** would have prevented it? Then paste your **personal flag** (`FLAG{...}`) captured from the challenge.
Ans. The input that crashed the program was **68 bytes long**, which exceeded the 64-byte stack buffer. The `strcpy()` function attempted to write 69 bytes, including the null terminator, causing a stack-buffer overflow.

This vulnerability can be prevented by validating the input length before copying or using a memory-safe language such as Rust. In the hardened C build, FORTIFY_SOURCE detected the overflow and terminated the program.

**Flag captured from the local lab:** `FLAG{stack_smashing_for_fun_and_education}`