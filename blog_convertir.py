#!/usr/bin/env python3
"""Convertit un guide HTML du site vitrine en HTML pour le blog Payhip (éditeur Quill, méthode L0011).

Usage : python3 blog_convertir.py guides/<fichier>.html > sortie.html
- enlève la nav et le lien retour ; garde le corps (sans le <h1>, le titre est saisi à part) ;
- tableaux → listes (Quill n'a pas de tableaux) ;
- liens relatifs entre guides → adresse du blog Payhip (slug = titre en minuscules sans accents ni ponctuation).
"""
import re, sys, unicodedata, pathlib, html

BLOG = "https://payhip.com/OutilsMicro/blog/guides-micro-entrepreneur"
GUIDES = pathlib.Path(__file__).parent / "guides"

def slug(titre):
    s = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s

def titre_de(fichier):
    t = fichier.read_text()
    return html.unescape(re.search(r"<title>([^<]*)</title>", t).group(1))

def table_to_list(m):
    rows = re.findall(r"<tr>(.*?)</tr>", m.group(0), flags=re.S)
    items = []
    for r in rows:
        if "<th" in r:
            continue
        cells = [re.sub(r"\s+", " ", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S)]
        if not cells:
            continue
        first = cells[0]
        rest = " — ".join(c for c in cells[1:] if c)
        items.append(f"<li><strong>{first}</strong> : {rest}</li>" if rest else f"<li>{first}</li>")
    return "<ul>" + "".join(items) + "</ul>"

def convertir(fichier):
    t = fichier.read_text()
    body = t.split("<body", 1)[1].split(">", 1)[1].rsplit("</body>", 1)[0]
    body = re.sub(r"<nav>.*?</nav>", "", body, flags=re.S)
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1, flags=re.S)
    body = re.sub(r'<p><a href="\.\./index\.html">[^<]*</a></p>', "", body)
    body = re.sub(r"<table>.*?</table>", table_to_list, body, flags=re.S)
    def lien(m):
        href = m.group(1)
        if href.startswith("http"):
            return m.group(0)
        cible = GUIDES / href.split("#")[0]
        if cible.exists():
            return m.group(0).replace(f'href="{href}"', f'href="{BLOG}/{slug(titre_de(cible))}"')
        return m.group(0).replace(f'href="{href}"', f'href="{BLOG}"')
    body = re.sub(r'<a href="([^"]+)"', lien, body)
    body = body.replace("<h2>", "<h2>").replace("<sup>", "").replace("</sup>", "")
    return re.sub(r"\n\s*\n", "\n", body).strip()

if __name__ == "__main__":
    f = pathlib.Path(sys.argv[1])
    print(convertir(f))
