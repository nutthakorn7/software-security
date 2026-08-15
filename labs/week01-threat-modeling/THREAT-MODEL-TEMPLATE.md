# Threat Model — <app name>

## 1. Data-flow diagram
                   [ Web Client ]
                    /    |     \
                   /     |      \
             /notes   /upload   /files/<name>
                 \       |       /
                  \      |      /
             - - - - - - - - - - - -
                  INTERNET TRUST
                     BOUNDARY
             - - - - - - - - - - - -
                       |
                       v
                 [ Flask App ]
                    /     \
                   /       \
                  v         v
             [notes.db]  [uploads/]
               SQLite      files
![alt text](image-1.png)


## 2. Elements & trust boundaries
| Element                | Type (process/store/entity/flow) | Trust boundary crossed?                                        |
| ---------------------- | -------------------------------- | -------------------------------------------------------------- |
| Web client             | External entity                  | Yes (Internet → app)                                           |
| Flask app              | Process                          | Yes (receives data from Web client and accesses DB/filesystem) |
| SQLite DB (`notes.db`) | Data store                       | Yes (Flask app → DB)                                           |
| `uploads/` store       | Data store                       | Yes (Flask app → filesystem / uploaded files)                  |


## 3. STRIDE analysis
| Element | S | T | R | I | D | E |
|---|---|---|---|---|---|---|

| /notes |Impersonation due to missing authentication |Modify notes through crafted requests |User actions cannot be reliably traced |Notes may be exposed to unauthorized users |Large numbers of requests can overload the database |Exploiting the Flask app's privileges to access the DB |

| /upload |Upload files as another user |Modify or replace uploaded files |Deny having uploaded a file |Sensitive uploaded files may be exposed |Large file uploads can exhaust storage/resources |Upload malicious scripts or executable files |

| /files/<name> |Access files without proper authentication |Modify files that should be read-only |File access cannot be properly attributed |Path traversal may expose files outside uploads/ |Excessive file requests can overload the server/storage |Path traversal or unsafe file handling may lead to access to sensitive files or code execution |

## 4. Top 5 risks (likelihood × impact) + mitigation
1.Path Traversal in /files/<name> — High × High
An attacker may use paths such as ../ to access files outside the uploads/ directory.
Mitigation: Use secure_filename() or a filename whitelist and ensure the resolved path always stays inside uploads/.

2.Malicious File Upload in /upload — High × High
An attacker may upload executable or malicious files.
Mitigation: Restrict file types and sizes, generate filenames on the server, store uploads outside the web root, and disable code execution in the upload directory.

3.Unauthorized File Access / IDOR — Medium-High × High
A user may access another user's files if authorization checks are missing.
Mitigation: Verify file ownership/authorization before serving files and use random, unpredictable file IDs instead of easily guessed filenames.

4.Denial of Service through File Upload — High × Medium-High
Attackers may upload very large or numerous files, exhausting disk space or server resources.
Mitigation: Set MAX_CONTENT_LENGTH, limit upload frequency/number, and monitor available storage.

5.SQL Injection / Data Tampering in /notes — Medium × High
If user input is directly concatenated into SQL queries, attackers may read or modify database contents.
Mitigation: Use parameterized queries/ORM, validate input, and follow the principle of least privilege.



///////////////////////////////////////////////////////////////////////////////////