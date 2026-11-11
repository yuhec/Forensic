#!/usr/bin/env python3
"""
Pipeline Complet : Audio → Texte → Filtrage → Rapport Forensic
Orchestre les 3 scripts en une seule exécution.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Imports des fonctions des autres scripts
# (Assurez-vous que les 3 scripts sont dans le même dossier)

def check_dependencies():
    """Vérifie et installe les dépendances nécessaires."""
    deps = ["openai-whisper", "pdfplumber", "anthropic"]
    for dep in deps:
        try:
            __import__(dep.replace("-", "_").split()[0])
        except ImportError:
            print(f"Installation de {dep}...")
            os.system(f"pip install {dep}")

def run_pipeline():
    print("=" * 70)
    print("  PIPELINE FORENSIC COMPLET")
    print("  Audio → Transcription → Template → Rapport IA")
    print("=" * 70)
    
    check_dependencies()
    
    import whisper
    import pdfplumber
    import anthropic
    
    # ─────────────────────────────────────────────────────────────────
    # ÉTAPE 1 : Transcription Audio
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("ÉTAPE 1/3 : TRANSCRIPTION AUDIO")
    print("─" * 70)
    
    audio_path = input("\n[Audio] Chemin du fichier audio : ").strip().strip('"\'')
    
    if not os.path.exists(audio_path):
        print(f"Erreur : Fichier audio introuvable : {audio_path}")
        sys.exit(1)
    
    print("\nChargement du modèle Whisper (base)...")
    model = whisper.load_model("base")
    
    print(f"Transcription de : {audio_path}")
    result = model.transcribe(audio_path, language="fr")
    transcription = result["text"]
    
    # Sauvegarder la transcription
    trans_output = Path(audio_path).with_suffix(".txt")
    with open(trans_output, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"✓ Transcription sauvegardée : {trans_output}")
    
    # ─────────────────────────────────────────────────────────────────
    # ÉTAPE 2 : Extraction Template PDF (optionnel)
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("ÉTAPE 2/3 : TEMPLATE DEPUIS PDF (optionnel)")
    print("─" * 70)
    
    pdf_path = input("\n[Template] Chemin du PDF template [Entrée = ignorer] : ").strip().strip('"\'')
    
    template = None
    if pdf_path and os.path.exists(pdf_path):
        # Dictionnaire de filtrage
        dict_path = input("[Filtre] Chemin du dictionnaire [Entrée = aucun] : ").strip().strip('"\'')
        
        words_to_remove = set()
        if dict_path and os.path.exists(dict_path):
            import json
            with open(dict_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    words_to_remove = set(w.lower() for w in data)
                elif "words" in data:
                    words_to_remove = set(w.lower() for w in data["words"])
        
        # Extraction PDF
        print(f"\nExtraction du PDF : {pdf_path}")
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        template = "\n\n".join(text_parts)
        
        # Filtrage
        if words_to_remove:
            import re
            pattern = r'\b(' + '|'.join(re.escape(w) for w in words_to_remove) + r')\b'
            template = re.sub(pattern, '[REDACTED]', template, flags=re.IGNORECASE)
        
        print(f"✓ Template extrait ({len(template)} caractères)")
    else:
        print("→ Aucun template PDF, utilisation du template par défaut")
    
    # ─────────────────────────────────────────────────────────────────
    # ÉTAPE 3 : Génération du Rapport Forensic
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("ÉTAPE 3/3 : GÉNÉRATION DU RAPPORT FORENSIC")
    print("─" * 70)
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = input("\n[API] Clé API Anthropic : ").strip()
    
    if not api_key:
        print("Erreur : Clé API requise pour la génération.")
        sys.exit(1)
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Template par défaut si non fourni
    if not template:
        template = f"""# COMPTE RENDU D'ENQUÊTE FORENSIC
## Informations Générales
- **Date** : {datetime.now().strftime("%d/%m/%Y")}
- **Analyste** : Ingénieur Forensic

## 1. Résumé Exécutif
## 2. Contexte
## 3. Chronologie des Événements
## 4. Analyse des Preuves
## 5. Constats
## 6. Conclusions
## 7. Recommandations
"""
    
    system_prompt = """Tu es un ingénieur forensic expert. Génère un compte rendu 
d'enquête professionnel, structuré et détaillé à partir des informations fournies.
Sois factuel, objectif et utilise la terminologie forensic appropriée."""
    
    user_prompt = f"""Génère un compte rendu d'enquête forensic complet.

TEMPLATE À SUIVRE :
{template}

TRANSCRIPTION SOURCE :
{transcription}

Génère le rapport en Markdown :"""
    
    print("\nGénération du rapport avec Claude...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    report = response.content[0].text
    
    # Sauvegarde finale
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"rapport_forensic_{timestamp}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # ─────────────────────────────────────────────────────────────────
    # RÉSUMÉ
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  PIPELINE TERMINÉ AVEC SUCCÈS")
    print("=" * 70)
    print(f"""
Fichiers générés :
  1. Transcription : {trans_output}
  2. Rapport final : {report_path}

Aperçu du rapport :
{"─" * 50}
{report[:800]}...
""")


if __name__ == "__main__":
    run_pipeline()
