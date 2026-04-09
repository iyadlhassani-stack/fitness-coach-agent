import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents.profiling_agent import extract_profile
from agents.nutrition_agent import generate_nutrition_plan
from agents.training_agent import generate_training_plan
from agents.validation_agent import validate_plans
from memory.user_memory import save_profile, load_profile, profile_exists, update_profile

def run_pipeline(user_id: str, user_input: str) -> dict:
    result = {}

    # Étape 1 — Extraction du profil
    print("🔍 Extraction du profil...")
    profiling_result = extract_profile(user_input)
    if not profiling_result["success"]:
        return {"error": "Échec de l'extraction du profil", "details": profiling_result}

    profile = profiling_result["profile"]
    result["profile"] = profile

    # Étape 2 — Sauvegarde en mémoire
    print("💾 Sauvegarde du profil...")
    if profile_exists(user_id):
        update_profile(user_id, {"profile": profile})
    else:
        save_profile(user_id, {"profile": profile})

    # Étape 3 — Génération du plan nutrition
    print("🥗 Génération du plan nutrition...")
    nutrition_result = generate_nutrition_plan(profile)
    if not nutrition_result["success"]:
        return {"error": "Échec de la génération du plan nutrition", "details": nutrition_result}

    nutrition_plan = nutrition_result["plan"]
    result["nutrition"] = nutrition_plan

    # Étape 4 — Génération du plan entraînement
    print("💪 Génération du plan entraînement...")
    training_result = generate_training_plan(profile)
    if not training_result["success"]:
        return {"error": "Échec de la génération du plan entraînement", "details": training_result}

    training_plan = training_result["plan"]
    result["training"] = training_plan

    # Étape 5 — Validation de la cohérence
    print("✅ Validation des plans...")
    validation_result = validate_plans(profile, nutrition_plan, training_plan)
    if not validation_result["success"]:
        return {"error": "Échec de la validation", "details": validation_result}

    result["validation"] = validation_result["validation"]

    # Étape 6 — Mise à jour mémoire avec les plans générés
    update_profile(user_id, {
        "nutrition_plan": nutrition_plan,
        "training_plan": training_plan,
        "validation": validation_result["validation"]
    })

    print("✅ Pipeline terminé.")
    return result