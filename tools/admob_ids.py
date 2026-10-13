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


def as_unit(value, app):
    """Aceita o bloco com barra ou, se for outro ID, com o til no lugar da barra.

    O secret às vezes é gravado no formato do app (ca-app-pub-XXX~YYY). Isso só vira
    bloco quando o valor é diferente do ID do app — copiar o app nos dois blocos
    não inventa um anúncio.
    """
    if UNIT_RE.match(value):
        return value
    if APP_RE.match(value) and value != app:
        return value.replace("~", "/", 1)
    return value


def main():
    app = normalize(os.environ.get("ADMOB_APP_ID", ""))
    raw_rewarded = normalize(os.environ.get("ADMOB_REWARDED_ID", ""))
    raw_inter = normalize(os.environ.get("ADMOB_INTERSTITIAL_ID", ""))
    rewarded = as_unit(raw_rewarded, app)
    inter = as_unit(raw_inter, app)
    if not (app or raw_rewarded or raw_inter):
        print("::warning::AdMob sem IDs reais (variáveis ADMOB_*); o build usa os IDs de TESTE.")
        return 0
    if app and not APP_RE.match(app):
        print(
            "::error::ADMOB_APP_ID deve ter o formato ca-app-pub-XXXXXXXX~YYYYYYYY (%s)"
            % shape(app)
        )
        return 1

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    # Secret repetido do app, ou sem barra, não é um bloco. Mantém o ID de teste
    # desse bloco para o AAB sair; o aviso fica no log da execução.
    test_units = []
    if not UNIT_RE.match(rewarded):
        test_units.append("ADMOB_REWARDED_ID")
        rewarded = data["rewarded"]
    if not UNIT_RE.match(inter):
        test_units.append("ADMOB_INTERSTITIAL_ID")
        inter = data["interstitial"]
    if test_units:
        print(
            "::warning::%s não é um bloco (formato ca-app-pub-XXX/YYY). "
            "O valor atual repete o ID do app ou não tem barra, então esse AAB "
            "usa o bloco de TESTE do Google. Troque o secret e rode de novo para anúncio real."
            % " e ".join(test_units)
        )
    if not app:
        data["rewarded"] = rewarded
        data["interstitial"] = inter
        with open(DATA, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent="\t") + "\n")
        print("AdMob: sem ID de app real; blocos atualizados a partir dos secrets.")
        return 0

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
    if test_units:
        print("AdMob: ID do app aplicado; blocos de teste (%s)" % ", ".join(test_units))
    else:
        print("AdMob: IDs reais aplicados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
