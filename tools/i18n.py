#!/usr/bin/env python3
"""Ferramenta de i18n do Bone Tribe.

Os arquivos res://i18n/pt_BR.csv, en_US.csv e es_419.csv sao a fonte da verdade.
Este script so ajuda a inserir/atualizar linhas nos 3 ao mesmo tempo e a validar.

Uso:
  python3 tools/i18n.py check
  python3 tools/i18n.py upsert arquivo.tsv   (colunas: key<TAB>pt_BR<TAB>en_US<TAB>es_419)
"""
import csv
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "i18n")
LOCALES = [("pt_BR", "pt_BR"), ("en_US", "en_US"), ("es_419", "es_419")]


def _path(name):
    return os.path.join(ROOT, name + ".csv")


def load(name):
    rows = {}
    order = []
    p = _path(name)
    if not os.path.exists(p):
        return rows, order
    with open(p, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r, None)
        for line in r:
            if not line:
                continue
            rows[line[0]] = line[1] if len(line) > 1 else ""
            order.append(line[0])
    return rows, order


def save(name, header, rows, order):
    with open(_path(name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(["keys", header])
        for k in order:
            w.writerow([k, rows[k]])


def upsert(entries):
    """entries: lista de (key, pt, en, es)."""
    for idx, (name, header) in enumerate(LOCALES):
        rows, order = load(name)
        for e in entries:
            key, text = e[0], e[idx + 1]
            if key not in rows:
                order.append(key)
            rows[key] = text
        save(name, header, rows, order)


def check():
    data = [load(n) for n, _ in LOCALES]
    keys = [set(d[0].keys()) for d in data]
    ok = True
    allk = set().union(*keys)
    for (name, _), ks, d in zip(LOCALES, keys, data):
        missing = sorted(allk - ks)
        if missing:
            ok = False
            print(f"[{name}] faltando {len(missing)}: {missing[:10]}")
        empty = [k for k, v in d[0].items() if not v.strip()]
        if empty:
            ok = False
            print(f"[{name}] vazias: {empty[:10]}")
        if len(d[1]) != len(set(d[1])):
            ok = False
            print(f"[{name}] chaves duplicadas")
    print(f"{len(allk)} chaves, {'OK' if ok else 'ERRO'}")
    return ok


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        sys.exit(0 if check() else 1)
    elif cmd == "upsert":
        entries = []
        with open(sys.argv[2], encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) != 4:
                    print("linha invalida:", line)
                    sys.exit(1)
                entries.append(tuple(parts))
        upsert(entries)
        check()
