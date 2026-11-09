#!/usr/bin/env python3
# Copyright (c) 2026 Lyle Brulhart
# Licensed under the MIT License
# https://opensource.org/licenses/MIT
#
# Word lists are curated from the EFF's Passphrase Wordlists
# Copyright (c) 2026 Electronic Frontier Foundation
# Licensed under GNU GPL v3 or later
# https://www.eff.org/document/passphrase-wordlists

import json
import os
import time
from collections import defaultdict


class PassphraseApp:
    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.max_requests_per_minute = 60
        self.request_log = defaultdict(list)

        preps = self.load_words("prepositions.txt")
        # [hand-picked, large] per part of speech; the page picks between them 70/30
        words = {
            "adj": [self.load_words("adjectives.txt"), self.load_words("adjectives_large.txt")],
            "noun": [self.load_words("medium_nouns.txt"), self.load_words("nouns_large.txt")],
            "verb": [self.load_words("verbs.txt"), self.load_words("verbs_large.txt")],
            "adv": [self.load_words("adverbs.txt"), self.load_words("adverbs_large.txt")],
            "prep": [preps, preps],
        }
        # Explicit utf-8: under mod_wsgi the default encoding can be ASCII, and the page has em dashes.
        with open(os.path.join(script_dir, "page.html"), encoding="utf-8") as f:
            self.page = f.read().replace("__WORDS__", json.dumps(words, separators=(",", ":")))

    def load_words(self, name):
        with open(os.path.join(self.script_dir, "words", name), encoding="utf-8") as f:
            return [w.strip() for w in f if w.strip()]

    def is_rate_limited(self, ip_address):
        now = time.time()
        self.request_log[ip_address] = [ts for ts in self.request_log[ip_address] if now - ts < 60]

        if len(self.request_log[ip_address]) >= self.max_requests_per_minute:
            return True

        self.request_log[ip_address].append(now)
        return False

    def handle_about(self, start_response, base_path=''):
        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)

        about_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>About - Secure Surreal Passphrases</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            flex-direction: column;
        }}
        img {{
            max-width: 90vw;
            max-height: 90vh;
            object-fit: contain;
        }}
        .back-link {{
            position: fixed;
            top: 20px;
            left: 20px;
            color: #fff;
            background: rgba(0, 123, 255, 0.8);
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-family: Arial, sans-serif;
        }}
        .back-link:hover {{
            background: rgba(0, 86, 179, 0.9);
        }}
        .about-text {{
            color: #fff;
            font-family: Arial, sans-serif;
            max-width: 600px;
            padding: 20px;
            line-height: 1.6;
            text-align: left;
            margin-top: 20px;
        }}
        .about-text p {{
            margin-bottom: 1em;
        }}
    </style>
</head>
<body>
    <a href="{base_path}/" class="back-link">← Back to Generator</a>
    <img src="{base_path}/creator.png" alt="About the Creator">
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

    def handle_rate_limit(self, start_response):
        status = '429 Too Many Requests'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        body = "<html><body><h1>Rate Limit Exceeded</h1><p>Please wait a moment before generating more passphrases.</p></body></html>"
        return [body.encode("utf-8")]

    def handle_creator_image(self, start_response):
        try:
            with open(os.path.join(self.script_dir, 'creator.png'), 'rb') as f:
                image_data = f.read()
            start_response('200 OK', [('Content-type', 'image/png')])
            return [image_data]
        except FileNotFoundError:
            start_response('404 Not Found', [('Content-type', 'text/plain')])
            return [b'Image not found']

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        base_path = environ.get('SCRIPT_NAME', '')

        if path.endswith('/about') or path.endswith('/about/'):
            return self.handle_about(start_response, base_path)

        if path.endswith('/creator.png'):
            return self.handle_creator_image(start_response)

        client_ip = environ.get('REMOTE_ADDR', 'unknown')
        if self.is_rate_limited(client_ip):
            return self.handle_rate_limit(start_response)

        status = '200 OK'
        headers = [
            ('Content-type', 'text/html; charset=utf-8'),
            ('X-Sector-5150', 'Classification: TOP SECRET // Source: The Crisp Niece // Status: Unstable')
        ]
        start_response(status, headers)

        return [self.page.replace("__BASE_PATH__", base_path).encode("utf-8")]


app = PassphraseApp(os.path.dirname(os.path.abspath(__file__)))


def application(environ, start_response):
    return app(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print("Access the generator at: http://localhost:5150")
    try:
        httpd = make_server('localhost', 5150, application)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSector 5150 standby. The truth remains out there.")