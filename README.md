# Secure Surreal Passphrases

A web-based passphrase generator that creates memorable, grammatically-structured passphrases with high entropy for security.

## Features

- **Grammar-based generation**: Creates passphrases using proper grammatical structure (adjectives, nouns, verbs, adverbs, prepositions)
- **Customizable output**: Choose separator style (space, dash, CamelCase, none), add numbers, control capitalization, and select terminators
- **Security-focused**: Uses cryptographically secure random generation (Python's `secrets` module)
- **Entropy calculation**: Displays bits of entropy and human-readable strength for each passphrase
- **Privacy-first**: No logging, no storage, no tracking - all generation happens server-side and results are never stored
- **Rate limiting**: 60 requests per minute per IP to prevent abuse
- **Responsive design**: Works on desktop and mobile devices

## How It Works

Strong passwords are hard to remember, and memorable passwords are usually weak. This generator solves that problem by combining multiple random words into phrases that are both secure and memorable.

Each passphrase is built from a large vocabulary organized by part of speech, creating surreal but grammatical combinations like "Crisp niece promises ruin" that are easy to remember but extremely difficult to crack.

## Installation

### Requirements

- Python 3.6+
- Apache with mod_wsgi (or any WSGI-compatible server)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/passphrase.git
cd passphrase
```

2. Configure Apache to serve the WSGI application. Example Apache config:
```apache
WSGIScriptAlias /passphrase /path/to/passphrase/app.wsgi
<Directory /path/to/passphrase>
    Require all granted
</Directory>
```

3. Restart Apache:
```bash
sudo systemctl restart httpd
```

4. Access at `http://yourserver/passphrase`

## Usage

1. Visit the web interface
2. Choose complexity level (Very Short to Extra Long)
3. Customize options:
   - **Separator**: Space, Dash, CamelCase, or None
   - **Add Number**: Optionally append a random digit (1-9)
   - **Capitalize First**: Toggle first word capitalization
   - **Terminator**: None, Period, or Random Symbol
4. Click "Generate New" to create 10 new passphrases
5. Click the 📑 icon to copy any passphrase to clipboard

## Security

- All randomness uses Python's `secrets` module (cryptographically secure)
- Entropy ranges from ~35 bits (Very Short) to 100+ bits (Extra Long)
- 50+ bit passphrases would take billions of years to crack with current technology
- No passphrases are logged, stored, or transmitted to third parties
- Rate limiting prevents automated attacks

## Word Lists

Word lists are curated from the [EFF's Passphrase Wordlists](https://www.eff.org/document/passphrase-wordlists), organized by part of speech for grammatical structure.

- EFF Wordlists: Copyright © 2026 Electronic Frontier Foundation, licensed under GNU GPL v3 or later
- Application code: Copyright © 2026 Lyle Brulhart, licensed under MIT License

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The word lists used are derived from the EFF's Passphrase Wordlists and are licensed under GNU GPL v3 or later.

## Credits

- Built by [Lyle Brulhart](https://lylebrulhart.com)
- Inspired by and using word lists from the [EFF's Passphrase Wordlists](https://www.eff.org/document/passphrase-wordlists)
- Thank you to the Electronic Frontier Foundation for their excellent work on password security

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

If you find this useful, consider [buying me a coffee](https://www.buymeacoffee.com/lylebrulhart).
