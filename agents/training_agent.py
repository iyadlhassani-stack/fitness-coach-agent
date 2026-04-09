import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.llm_client import call_llm
import json

SYSTEM_PROMPT = """
Tu es un coach sportif expert.
À partir du profil utilisateur fourni, génère un plan d'entraînement hebdomadaire adapté.
Tu dois toujours répondre en JSON valide avec exactement cette structure :
{
    "jours_entrainement": number,
    "duree_seance_minutes": number,
    "objectif_seance": string,
    "programme": {
        "jour_1": {"nom": string, "exercices": [{"nom": string, "series": number, "repetitions": string, "repos_secondes": number}]},
        "jour_2": {"nom": string, "exercices": [{"nom": string, "series": number, "repetitions": string, "repos_secondes": number}]},
        "jour_3": {"nom": string, "exercices": [{"nom": string, "series": number, "repetitions": string, "repos_secondes": number}]}
    },
    "conseils": [string]
}
Adapte le nombre de jours au profil. Ne réponds rien d'autre que le JSON.
"""

def generate_training_plan(profile: dict) -> dict:
    user_message = f"Voici le profil de l'utilisateur : {json.dumps(profile, ensure_ascii=False)}"

    raw = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        temperature=0.3
    )

    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        plan = json.loads(cleaned)
        return {"success": True, "plan": plan}
    except json.JSONDecodeError:
        return {"success": False, "raw": raw, "error": "JSON invalide"}