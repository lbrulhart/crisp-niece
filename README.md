# Secure Surreal Passphrases

A web-based passphrase generator that creates memorable, grammatically-structured passphrases with high entropy for security.

## Why Another Password Generator?

**The Diceware Problem:** Traditional passphrase generators give you random words like "correct horse battery staple" - secure, but hard to remember because there's no connection between the words.

**The Solution:** This generates *grammatical* phrases that tell a story: "Ancient emperor travels carefully through crystal" or "Reckless penguin overthinks wildly."

Your brain naturally creates mental images from grammatical sentences. The surreal combinations are often accidentally funny, making them even more memorable. Same entropy as random words, but actually memorable.

**The Philosophy:** Entropy comes from word selection, not symbols. Numbers and special characters should be opt-in for systems that require them, not defaults that clutter otherwise clean passphrases.

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
   - **Separator**: Space (default), Dash, CamelCase, or None
   - **Capitalize**: First word (default), All words, or None
   - **Add Number**: Optionally append a random digit (1-9)
   - **Terminator**: None (default), Period, or Random Symbol
4. Click "Generate New" to create 10 new passphrases
5. Click the 📑 icon to copy any passphrase to clipboard

**Defaults:** Long (4-6 words), space separator, capitalize first word only, no number, no terminator. Clean and sentence-like: "Ancient emperor travels carefully through crystal"

## Security

- All randomness uses Python's `secrets` module (cryptographically secure)
- Entropy ranges from ~35 bits (Very Short) to 100+ bits (Extra Long)
- 50+ bit passphrases would take billions of years to crack with current technology
- No passphrases are logged, stored, or transmitted to third parties
- Rate limiting prevents automated attacks

## Word Lists

Word lists use a weighted 70/30 mix:
- **70%**: Hand-picked words chosen for clarity, memorability, and surreal combinations
- **30%**: [EFF's Long Passphrase Wordlist](https://www.eff.org/document/passphrase-wordlists) for additional entropy

Words are organized by part of speech (adjectives, nouns, verbs, adverbs, prepositions) to enable grammatical structure generation.

**Licensing:**
- EFF Wordlists: Copyright © Electronic Frontier Foundation, licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/us/)
- Application code: Copyright © 2026 Lyle Brulhart, licensed under MIT License

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The EFF word lists used are licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/us/).

## Credits

- Built by [Lyle Brulhart](https://lylebrulhart.com)
- Inspired by and using word lists from the [EFF's Passphrase Wordlists](https://www.eff.org/document/passphrase-wordlists)
- Thank you to the Electronic Frontier Foundation for their excellent work on password security

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

If you find this useful, consider [buying me a coffee](https://www.buymeacoffee.com/lylebrulhart).
