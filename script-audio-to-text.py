#!/usr/bin/env python3
"""
Script 1 : Transcription audio vers texte
Utilise OpenAI Whisper pour convertir un fichier audio en texte.
"""

import os
import sys
from pathlib import Path

try:
    import whisper
except ImportError:
    print("Installation de whisper en cours...")
    os.system("pip install openai-whisper")
    import whisper


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """
    Transcrit un fichier audio en texte avec Whisper.
    
    Args:
        audio_path: Chemin vers le fichier audio
        model_size: Taille du modèle ('tiny', 'base', 'small', 'medium', 'large')
    
    Returns:
        Texte transcrit
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Fichier audio introuvable : {audio_path}")
    
    print(f"Chargement du modèle Whisper ({model_size})...")
    model = whisper.load_model(model_size)
    
    print(f"Transcription en cours de : {audio_path}")
    result = model.transcribe(audio_path, language="fr")
    
    return result["text"]


def save_transcription(text: str, output_path: str) -> None:
    """Sauvegarde la transcription dans un fichier texte."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Transcription sauvegardée dans : {output_path}")


def main():
    print("=" * 50)
    print("  TRANSCRIPTION AUDIO VERS TEXTE (Whisper)")
    print("=" * 50)
    
    # Demander le chemin du fichier audio
    audio_path = input("\nEntrez le chemin du fichier audio : ").strip()
    audio_path = audio_path.strip('"').strip("'")  # Nettoyer les guillemets
    
    if not audio_path:
        print("Erreur : Aucun chemin fourni.")
        sys.exit(1)
    
    # Vérifier l'existence du fichier
    if not os.path.exists(audio_path):
        print(f"Erreur : Le fichier '{audio_path}' n'existe pas.")
        sys.exit(1)
    
    # Choix du modèle
    print("\nModèles disponibles :")
    print("  1. tiny   (rapide, moins précis)")
    print("  2. base   (équilibré) [défaut]")
    print("  3. small  (meilleur)")
    print("  4. medium (très bon)")
    print("  5. large  (meilleur, lent)")
    
    model_choice = input("\nChoisissez un modèle (1-5) [2] : ").strip() or "2"
    models = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large"}
    model_size = models.get(model_choice, "base")
    
    # Transcription
    try:
        transcription = transcribe_audio(audio_path, model_size)
        
        # Générer le nom du fichier de sortie
        input_path = Path(audio_path)
        output_path = input_path.with_suffix(".txt")
        
        # Demander confirmation pour le fichier de sortie
        custom_output = input(f"\nFichier de sortie [{output_path}] : ").strip()
        if custom_output:
            output_path = custom_output
        
        save_transcription(transcription, str(output_path))
        
        print("\n" + "=" * 50)
        print("TRANSCRIPTION TERMINÉE")
        print("=" * 50)
        print(f"\nAperçu (500 premiers caractères) :\n{transcription[:500]}...")
        
        return str(output_path)
        
    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
