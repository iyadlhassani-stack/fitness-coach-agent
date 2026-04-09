import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.llm_client import call_llm
import json

SYSTEM_PROMPT = """
Tu es un nutritionniste expert.
À partir du profil utilisateur fourni, génère un plan alimentaire hebdomadaire adapté.
Tu dois toujours répondre en JSON valide avec exactement cette structure :
{
    "calories_journalieres": number,
    "proteines_g": number,
    "glucides_g": number,
    "lipides_g": number,
    "repas": {
        "petit_dejeuner": [string],
        "dejeuner": [string],
        "diner": [string],
        "collations": [string]
    },
    "conseils": [string]
}
Ne réponds rien d'autre que le JSON. Pas de texte avant, pas de texte après.
"""

def generate_nutrition_plan(profile: dict) -> dict:
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