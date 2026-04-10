import streamlit as st
from core.orchestrator import run_pipeline
from memory.user_memory import load_profile, profile_exists, save_to_history, load_history

st.set_page_config(page_title="Fitness Coach AI", page_icon="💪", layout="wide")

st.title("💪 Fitness Coach AI")
st.caption("Ton coach personnel fitness & nutrition propulsé par l'IA")

# Sidebar
with st.sidebar:
    st.header("👤 Ton profil")
    user_id = st.text_input("Ton prénom (identifiant)", value="user1")

    if profile_exists(user_id):
        st.success(f"Profil existant pour **{user_id}**")
        data = load_profile(user_id)
        if "profile" in data:
            p = data["profile"]
            st.write(f"🎯 Objectif : {p.get('objectif', '-')}")
            st.write(f"⚖️ Poids : {p.get('poids_kg', '-')} kg")
            st.write(f"📅 Niveau : {p.get('niveau', '-')}")
    else:
        st.info("Aucun profil trouvé.")

    # Historique
    st.divider()
    st.header("🕓 Historique")
    history = load_history(user_id)
    if not history:
        st.caption("Aucun plan généré pour l'instant.")
    else:
        for i, entry in enumerate(reversed(history)):
            with st.expander(f"📅 {entry['date']}"):
                p = entry.get("profile", {})
                st.write(f"🎯 {p.get('objectif', '-')} — {p.get('niveau', '-')}")
                n = entry.get("nutrition", {})
                st.write(f"🥗 {n.get('calories_journalieres', '-')} kcal/jour")
                t = entry.get("training", {})
                st.write(f"💪 {t.get('jours_entrainement', '-')} jours/semaine")
                v = entry.get("validation", {})
                score = v.get("score", "-")
                st.write(f"✅ Score cohérence : {score}/100")

# Formulaire
st.subheader("📋 Dis-nous qui tu es")

col1, col2 = st.columns(2)

with col1:
    prenom = st.text_input("Prénom")
    age = st.number_input("Âge", min_value=10, max_value=80, value=25)
    poids = st.number_input("Poids (kg)", min_value=30, max_value=200, value=75)
    taille = st.number_input("Taille (cm)", min_value=100, max_value=220, value=175)
    sexe = st.radio("Sexe", ["Homme", "Femme"], horizontal=True)

with col2:
    objectif = st.selectbox("🎯 Objectif", [
        "Perdre du gras",
        "Prendre du muscle",
        "Perdre du gras et prendre du muscle",
        "Maintien"
    ])
    niveau = st.selectbox("📊 Niveau", [
        "Débutant",
        "Intermédiaire",
        "Avancé"
    ])
    jours = st.select_slider("📅 Jours disponibles par semaine",
        options=[2, 3, 4, 5, 6], value=3)
    restrictions = st.multiselect("🥗 Restrictions alimentaires", [
        "Aucune", "Halal", "Végétarien", "Végétalien", "Sans gluten", "Sans lactose"
    ], default=["Aucune"])

remarques = st.text_area("💬 Remarques supplémentaires (facultatif)",
    placeholder="Blessures, préférences, contraintes particulières...")

if st.button("🚀 Générer mon programme", type="primary"):
    if not prenom:
        st.warning("Entre ton prénom pour continuer.")
    else:
        restrictions_str = ", ".join(restrictions) if restrictions else "Aucune"
        user_input = f"""
        Je m'appelle {prenom}, j'ai {age} ans, je pèse {poids}kg pour {taille}cm.
        Je suis un {sexe.lower()}.
        Mon objectif est : {objectif}.
        Mon niveau est : {niveau}.
        Je suis disponible {jours} jours par semaine.
        Restrictions alimentaires : {restrictions_str}.
        Remarques : {remarques if remarques else 'Aucune'}.
        """

        with st.spinner("Génération de ton programme personnalisé..."):
            result = run_pipeline(user_id, user_input)

        if "error" in result:
            st.error(f"Erreur : {result['error']}")
        else:
            # Sauvegarde dans l'historique
            save_to_history(user_id, result)

            st.subheader("👤 Profil extrait")
            st.json(result["profile"])

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🥗 Plan Nutrition")
                n = result["nutrition"]
                st.metric("Calories/jour", f"{n['calories_journalieres']} kcal")
                st.metric("Protéines", f"{n['proteines_g']}g")
                st.metric("Glucides", f"{n['glucides_g']}g")
                st.metric("Lipides", f"{n['lipides_g']}g")
                st.write("**Repas types :**")
                for repas, items in n["repas"].items():
                    with st.expander(repas.replace("_", " ").capitalize()):
                        for item in items:
                            st.write(f"• {item}")
                st.write("**Conseils nutrition :**")
                for conseil in n["conseils"]:
                    st.write(f"✅ {conseil}")

            with col2:
                st.subheader("💪 Plan Entraînement")
                t = result["training"]
                st.metric("Jours/semaine", t["jours_entrainement"])
                st.metric("Durée séance", f"{t['duree_seance_minutes']} min")
                st.write("**Programme :**")
                for jour, contenu in t["programme"].items():
                    with st.expander(f"{jour.replace('_', ' ').capitalize()} — {contenu['nom']}"):
                        for ex in contenu["exercices"]:
                            st.write(f"• **{ex['nom']}** — {ex['series']} séries × {ex['repetitions']} reps | repos {ex['repos_secondes']}s")
                st.write("**Conseils entraînement :**")
                for conseil in t["conseils"]:
                    st.write(f"✅ {conseil}")

            st.subheader("✅ Validation des plans")
            v = result["validation"]
            score = v["score"]
            couleur = "green" if score >= 80 else "orange" if score >= 60 else "red"
            st.markdown(f"**Score de cohérence : :{couleur}[{score}/100]**")
            st.write(v["resume"])
            if v["problemes"]:
                st.warning("**Problèmes détectés :**")
                for p in v["problemes"]:
                    st.write(f"⚠️ {p}")
            if v["corrections"]:
                st.info("**Corrections suggérées :**")
                for c in v["corrections"]:
                    st.write(f"🔧 {c}")
            st.caption(f"Validation effectuée en {v.get('attempts', 1)} tentative(s)")

            st.rerun()