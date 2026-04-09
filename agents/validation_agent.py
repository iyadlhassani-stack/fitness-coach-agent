import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.llm_client import call_llm
import json

SYSTEM_PROMPT = """
Tu es un expert en nutrition et fitness chargé de valider la cohérence entre un plan alimentaire et un plan d'entraînement.
Tu dois vérifier :
1. Les calories sont suffisantes pour supporter l'entraînement
2. Les protéines sont adaptées à l'objectif (prise de masse, sèche, maintien)
3. Le volume d'entraînement est réaliste pour le niveau indiqué
4. Les deux plans sont cohérents avec l'objectif de l'utilisateur

Tu dois toujours répondre en JSON valide avec exactement cette structure :
{
    "valide": boolean,
    "score": number,
    "problemes": [string],
    "corrections": [string],
    "resume": string
}
Ne réponds rien d'autre que le JSON. Pas de texte avant, pas de texte après.
"""

def validate_plans(profile: dict, nutrition_plan: dict, training_plan: dict, max_retries: int = 3) -> dict:
    user_message = f"""
    Profil utilisateur : {json.dumps(profile, ensure_ascii=False)}
    Plan alimentaire : {json.dumps(nutrition_plan, ensure_ascii=False)}
    Plan d'entraînement : {json.dumps(training_plan, ensure_ascii=False)}
    """

    for attempt in range(max_retries):
        raw = call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.1
        )

        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            result = json.loads(cleaned)
            result["attempts"] = attempt + 1
            return {"success": True, "validation": result}
        except json.JSONDecodeError:
            if attempt == max_retries - 1:
                return {"success": False, "raw": raw, "error": "JSON invalide après 3 tentatives"}
            continue