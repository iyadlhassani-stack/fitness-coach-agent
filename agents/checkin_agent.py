from core.llm_client import call_llm
import json

SYSTEM_PROMPT = """
Tu es un coach fitness et nutrition qui analyse le check-in quotidien d'un utilisateur.
À partir de son check-in du jour et de son historique récent, génère des ajustements et encouragements.
Tu dois toujours répondre en JSON valide avec exactement cette structure :
{
    "analyse": string,
    "ajustements_nutrition": [string],
    "ajustements_entrainement": [string],
    "message_motivation": string,
    "alerte": boolean
}
Ne réponds rien d'autre que le JSON. Pas de texte avant, pas de texte après.
"""

def analyze_checkin(profile: dict, checkin: dict, historique_checkins: list) -> dict:
    user_message = f"""
    Profil : {json.dumps(profile, ensure_ascii=False)}
    Check-in du jour : {json.dumps(checkin, ensure_ascii=False)}
    Historique des 7 derniers check-ins : {json.dumps(historique_checkins[-7:], ensure_ascii=False)}
    """

    raw = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        temperature=0.3
    )

    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        result = json.loads(cleaned)
        return {"success": True, "analysis": result}
    except json.JSONDecodeError:
        return {"success": False, "raw": raw, "error": "JSON invalide"}