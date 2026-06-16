# Multi-Algorithm Text Encryption & Decryption System

A Flask web app that encrypts and decrypts text using three algorithms — Caesar, XOR, and the custom Mossab Rotating Cipher (MRC) — with full step-by-step output.

## Screenshots

### Home
![Home page](screenshots/home.png)

### History & Performance Chart
![History page](screenshots/history.png)

### Login
![Login page](screenshots/login.png)

### Register
![Register page](screenshots/register.png)

## Features

- Text input or `.txt` file upload
- Three algorithms: Caesar, XOR, MRC
- Step-by-step encryption and decryption details
- Download encrypted / decrypted output (`.txt`)
- Encryption history stored in SQLite
- Execution time measured in milliseconds
- Performance comparison chart
- User accounts with login (each user sees only their own records)

## Tech Stack

- Python 3
- Flask, Flask-Login
- SQLite
- HTML, CSS, Jinja2
- Chart.js

## Project Structure

```
project/
├── app.py              # Flask routes, file handling, database, login
├── encryption.py       # Caesar, XOR and MRC cipher logic
├── requirements.txt    # Python dependencies
├── README.md
├── .gitignore
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── history.html
│   ├── login.html
│   └── register.html
├── static/
│   └── style.css
├── screenshots/        # Images used in this README
└── uploads/            # Uploaded .txt files (ignored by git)
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:5000 in a browser.


## Algorithms

| Algorithm | Encryption | Decryption |
|-----------|------------|------------|
| Caesar | `E(x) = (x + k) mod 26` | `D(x) = (x - k + 26) mod 26` |
| XOR | `E(x) = x XOR k` | `D(x) = E(x) XOR k` |
| MRC | `Ei = ASCII(Ci) + k + i`, then reverse | reverse, then `Di = ASCII(Ei) - k - i` |

Example: `HELLO` with key `3` → MRC → `VRQIK` → `HELLO`.

## Custom Algorithm — Mossab Rotating Cipher (MRC)

Implemented in `encryption.py`. Encryption runs in two steps: each character is shifted by `ASCII(char) + key + position` (the position makes repeated letters encrypt differently), then the whole string is reversed. Decryption reverses the string first, then subtracts `key + position` from each character's ASCII value to recover the original text.

## How the Bonus Features Were Implemented

**Level 1 — Download buttons.** The result page has two small forms that POST the encrypted or decrypted text to the `/download` route in `app.py`. The route writes the text into an in-memory buffer (`io.BytesIO`) and returns it with `send_file(..., as_attachment=True)`, so the browser downloads it as `encrypted.txt` or `decrypted.txt`.

**Level 2 — Encryption history (SQLite).** On startup, `init_db()` creates a `history` table in `history.db`. Each time text is processed, the `/encrypt` route inserts a row (algorithm, original text, encrypted text, decrypted text, key, timings and a timestamp). The `/history` page reads those rows and lists them in a table.

**Level 3 — Execution time.** Inside `/encrypt`, `time.perf_counter()` is read just before and after each operation; the difference is multiplied by 1000 to get milliseconds, rounded, shown on the result page, and saved to the database.

**Level 4 — Performance chart.** The `/history` route averages the encryption and decryption times per algorithm and passes them to the template, where Chart.js draws a bar chart comparing the three algorithms.

**Level 5 — User authentication.** Flask-Login manages the user session. Passwords are hashed with Werkzeug's `generate_password_hash` and verified with `check_password_hash` (plain passwords are never stored). Each history row is tagged with a `user_id`, so a logged-in user only sees their own records, while anonymous use is still allowed.

## Input Validation

The registration form checks that fields are filled, the username is at least 3 characters and uses only letters/numbers/underscore, the password is at least 6 characters, and the two password fields match — before the account is created. The encryption form checks that text is provided (typed or uploaded), the key is a whole number, and only `.txt` files are accepted for upload.
