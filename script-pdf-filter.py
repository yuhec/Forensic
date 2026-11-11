#!/usr/bin/env python3
"""
Script 2 : Extraction PDF vers Markdown avec filtrage de mots
Extrait le texte d'un PDF et supprime les mots d'un dictionnaire.
"""

import os
import sys
import re
import json
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Installation de pdfplumber...")
    os.system("pip install pdfplumber")
    import pdfplumber


def load_word_dictionary(dict_path: str) -> set:
    """
    Charge un dictionnaire de mots à filtrer.
    Supporte : .txt (un mot par ligne), .json (liste ou dict avec clé 'words')
    """
    if not os.path.exists(dict_path):
        raise FileNotFoundError(f"Dictionnaire introuvable : {dict_path}")
    
    words = set()
    ext = Path(dict_path).suffix.lower()
    
    with open(dict_path, "r", encoding="utf-8") as f:
        if ext == ".json":
            data = json.load(f)
            if isinstance(data, list):
                words = set(w.lower().strip() for w in data)
            elif isinstance(data, dict) and "words" in data:
                words = set(w.lower().strip() for w in data["words"])
        else:  # .txt ou autre
            words = set(line.lower().strip() for line in f if line.strip())
    
    print(f"Dictionnaire chargé : {len(words)} mots à filtrer")
    return words


def extract_pdf_text(pdf_path: str) -> str:
    """Extrait le texte d'un fichier PDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF introuvable : {pdf_path}")
    
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages, 1):
            print(f"  Extraction page {i}/{total_pages}...", end="\r")
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    
    print(f"  Extraction terminée : {total_pages} pages")
    return "\n\n".join(text_parts)


def filter_words(text: str, words_to_remove: set) -> str:
    """
    Supprime les mots du dictionnaire du texte.
    Préserve la ponctuation et la structure.
    """
    if not words_to_remove:
        return text
    
    # Créer un pattern regex pour tous les mots à supprimer
    # \b pour les limites de mots, re.IGNORECASE pour ignorer la casse
    pattern = r'\b(' + '|'.join(re.escape(w) for w in words_to_remove) + r')\b'
    
    filtered = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
    
    # Optionnel : supprimer complètement au lieu de [REDACTED]
    # filtered = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Nettoyer les espaces multiples
    filtered = re.sub(r' +', ' ', filtered)
    filtered = re.sub(r'\n{3,}', '\n\n', filtered)
    
    return filtered.strip()


def convert_to_markdown(text: str, title: str = "Document") -> str:
    """Convertit le texte en format Markdown basique."""
    md_content = f"# {title}\n\n"
    md_content += "---\n\n"
    
    # Séparer en paragraphes
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if para:
            md_content += f"{para}\n\n"
    
    return md_content


def save_markdown(content: str, output_path: str) -> None:
    """Sauvegarde le contenu en fichier Markdown."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fichier Markdown sauvegardé : {output_path}")


def main():
    print("=" * 50)
    print("  PDF VERS MARKDOWN (avec filtrage)")
    print("=" * 50)
    
    # Chemin du dictionnaire
    dict_path = input("\nChemin du dictionnaire de mots à filtrer : ").strip()
    dict_path = dict_path.strip('"').strip("'")
    
    if not dict_path:
        print("Aucun dictionnaire fourni. Aucun filtrage ne sera appliqué.")
        words_to_remove = set()
    else:
        try:
            words_to_remove = load_word_dictionary(dict_path)
        except FileNotFoundError as e:
            print(f"Erreur : {e}")
            sys.exit(1)
    
    # Chemin du PDF
    pdf_path = input("\nChemin du fichier PDF : ").strip()
    pdf_path = pdf_path.strip('"').strip("'")
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("Erreur : Fichier PDF invalide ou introuvable.")
        sys.exit(1)
    
    print("\nExtraction du PDF en cours...")
    try:
        raw_text = extract_pdf_text(pdf_path)
    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        sys.exit(1)
    
    # Filtrage
    print("Filtrage des mots en cours...")
    filtered_text = filter_words(raw_text, words_to_remove)
    
    # Conversion en Markdown
    title = Path(pdf_path).stem.replace("_", " ").replace("-", " ").title()
    markdown_content = convert_to_markdown(filtered_text, title)
    
    # Fichier de sortie
    default_output = Path(pdf_path).with_suffix(".md")
    output_path = input(f"\nFichier de sortie [{default_output}] : ").strip()
    output_path = output_path or str(default_output)
    
    save_markdown(markdown_content, output_path)
    
    print("\n" + "=" * 50)
    print("CONVERSION TERMINÉE")
    print("=" * 50)
    
    # Stats
    original_words = len(raw_text.split())
    filtered_words = len(filtered_text.split())
    redacted_count = filtered_text.count("[REDACTED]")
    
    print(f"\nStatistiques :")
    print(f"  - Mots originaux : {original_words}")
    print(f"  - Occurrences filtrées : {redacted_count}")
    
    return output_path


if __name__ == "__main__":
    main()
