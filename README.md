# 2FA Decoder

`2FA Decoder` is a lightweight desktop utility for generating time-based one-time passwords (TOTP) from a copied 2FA secret.

It is built with Python, Tkinter, and `pyotp`, with a simple workflow focused on speed:

- click the input field to paste a secret from the clipboard
- decode the current TOTP code instantly
- click the large code to copy it back to the clipboard

## Features

- Clean desktop UI built with Tkinter
- Supports raw Base32 secrets
- Supports full `otpauth://` URIs
- Live 30-second refresh progress bar
- One-click copy for the current code
- Lightweight single-file implementation

## Tech Stack

- Python 3
- Tkinter
- [pyotp](https://pyauth.github.io/pyotp/)

## Getting Started

1. Clone the repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python 2fa_decoder.py
```

## How It Works

The app reads a secret from the clipboard, normalizes it, and generates the active TOTP code using the standard 30-second interval. If the clipboard contains a full `otpauth://` link, the app extracts the `secret` parameter automatically.

## Use Cases

- Quick access to 2FA codes during development or testing
- Local decoding of exported TOTP secrets
- Small portfolio example of a Python desktop utility

## Project Structure

```text
.
|-- 2fa_decoder.py
|-- requirements.txt
|-- LICENSE
`-- README.md
```

## Notes

- This project is intended as a small desktop helper and portfolio sample.
- Secrets are handled locally in memory and are not sent anywhere.

## License

This project is available under the [MIT License](LICENSE).
