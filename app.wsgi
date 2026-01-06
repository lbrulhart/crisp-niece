#!/usr/bin/env python3
# Copyright (c) 2026 Lyle Brulhart
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

import secrets
import math
import time
import os
from collections import defaultdict

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load word lists
def load_words(path):
    with open(path) as f:
        return [w.strip() for w in f if w.strip()]

adjectives = load_words(os.path.join(script_dir, "words/adjectives.txt"))
verbs      = load_words(os.path.join(script_dir, "words/verbs.txt"))
adverbs    = load_words(os.path.join(script_dir, "words/adverbs.txt"))
nouns      = load_words(os.path.join(script_dir, "words/medium_nouns.txt"))
prepositions = load_words(os.path.join(script_dir, "words/prepositions.txt"))

word_counts = {
    "adj": len(adjectives),
    "noun": len(nouns),
    "verb": len(verbs),
    "adv": len(adverbs),
    "prep": len(prepositions),
}

# Simple rate limiting: track requests per IP
# Format: {ip: [(timestamp1, timestamp2, ...)]}
request_log = defaultdict(list)
max_requests_per_minute = 60

def is_rate_limited(ip_address):
    """Check if IP has exceeded the rate limit"""
    now = time.time()
    # Clean up old entries (older than 1 minute)
    request_log[ip_address] = [ts for ts in request_log[ip_address] if now - ts < 60]

    # Check if over limit
    if len(request_log[ip_address]) >= max_requests_per_minute:
        return True

    # Log this request
    request_log[ip_address].append(now)
    return False

templates = {
    "very_short": [
        ["adj", "noun", "verb"],
        ["noun", "verb", "adv"],
    ],
    "short": [
        ["adj", "noun", "verb", "adv"],
        ["adj", "noun", "verb", "noun"],
        ["noun", "verb", "adj", "noun"],
    ],
    "medium": [
        ["adj", "noun", "verb", "adv"],
        ["adj", "noun", "verb", "adj", "noun"],
    ],
    "long": [
        ["adj", "noun", "verb", "adv"],
        ["adj", "noun", "verb", "adj", "noun"],
        ["adj", "noun", "verb", "prep", "adj", "noun"],
    ],
    "extralong": [
        ["adj", "noun", "verb", "noun", "prep", "adj", "noun"],
        ["adj", "noun", "verb", "adv", "noun", "prep", "adj", "noun"],
        ["adj", "noun", "verb", "noun", "prep", "adj", "noun", "prep", "adj", "noun"],
    ],
}

def calculate_entropy(template):
    """Calculate bits of entropy for a given template"""
    combinations = 1
    for pos in template:
        combinations *= word_counts[pos]
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

def generate_phrase(template, separator=" ", add_number=False, capitalize_first=True, terminator='.'):
    word_lists = {
        "adj": adjectives,
        "noun": nouns,
        "verb": verbs,
        "adv": adverbs,
        "prep": prepositions,
    }

    phrase_words = []
    for pos in template:
        phrase_words.append(secrets.choice(word_lists[pos]))

    # Handle different separator types
    if separator == "":
        # CamelCase: capitalize each word and remove spaces within multi-word entries
        phrase_words = [''.join([w.capitalize() for w in word.split()]) for word in phrase_words]
        result = ''.join(phrase_words)
    elif separator is None:
        # None: no separator, respect capitalization option
        if capitalize_first:
            phrase_words[0] = phrase_words[0].capitalize()
        result = ''.join(phrase_words)
    else:
        # Space or dash: join with separator
        if capitalize_first:
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

    return result + terminator

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
        .about-text {
            color: #fff;
            font-family: Arial, sans-serif;
            max-width: 600px;
            padding: 20px;
            line-height: 1.6;
            text-align: left;
            margin-top: 20px;
        }
        .about-text p {
            margin-bottom: 1em;
        }
    </style>
</head>
<body>
    <a href="/passphrase" class="back-link">← Back to Generator</a>
    <img src="/passphrase/avatar.png" alt="About the Creator">
    <div class="about-text">
        <p>Built by someone who got tired of searching the internet for a decent passphrase generator and thought, "How hard could it be?"</p>
        <p>Turns out, pretty fun actually.</p>
        <p>After an afternoon of tinkering (and way too much debate about whether the period counts as a special character), this tool emerged: a generator that makes passphrases weird enough to remember but strong enough that even your most paranoid sysadmin would approve.</p>
        <p>Why surreal passphrases? Because "Ancient emperor travels carefully through crystal castles" is objectively more fun to type than P@ssw0rd123! and way more secure.</p>
        <p>If this saved you from yet another password reset email, consider buying me a coffee. If it didn't, well, at least you got to read about a crisp niece who promises ruin.</p>
    </div>
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
    headers = [
        ('Content-type', 'text/html; charset=utf-8'),
        ('X-Sector-5150', 'Classification: TOP SECRET // Source: The Crisp Niece // Status: Unstable')
    ]
    start_response(status, headers)

    # Parse query string for complexity level and separator
    query_string = environ.get('QUERY_STRING', '')
    complexity = 'short'  # default
    if 'level=very_short' in query_string:
        complexity = 'very_short'
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
    elif 'sep=camel' in query_string:
        separator = ''
    elif 'sep=none' in query_string:
        separator = None

    # Parse add_number option
    add_number = 'num=yes' in query_string

    # Parse capitalization option
    capitalize_first = 'cap=no' not in query_string  # default yes

    # Parse terminator option
    terminator_type = 'none'  # default none
    if 'term=period' in query_string:
        terminator_type = 'period'
    elif 'term=symbol' in query_string:
        terminator_type = 'symbol'

    # Build URL parameters
    sep_param = 'space' if separator == ' ' else ('dash' if separator == '-' else ('camel' if separator == '' else 'none'))
    num_param = '&num=yes' if add_number else ''
    cap_param = '' if capitalize_first else '&cap=no'
    term_param = '&term=symbol' if terminator_type == 'symbol' else ('&term=period' if terminator_type == 'period' else '')

    # Generate passphrases
    passphrase_items = []
    template_list = templates[complexity]
    for _ in range(10):
        template = secrets.choice(template_list)
        # Generate terminator for each phrase
        if terminator_type == 'symbol':
            terminator = secrets.choice(['!', '?', '@', '#', '$', '%', '&', '*'])
        elif terminator_type == 'none':
            terminator = ''
        else:
            terminator = '.'
        phrase = generate_phrase(template, separator, add_number, capitalize_first, terminator)
        entropy = calculate_entropy(template)
        description = entropy_description(entropy)
        # Escape single quotes for JavaScript
        escaped_phrase = phrase.replace("'", "\\'")
        passphrase_items.append(f"<li><span class='passphrase'>{phrase}</span><button class='copy-btn' onclick='copyPassphrase(this, \"{escaped_phrase}\")' title='Copy to clipboard'><svg width='16' height='16' viewBox='0 0 16 16' fill='currentColor'><path d='M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V2Z'/><path d='M2 6a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-1H6a3 3 0 0 1-3-3V6H2Z'/></svg></button><span class='entropy'>(~{entropy:.0f} bits - {description})</span></li>")

    passphrases_html = '\n'.join(passphrase_items)
    script_name = environ.get('SCRIPT_NAME', '/passphrase')

    body = f"""<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Secure Surreal Passphrases</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; max-width: 1200px; margin-left: auto; margin-right: auto; }}
.buttons {{ margin: 20px 0; display: flex; flex-wrap: wrap; gap: 5px; }}
.buttons a {{ padding: 6px 14px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 14px; white-space: nowrap; }}
.buttons a:hover {{ background: #0056b3; }}
.buttons a.active {{ background: #28a745; pointer-events: none; cursor: default; }}
.options-table {{ margin: 20px 0; }}
.option-row {{ display: grid; grid-template-columns: 150px 1fr; align-items: center; margin: 6px 0; gap: 10px; }}
.option-row strong {{ text-align: right; padding-right: 15px; }}
.option-row .buttons {{ margin: 0; display: flex; gap: 5px; flex-wrap: wrap; }}
.top-buttons {{ margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px; }}
.generate-btn {{ padding: 10px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block; }}
.generate-btn:hover {{ background: #218838; }}
.reset-btn {{ padding: 10px 30px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block; }}
.reset-btn:hover {{ background: #5a6268; }}
ul {{ list-style: none; padding: 0; }}
li {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #007bff; word-break: break-word; }}
.passphrase {{ font-size: 1.1em; user-select: all; cursor: pointer; display: inline-block; word-break: break-word; }}
.passphrase:hover {{ background: #e9ecef; padding: 2px 4px; margin: -2px -4px; border-radius: 3px; }}
.entropy {{ color: #666; font-size: 0.9em; margin-left: 10px; display: inline-block; }}
.copy-btn {{ margin-left: 10px; padding: 4px 8px; background: transparent; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 1.2em; }}
.copy-btn:hover {{ background: #f8f9fa; border-color: #007bff; }}
.copy-btn:active {{ background: #e9ecef; }}

@media (max-width: 768px) {{
  body {{ margin: 20px 10px; }}
  h1 {{ font-size: 1.5em; }}
  .option-row {{ grid-template-columns: 1fr; gap: 5px; }}
  .option-row strong {{ text-align: left; padding-right: 0; padding-bottom: 5px; }}
  .buttons:not(.option-row .buttons) {{ flex-direction: column; }}
  .buttons:not(.option-row .buttons) a {{ width: 100%; text-align: center; }}
  .buttons a {{ font-size: 13px; padding: 5px 10px; }}
  .generate-btn, .reset-btn {{ padding: 8px 20px; font-size: 14px; width: 100%; text-align: center; }}
  .top-buttons {{ flex-direction: column; }}
  .passphrase {{ font-size: 1em; }}
  .entropy {{ display: block; margin-left: 0; margin-top: 5px; }}
  li {{ padding: 8px; }}
}}

@media (max-width: 480px) {{
  body {{ margin: 15px 8px; }}
  h1 {{ font-size: 1.3em; }}
  .buttons a {{ font-size: 12px; padding: 4px 8px; }}
  .passphrase {{ font-size: 0.95em; }}
}}
</style>
<script>
function copyPassphrase(button, text) {{
  navigator.clipboard.writeText(text).then(() => {{
    // Change to checkmark SVG
    button.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg>';
    setTimeout(() => {{
      button.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V2Z"/><path d="M2 6a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-1H6a3 3 0 0 1-3-3V6H2Z"/></svg>';
    }}, 1500);
  }});
}}
</script>
</head>
<body>
<h1>Secure Surreal Passphrases</h1>

<div class='top-buttons'>
<a href='?level={complexity}&sep={sep_param}{num_param}{cap_param}{term_param}' class='generate-btn'>Generate New</a>
<a href='{script_name}' class='reset-btn'>Reset to Defaults</a>
</div>

<div class='buttons'>
<a href='?level=very_short&sep={sep_param}{num_param}{cap_param}{term_param}' class='{'active' if complexity == 'very_short' else ''}'>Very Short (3 words)</a>
<a href='?level=short&sep={sep_param}{num_param}{cap_param}{term_param}' class='{'active' if complexity == 'short' else ''}'>Short (4 words)</a>
<a href='?level=medium&sep={sep_param}{num_param}{cap_param}{term_param}' class='{'active' if complexity == 'medium' else ''}'>Medium (4-5 words)</a>
<a href='?level=long&sep={sep_param}{num_param}{cap_param}{term_param}' class='{'active' if complexity == 'long' else ''}'>Long (4-6 words)</a>
<a href='?level=extralong&sep={sep_param}{num_param}{cap_param}{term_param}' class='{'active' if complexity == 'extralong' else ''}'>Extra Long (7-10 words)</a>
</div>

<div class='options-table'>

<div class='option-row'>
<strong>Separator:</strong>
<div class='buttons'>
<a href='?level={complexity}&sep=space{num_param}{cap_param}{term_param}' class='{'active' if separator == ' ' else ''}'>Space</a>
<a href='?level={complexity}&sep=dash{num_param}{cap_param}{term_param}' class='{'active' if separator == '-' else ''}'>Dash</a>
<a href='?level={complexity}&sep=camel{num_param}{cap_param}{term_param}' class='{'active' if separator == '' else ''}'>CamelCase</a>
<a href='?level={complexity}&sep=none{num_param}{cap_param}{term_param}' class='{'active' if separator is None else ''}'>None</a>
</div></div>

<div class='option-row'>
<strong>Add Number:</strong>
<div class='buttons'>
<a href='?level={complexity}&sep={sep_param}{cap_param}{term_param}' class='{'active' if not add_number else ''}'>No</a>
<a href='?level={complexity}&sep={sep_param}&num=yes{cap_param}{term_param}' class='{'active' if add_number else ''}'>Yes</a>
</div></div>

<div class='option-row'>
<strong>Capitalize First:</strong>
<div class='buttons'>
<a href='?level={complexity}&sep={sep_param}{num_param}{term_param}' class='{'active' if capitalize_first else ''}'>Yes</a>
<a href='?level={complexity}&sep={sep_param}{num_param}&cap=no{term_param}' class='{'active' if not capitalize_first else ''}'>No</a>
</div></div>

<div class='option-row'>
<strong>Terminator:</strong>
<div class='buttons'>
<a href='?level={complexity}&sep={sep_param}{num_param}{cap_param}' class='{'active' if terminator_type == 'none' else ''}'>None</a>
<a href='?level={complexity}&sep={sep_param}{num_param}{cap_param}&term=period' class='{'active' if terminator_type == 'period' else ''}'>Period</a>
<a href='?level={complexity}&sep={sep_param}{num_param}{cap_param}&term=symbol' class='{'active' if terminator_type == 'symbol' else ''}'>Random Symbol</a>
</div></div>

</div>

<ul>
{passphrases_html}
</ul>

<div style='margin-top: 40px; padding: 20px; background: #fff3cd; border-left: 4px solid #ffc107; font-size: 0.9em;'>
<strong>Privacy Notice:</strong> All passphrases are generated server-side using cryptographically secure randomness.
Generated passphrases are <strong>not logged, stored, or transmitted</strong> to any third party.
Each generation is completely random and independent.
</div>

<div style='margin-top: 30px; text-align: center;'>
<a href='https://www.buymeacoffee.com/lylebrulhart' target='_blank'>
<img src='https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png' alt='Buy Me A Coffee' style='height: 50px; border-radius: 5px;'>
</a>
</div>

<div style='margin-top: 20px; text-align: center; color: #666; font-size: 0.85em;'>
<a href='/passphrase/about' style='color: #007bff; margin-right: 15px;'>About</a> |
Copyright &copy; 2026 | Licensed under <a href='https://opensource.org/licenses/MIT' style='color: #007bff;'>MIT License</a>
</div>

</body>
</html>"""

    return [body.encode("utf-8")]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    # Port 5150: Area 51 + Section 5150 (Involuntary Hold)
    print("Initiating Sector 5150...")
    print("Access the generator at: http://localhost:5150")
    try:
        httpd = make_server('localhost', 5150, application)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSector 5150 standby. The truth remains out there.")