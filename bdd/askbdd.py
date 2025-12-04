import re
import os

def rechercher_constructeur(mac_input, fichier_bdd= os.path.dirname(os.path.abspath(__file__)) + "/bdd.txt"):
    if fichier_bdd is None:
        dossier = os.path.dirname(os.path.abspath(__file__))
        fichier_bdd = os.path.join(dossier, "bdd", "bdd.txt")

    if not os.path.exists(fichier_bdd):
        print(f"ERREUR : fichier BDD introuvable → {fichier_bdd}")
        return None, None
    prefixes = {}
    regex_prefixe = re.compile(r"^([0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2})\s+\(hex\)")

    with open(fichier_bdd, "r", encoding="utf-8") as f:
        lignes = f.readlines()
    i = 0
    while i < len(lignes):
        ligne = lignes[i].strip()
        match = regex_prefixe.match(ligne)
        if match:
            prefixe_mac = match.group(1).replace("-", "").upper()
            constructeur = ligne.replace(match.group(1), "").replace("(hex)", "").strip()
            i += 1
            adresse = ""
            while i < len(lignes) and lignes[i].strip() and not regex_prefixe.match(lignes[i]):
                contenu = lignes[i].strip()
                if "(base 16)" in contenu:
                    i += 1
                    continue
                adresse += " " + contenu
                i += 1
            constructeur = constructeur.strip() if constructeur else None
            adresse = adresse.replace("\d", " ").strip() if adresse else None

            prefixes[prefixe_mac] = (constructeur, adresse)
        else:
            i += 1
    mac_clean = re.sub(r"[^0-9A-Fa-f]", "", mac_input).upper()
    if len(mac_clean) < 6:
        return None, None
    prefixe_mac = mac_clean[:6]
    return prefixes.get(prefixe_mac, (None, None))