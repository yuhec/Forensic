#!/usr/bin/env python3
"""
Script 3 : Générateur de compte rendu d'enquête forensic avec IA
Utilise l'API Anthropic Claude pour générer des rapports professionnels.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("Installation de anthropic...")
    os.system("pip install anthropic")
    import anthropic


# Configuration
DEFAULT_MODEL = "claude-sonnet-4-20250514"

FORENSIC_SYSTEM_PROMPT = """Tu es un ingénieur forensic expert avec plus de 15 ans d'expérience dans l'analyse d'incidents de sécurité, l'investigation numérique et la rédaction de rapports d'enquête.

Ton rôle est de générer des comptes rendus d'enquête professionnels, structurés et détaillés à partir des informations fournies.

Directives pour la rédaction :
1. Utilise un ton professionnel et objectif
2. Structure le rapport de manière claire et logique
3. Mentionne les faits sans interprétation excessive
4. Identifie les éléments clés, les timeline et les acteurs
5. Propose des recommandations basées sur les constats
6. Utilise la terminologie forensic appropriée
7. Respecte la confidentialité (pas de noms réels sauf si nécessaire)

Format de sortie : Markdown professionnel avec sections clairement définies."""


def load_file(file_path: str) -> str:
    """Charge le contenu d'un fichier texte."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_template(template_path: str) -> str:
    """Charge un template de rapport si fourni."""
    if not template_path or not os.path.exists(template_path):
        return get_default_template()
    
    return load_file(template_path)


def get_default_template() -> str:
    """Retourne un template par défaut pour le rapport forensic."""
    return """
# COMPTE RENDU D'ENQUÊTE FORENSIC

## Informations Générales
- **Référence dossier** : [À compléter]
- **Date du rapport** : {date}
- **Analyste** : [Ingénieur Forensic]
- **Classification** : Confidentiel

---

## 1. Résumé Exécutif
[Synthèse en 3-5 phrases des points clés de l'enquête]

## 2. Contexte de l'Enquête
### 2.1 Origine de la demande
### 2.2 Périmètre d'investigation
### 2.3 Objectifs

## 3. Méthodologie
[Outils et techniques utilisés]

## 4. Chronologie des Événements
[Timeline détaillée]

## 5. Analyse des Preuves
### 5.1 Preuves numériques
### 5.2 Témoignages / Transcriptions
### 5.3 Corrélations

## 6. Constats et Observations
[Points clés identifiés]

## 7. Conclusions
[Conclusions factuelles de l'enquête]

## 8. Recommandations
[Actions suggérées]

## 9. Annexes
- Liste des pièces analysées
- Logs et captures

---
*Document généré automatiquement - À valider par l'analyste responsable*
"""


def generate_forensic_report(
    transcription: str,
    template: str,
    client: anthropic.Anthropic,
    additional_context: str = ""
) -> str:
    """
    Génère un compte rendu forensic à partir de la transcription et du template.
    """
    current_date = datetime.now().strftime("%d/%m/%Y")
    template = template.replace("{date}", current_date)
    
    user_prompt = f"""À partir des éléments suivants, génère un compte rendu d'enquête forensic complet et professionnel.

## TEMPLATE DE RAPPORT À SUIVRE :
{template}

## TRANSCRIPTION / DONNÉES SOURCE :
{transcription}

{f"## CONTEXTE ADDITIONNEL :{chr(10)}{additional_context}" if additional_context else ""}

---

Instructions :
1. Remplis toutes les sections du template avec les informations pertinentes
2. Extrait les faits clés, dates, personnes et événements mentionnés
3. Organise chronologiquement les informations
4. Identifie les anomalies ou points d'attention
5. Propose des recommandations concrètes
6. Reste factuel et objectif

Génère le rapport complet en Markdown :"""

    print("Génération du rapport en cours (cela peut prendre quelques instants)...")
    
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=8000,
        system=FORENSIC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    return response.content[0].text


def save_report(content: str, output_path: str) -> None:
    """Sauvegarde le rapport généré."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Rapport sauvegardé : {output_path}")


def main():
    print("=" * 60)
    print("  GÉNÉRATEUR DE COMPTE RENDU FORENSIC (IA)")
    print("=" * 60)
    
    # Vérification de la clé API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = input("\nClé API Anthropic (ANTHROPIC_API_KEY) : ").strip()
        if not api_key:
            print("Erreur : Clé API requise.")
            print("Définissez ANTHROPIC_API_KEY ou entrez-la manuellement.")
            sys.exit(1)
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Fichier de transcription (sortie du script 1)
    print("\n[1] Fichier source (transcription du script 1)")
    transcription_path = input("    Chemin du fichier texte : ").strip()
    transcription_path = transcription_path.strip('"').strip("'")
    
    if not transcription_path or not os.path.exists(transcription_path):
        print("Erreur : Fichier de transcription invalide.")
        sys.exit(1)
    
    transcription = load_file(transcription_path)
    print(f"    → Chargé : {len(transcription)} caractères")
    
    # Template (optionnel - sortie du script 2)
    print("\n[2] Template de rapport (sortie du script 2, optionnel)")
    template_path = input("    Chemin du template [Entrée = défaut] : ").strip()
    template_path = template_path.strip('"').strip("'")
    
    template = load_template(template_path)
    if template_path and os.path.exists(template_path):
        print(f"    → Template personnalisé chargé")
    else:
        print(f"    → Template par défaut utilisé")
    
    # Contexte additionnel
    print("\n[3] Contexte additionnel (optionnel)")
    additional = input("    Informations supplémentaires [Entrée = aucun] : ").strip()
    
    # Génération
    print("\n" + "-" * 60)
    try:
        report = generate_forensic_report(
            transcription=transcription,
            template=template,
            client=client,
            additional_context=additional
        )
    except anthropic.APIError as e:
        print(f"Erreur API : {e}")
        sys.exit(1)
    
    # Sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_output = f"rapport_forensic_{timestamp}.md"
    
    output_path = input(f"\nFichier de sortie [{default_output}] : ").strip()
    output_path = output_path or default_output
    
    save_report(report, output_path)
    
    print("\n" + "=" * 60)
    print("  RAPPORT GÉNÉRÉ AVEC SUCCÈS")
    print("=" * 60)
    print(f"\n→ Fichier : {output_path}")
    print("\nAperçu du rapport :")
    print("-" * 40)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    
    return output_path


if __name__ == "__main__":
    main()
