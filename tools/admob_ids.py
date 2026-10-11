#!/usr/bin/env python3
"""Troca os IDs de teste do AdMob pelos reais antes da exportação.

Lê ADMOB_APP_ID, ADMOB_REWARDED_ID e ADMOB_INTERSTITIAL_ID do ambiente
(variáveis do repositório no GitHub). Sem elas, mantém os IDs de teste do Google.
Atualiza data/admob.json e a configuração admob/general/android/app_id do project.godot.
"""
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data", "admob.json")
PROJECT = os.path.join(ROOT, "project.godot")

APP_RE = re.compile(r"^ca-app-pub-\d+~\d+$")
UNIT_RE = re.compile(r"^ca-app-pub-\d+/\d+$")


def normalize(value):
    value = value.replace("\ufeff", "").replace("\\/", "/")
    for ch in ("\u200b", "\u200c", "\u200d", "\u2060", "\u00a0"):
        value = value.replace(ch, "")
    return value.strip().strip('"').strip("'").strip()


def shape(value):
    """Descreve o ID sem revelar os dígitos (o log do Actions mascara o valor inteiro)."""
    sep = "?"
    match = re.search(r"\d([^\d])\d", value)
    if match:
        char = match.group(1)
        sep = {"~": "tilde", "/": "slash", "\\": "backslash", "-": "hyphen"}.get(
            char, "U+%04X" % ord(char)
        )
    flags = []
    if "~" in value:
        flags.append("tilde")
    if "/" in value:
        flags.append("slash")
    if "\\" in value:
        flags.append("backslash")
    if any(c in value for c in "\"'"):
        flags.append("quote")
    if any(c.isspace() for c in value):
        flags.append("space")
    if any(ord(c) > 127 for c in value):
        flags.append("nonascii")
    return "len=%d sep=%s flags=%s" % (len(value), sep, ",".join(flags) or "none")


def main():
    app = normalize(os.environ.get("ADMOB_APP_ID", ""))
    rewarded = normalize(os.environ.get("ADMOB_REWARDED_ID", ""))
    inter = normalize(os.environ.get("ADMOB_INTERSTITIAL_ID", ""))
    if not (app or rewarded or inter):
        print("::warning::AdMob sem IDs reais (variáveis ADMOB_*); o build usa os IDs de TESTE.")
        return 0
    errors = []
    if not APP_RE.match(app):
        errors.append(
            "ADMOB_APP_ID deve ter o formato ca-app-pub-XXXXXXXX~YYYYYYYY (%s)"
            % shape(app)
        )
    if not UNIT_RE.match(rewarded):
        errors.append(
            "ADMOB_REWARDED_ID deve ter o formato ca-app-pub-XXXXXXXX/YYYYYYYY (%s)"
            % shape(rewarded)
        )
    if not UNIT_RE.match(inter):
        errors.append(
            "ADMOB_INTERSTITIAL_ID deve ter o formato ca-app-pub-XXXXXXXX/YYYYYYYY (%s)"
            % shape(inter)
        )
    if errors:
        for e in errors:
            print("::error::" + e)
        return 1

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    data["app_id"] = app
    data["rewarded"] = rewarded
    data["interstitial"] = inter
    with open(DATA, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent="\t") + "\n")

    with open(PROJECT, encoding="utf-8") as f:
        text = f.read()
    line = 'general/android/app_id="%s"' % app
    if re.search(r"^general/android/app_id=.*$", text, re.M):
        text = re.sub(r"^general/android/app_id=.*$", line, text, flags=re.M)
    elif re.search(r"^\[admob\]$", text, re.M):
        text = re.sub(r"^\[admob\]\n", "[admob]\n\n" + line + "\n", text, count=1, flags=re.M)
    else:
        text = text.rstrip("\n") + "\n\n[admob]\n\n" + line + "\n"
    with open(PROJECT, "w", encoding="utf-8") as f:
        f.write(text)
    print("AdMob: IDs reais aplicados (app %s)" % app)
    return 0


if __name__ == "__main__":
    sys.exit(main())
