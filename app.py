import sys
import os
sys.path.append(os.path.dirname(__file__))
import streamlit as st
from core.orchestrator import run_pipeline
from memory.user_memory import load_profile, profile_exists

st.set_page_config(page_title="Fitness Coach AI", page_icon="💪", layout="wide")

st.title("💪 Fitness Coach AI")
st.caption("Ton coach personnel fitness & nutrition propulsé par l'IA")

# Sidebar — identifiant utilisateur
with st.sidebar:
    st.header("👤 Ton profil")
    user_id = st.text_input("Ton prénom (identifiant)", value="user1")

    if profile_exists(user_id):
        st.success(f"Profil existant trouvé pour **{user_id}**")
        data = load_profile(user_id)
        if "profile" in data:
            p = data["profile"]
            st.write(f"🎯 Objectif : {p.get('objectif', '-')}")
            st.write(f"⚖️ Poids : {p.get('poids_kg', '-')} kg")
            st.write(f"📅 Niveau : {p.get('niveau', '-')}")
    else:
        st.info("Aucun profil trouvé. Décris-toi ci-dessous.")

# Zone principale
st.subheader("📝 Décris-toi")
st.write("Exemple : *Je m'appelle Iyad, j'ai 25 ans, je pèse 80kg pour 178cm. Mon objectif est de perdre du gras tout en gardant le muscle. Je suis intermédiaire, disponible 4 jours par semaine. Pas de restrictions alimentaires.*")

user_input = st.text_area("Ton profil en quelques phrases", height=120)

if st.button("🚀 Générer mon programme", type="primary"):
    if not user_input.strip():
        st.warning("Décris-toi d'abord !")
    else:
        with st.spinner("Analyse de ton profil en cours..."):
            result = run_pipeline(user_id, user_input)

        if "error" in result:
            st.error(f"Erreur : {result['error']}")
        else:
            # Profil
            st.subheader("👤 Profil extrait")
            st.json(result["profile"])

            col1, col2 = st.columns(2)

            # Plan nutrition
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

            # Plan entraînement
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

            # Validation
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