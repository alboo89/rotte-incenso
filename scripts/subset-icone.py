#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rigenera il font Material Symbols ridotto alle sole icone usate dal sito.
Da rilanciare se si aggiungono icone nuove (nei template, nei dati o dal CMS):
    python3 scripts/subset-icone.py
Richiede: pip install fonttools brotli
"""
from fontTools.ttLib import TTFont
import subprocess, os, re, glob, json

# 1) raccoglie i nomi icona da TUTTE le fonti: template, markdown, JSON dei contenuti, JS
icone = set()
for f in glob.glob('src/**/*.njk', recursive=True) + ['src/assets/brand.js']:
    s = open(f, encoding='utf-8').read()
    icone |= set(re.findall(r'material-symbols-outlined[^>]*>\s*([a-z_]+)\s*<', s))
for f in glob.glob('src/destinazioni/*.md'):
    m = re.search(r'icona: "([a-z_]+)"', open(f, encoding='utf-8').read())
    if m: icone.add(m.group(1))
def json_icone(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'icona' and isinstance(v, str): icone.add(v)
            else: json_icone(v)
    elif isinstance(o, list):
        for v in o: json_icone(v)
for f in glob.glob('src/_data/*.json'):
    json_icone(json.load(open(f, encoding='utf-8')))
icone |= {'menu', 'close'}  # impostate via JavaScript

# 2) margine per il CMS: icone plausibili per un sito di viaggi, gia' pronte
EXTRA = {'explore', 'hiking', 'sailing', 'beach_access', 'spa', 'coffee', 'public', 'map',
         'schedule', 'star', 'groups', 'photo_camera', 'flight', 'train', 'directions_boat',
         'nightlight', 'sunny', 'landscape', 'holiday_village', 'texture'}
icone |= EXTRA
icone = sorted(icone)
print(f"{len(icone)} icone nel subset:", ", ".join(icone))

# 3) pota le legature del font originale e genera il subset
f = TTFont('node_modules/material-symbols/material-symbols-outlined.woff2')
cmap = f.getBestCmap()
g2c = {v: chr(k) for k, v in cmap.items()}
tenute = 0
for lookup in f['GSUB'].table.LookupList.Lookup:
    for st in lookup.SubTable:
        st = st.ExtSubTable if lookup.LookupType == 7 else st
        if not hasattr(st, 'ligatures'): continue
        for primo in list(st.ligatures.keys()):
            nuovo = [lig for lig in st.ligatures[primo]
                     if g2c.get(primo, '?') + ''.join(g2c.get(c, '?') for c in lig.Component) in icone]
            tenute += len(nuovo)
            if nuovo: st.ligatures[primo] = nuovo
            else: del st.ligatures[primo]
f.save('/tmp/msym-pruned.woff2')
assert tenute == len(icone), f"ATTENZIONE: trovate {tenute} legature per {len(icone)} icone (nome inesistente?)"

subprocess.run(["pyftsubset", "/tmp/msym-pruned.woff2",
    "--text=abcdefghijklmnopqrstuvwxyz_",
    "--layout-features=rlig,rclt,ccmp,liga", "--flavor=woff2",
    "--output-file=src/assets/fonts/material-symbols-outlined-subset.woff2"], check=True)
kb = os.path.getsize("src/assets/fonts/material-symbols-outlined-subset.woff2") / 1024
print(f"OK: {tenute} legature, font da {kb:.1f} KB")
