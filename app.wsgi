#!/usr/bin/env python3
# Copyright (c) 2026 Lyle Brulhart
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

import secrets
import math
import time
from collections import defaultdict

# Load word lists
def load_words(path):
    with open(path) as f:
        return [w.strip() for w in f if w.strip()]

ADJECTIVES = load_words("/var/www/passphrase/words/adjectives.txt")
VERBS      = load_words("/var/www/passphrase/words/verbs.txt")
ADVERBS    = load_words("/var/www/passphrase/words/adverbs.txt")
NOUNS      = load_words("/var/www/passphrase/words/medium_nouns.txt")
PREPOSITIONS = load_words("/var/www/passphrase/words/prepositions.txt")

WORD_COUNTS = {
    "ADJ": len(ADJECTIVES),
    "NOUN": len(NOUNS),
    "VERB": len(VERBS),
    "ADV": len(ADVERBS),
    "PREP": len(PREPOSITIONS),
}

# Simple rate limiting: track requests per IP
# Format: {ip: [(timestamp1, timestamp2, ...)]}
REQUEST_LOG = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 60

def is_rate_limited(ip_address):
    """Check if IP has exceeded rate limit"""
    now = time.time()
    # Clean up old entries (older than 1 minute)
    REQUEST_LOG[ip_address] = [ts for ts in REQUEST_LOG[ip_address] if now - ts < 60]

    # Check if over limit
    if len(REQUEST_LOG[ip_address]) >= MAX_REQUESTS_PER_MINUTE:
        return True

    # Log this request
    REQUEST_LOG[ip_address].append(now)
    return False

TEMPLATES = {
    "veryshort": [
        ["ADJ", "NOUN", "VERB"],
        ["NOUN", "VERB", "ADV"],
    ],
    "short": [
        ["ADJ", "NOUN", "VERB", "ADV"],
        ["ADJ", "NOUN", "VERB", "NOUN"],
        ["NOUN", "VERB", "ADJ", "NOUN"],
    ],
    "medium": [
        ["ADJ", "NOUN", "VERB", "ADV"],
        ["ADJ", "NOUN", "VERB", "ADJ", "NOUN"],
    ],
    "long": [
        ["ADJ", "NOUN", "VERB", "ADV"],
        ["ADJ", "NOUN", "VERB", "ADJ", "NOUN"],
        ["ADJ", "NOUN", "VERB", "PREP", "ADJ", "NOUN"],
    ],
    "extralong": [
        ["ADJ", "NOUN", "VERB", "ADV", "PREP", "ADJ", "NOUN"],
        ["ADJ", "NOUN", "VERB", "PREP", "ADJ", "NOUN", "PREP", "ADJ", "NOUN"],
        ["ADJ", "NOUN", "VERB", "ADV", "PREP", "ADJ", "NOUN", "PREP", "ADJ", "NOUN"],
    ],
}

def calculate_entropy(template):
    """Calculate bits of entropy for a given template"""
    combinations = 1
    for pos in template:
        combinations *= WORD_COUNTS[pos]
    return math.log2(combinations)

def entropy_description(bits):
    """Convert entropy bits to human-readable strength description"""
    if bits < 35:
        return "moderate"
    elif bits < 50:
        return "strong"
    elif bits < 65:
        return "very strong"
    elif bits < 75:
        return "extremely strong"
    else:
        return "virtually uncrackable"

def generate_phrase(template, separator=" ", add_number=False):
    word_lists = {
        "ADJ": ADJECTIVES,
        "NOUN": NOUNS,
        "VERB": VERBS,
        "ADV": ADVERBS,
        "PREP": PREPOSITIONS,
    }

    phrase_words = []
    for pos in template:
        phrase_words.append(secrets.choice(word_lists[pos]))

    # If no separator, use CamelCase (capitalize each word)
    if separator == "":
        # Handle multi-word entries by capitalizing each word and removing spaces
        phrase_words = [''.join([w.capitalize() for w in word.split()]) for word in phrase_words]
    else:
        phrase_words[0] = phrase_words[0].capitalize()

    result = separator.join(phrase_words)

    # Add a random number at the end if requested (1-9, no zero to avoid confusion with O)
    if add_number:
        number = str(secrets.randbelow(9) + 1)
        if separator == " ":
            # Space separator: add space before number
            result += " " + number
        else:
            # Dash or CamelCase: just append the number
            result += number

    return result + "."

# This is the WSGI entry point Apache expects
def application(environ, start_response):
    # Handle about page
    path = environ.get('PATH_INFO', '')
    if path.endswith('/about'):
        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)

        about_html = """<!DOCTYPE html>
<html>
<head>
    <title>About - Secure Surreal Passphrases</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            flex-direction: column;
        }
        img {
            max-width: 90vw;
            max-height: 90vh;
            object-fit: contain;
        }
        .back-link {
            position: fixed;
            top: 20px;
            left: 20px;
            color: #fff;
            background: rgba(0, 123, 255, 0.8);
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-family: Arial, sans-serif;
        }
        .back-link:hover {
            background: rgba(0, 86, 179, 0.9);
        }
    </style>
</head>
<body>
    <a href="/passphrase" class="back-link">← Back to Generator</a>
    <img src="/passphrase/avatar.png" alt="About the Creator">
</body>
</html>"""
        return [about_html.encode("utf-8")]

    # Get client IP for rate limiting
    client_ip = environ.get('REMOTE_ADDR', 'unknown')

    # Check rate limit
    if is_rate_limited(client_ip):
        status = '429 Too Many Requests'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        body = "<html><body><h1>Rate Limit Exceeded</h1><p>Please wait a moment before generating more passphrases.</p></body></html>"
        return [body.encode("utf-8")]

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)

    # Parse query string for complexity level and separator
    query_string = environ.get('QUERY_STRING', '')
    complexity = 'short'  # default
    if 'level=veryshort' in query_string:
        complexity = 'veryshort'
    elif 'level=medium' in query_string:
        complexity = 'medium'
    elif 'level=long' in query_string:
        complexity = 'long'
    elif 'level=extralong' in query_string:
        complexity = 'extralong'

    # Parse separator
    separator = ' '  # default (Space)
    if 'sep=space' in query_string:
        separator = ' '
    elif 'sep=dash' in query_string:
        separator = '-'
    elif 'sep=none' in query_string:
        separator = ''

    # Parse add_number option
    add_number = 'num=yes' in query_string

    body = "<html><head><title>Secure Surreal Passphrases</title>"
    body += "<style>"
    body += "body { font-family: Arial, sans-serif; margin: 40px; }"
    body += ".buttons { margin: 20px 0; }"
    body += ".buttons a { padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }"
    body += ".buttons a:hover { background: #0056b3; }"
    body += ".buttons a.active { background: #28a745; pointer-events: none; cursor: default; }"
    body += ".generate-btn { padding: 10px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block; }"
    body += ".generate-btn:hover { background: #218838; }"
    body += ".reset-btn { padding: 10px 30px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block; }"
    body += ".reset-btn:hover { background: #5a6268; }"
    body += "ul { list-style: none; padding: 0; }"
    body += "li { margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #007bff; }"
    body += ".passphrase { font-size: 1.1em; user-select: all; cursor: pointer; display: inline-block; }"
    body += ".passphrase:hover { background: #e9ecef; padding: 2px 4px; margin: -2px -4px; border-radius: 3px; }"
    body += ".entropy { color: #666; font-size: 0.9em; margin-left: 10px; }"
    body += ".copy-btn { margin-left: 10px; padding: 4px 8px; background: transparent; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 1.2em; }"
    body += ".copy-btn:hover { background: #f8f9fa; border-color: #007bff; }"
    body += ".copy-btn:active { background: #e9ecef; }"
    body += "</style>"
    body += "<script>"
    body += "function copyPassphrase(text) {"
    body += "  navigator.clipboard.writeText(text).then(() => {"
    body += "    event.target.textContent = '✓';"
    body += "    setTimeout(() => { event.target.textContent = '📑'; }, 1500);"
    body += "  });"
    body += "}"
    body += "</script></head><body>"
    body += "<h1>Secure Surreal Passphrases</h1>"

    sep_param = 'space' if separator == ' ' else ('dash' if separator == '-' else 'none')
    num_param = '&num=yes' if add_number else ''

    body += "<div style='margin-bottom: 20px;'>"
    body += f"<a href='?level={complexity}&sep={sep_param}{num_param}' class='generate-btn'>Generate New</a>"
    body += " "
    body += f"<a href='{environ.get('SCRIPT_NAME', '/passphrase')}' style='padding: 10px 30px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block;'>Reset to Defaults</a>"
    body += "</div>"

    body += "<div class='buttons'>"
    body += f"<a href='?level=veryshort&sep={sep_param}{num_param}' class='{'active' if complexity == 'veryshort' else ''}'>Very Short (3 words)</a>"
    body += f"<a href='?level=short&sep={sep_param}{num_param}' class='{'active' if complexity == 'short' else ''}'>Short (4 words)</a>"
    body += f"<a href='?level=medium&sep={sep_param}{num_param}' class='{'active' if complexity == 'medium' else ''}'>Medium (4-5 words)</a>"
    body += f"<a href='?level=long&sep={sep_param}{num_param}' class='{'active' if complexity == 'long' else ''}'>Long (4-6 words)</a>"
    body += f"<a href='?level=extralong&sep={sep_param}{num_param}' class='{'active' if complexity == 'extralong' else ''}'>Extra Long (7-10 words)</a>"
    body += "</div>"

    body += "<div class='buttons' style='margin-top: 10px;'>"
    body += "<strong style='margin-right: 10px;'>Separator:</strong>"
    body += f"<a href='?level={complexity}&sep=none{num_param}' class='{'active' if separator == '' else ''}'>CamelCase</a>"
    body += f"<a href='?level={complexity}&sep=space{num_param}' class='{'active' if separator == ' ' else ''}'>Space</a>"
    body += f"<a href='?level={complexity}&sep=dash{num_param}' class='{'active' if separator == '-' else ''}'>Dash</a>"
    body += "</div>"

    body += "<div class='buttons' style='margin-top: 10px;'>"
    body += "<strong style='margin-right: 10px;'>Add Number:</strong>"
    body += f"<a href='?level={complexity}&sep={sep_param}&num=yes' class='{'active' if add_number else ''}'>Yes</a>"
    body += f"<a href='?level={complexity}&sep={sep_param}' class='{'active' if not add_number else ''}'>No</a>"
    body += "</div>"

    body += "<ul>"

    templates = TEMPLATES[complexity]
    for _ in range(10):
        template = secrets.choice(templates)
        phrase = generate_phrase(template, separator, add_number)
        entropy = calculate_entropy(template)
        description = entropy_description(entropy)
        # Escape single quotes for JavaScript
        escaped_phrase = phrase.replace("'", "\\'")
        body += f"<li><span class='passphrase'>{phrase}</span><button class='copy-btn' onclick='copyPassphrase(\"{escaped_phrase}\")' title='Copy to clipboard'>📑</button><span class='entropy'>(~{entropy:.0f} bits - {description})</span></li>"

    body += "</ul>"
    body += "<div style='margin-top: 40px; padding: 20px; background: #fff3cd; border-left: 4px solid #ffc107; font-size: 0.9em;'>"
    body += "<strong>Privacy Notice:</strong> All passphrases are generated server-side using cryptographically secure randomness. "
    body += "Generated passphrases are <strong>not logged, stored, or transmitted</strong> to any third party. "
    body += "Each generation is completely random and independent."
    body += "</div>"
    body += "<div style='margin-top: 30px; text-align: center;'>"
    body += "<a href='https://www.buymeacoffee.com/lylebrulhart' target='_blank'>"
    body += "<img src='https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png' alt='Buy Me A Coffee' style='height: 50px; border-radius: 5px;'>"
    body += "</a>"
    body += "</div>"
    body += "<div style='margin-top: 20px; text-align: center; color: #666; font-size: 0.85em;'>"
    body += "<a href='/passphrase/about' style='color: #007bff; margin-right: 15px;'>About</a> | "
    body += "Copyright &copy; 2026 | Licensed under <a href='https://opensource.org/licenses/MIT' style='color: #007bff;'>MIT License</a>"
    body += "</div>"
    body += "</body></html>"

    return [body.encode("utf-8")]
