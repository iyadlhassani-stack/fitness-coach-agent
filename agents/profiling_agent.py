import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.llm_client import call_llm
import json

SYSTEM_PROMPT = """
Tu es un coach fitness et nutrition professionnel.
Ton rôle est d'analyser le profil d'un utilisateur et d'extraire les informations clés.
Tu dois toujours répondre en JSON valide avec exactement cette structure :
{
    "nom": string,
    "age": number,
    "poids_kg": number,
    "taille_cm": number,
    "sexe": string,
    "objectif": string,
    "niveau": string,
    "jours_disponibles": number,
    "restrictions_alimentaires": [string],
    "remarques": string
}
Ne réponds rien d'autre que le JSON. Pas de texte avant, pas de texte après.
"""

def extract_profile(user_input: str) -> dict:
    raw = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_input,
        temperature=0.2
    )

    # Nettoyage au cas où le LLM ajoute des backticks
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        profile = json.loads(cleaned)
        return {"success": True, "profile": profile}
    except json.JSONDecodeError:
        return {"success": False, "raw": raw, "error": "JSON invalide"}