import streamlit as st
from core.orchestrator import run_pipeline
from memory.user_memory import load_profile, profile_exists, save_to_history, load_history, save_checkin, load_checkins
from agents.checkin_agent import analyze_checkin

st.set_page_config(page_title="Fitness Coach AI", page_icon="💪", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #111111; color: #f0f0f0; }
    [data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 2px solid #FFD700; }
    h1 { color: #FFD700 !important; font-weight: 900 !important; }
    h2, h3 { color: #FFD700 !important; font-weight: 700 !important; }
    .stButton > button { background-color: #FFD700 !important; color: #111111 !important; font-weight: 800 !important; border-radius: 8px !important; }
    .stButton > button:hover { background-color: #FFC200 !important; transform: scale(1.03); }
    [data-testid="stMetric"] { background-color: #1f1f1f; border-left: 4px solid #FFD700; border-radius: 8px; padding: 1rem; }
    [data-testid="stMetricValue"] { color: #FFD700 !important; font-weight: 800 !important; }
    [data-testid="stExpander"] { background-color: #1a1a1a; border: 1px solid #333333; border-radius: 8px; }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea { background-color: #1f1f1f !important; color: #f0f0f0 !important; border: 1px solid #444444 !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

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
            st.write(f"🎯 {p.get('objectif', '-')}")
            st.write(f"⚖️ {p.get('poids_kg', '-')} kg")
            st.write(f"📅 {p.get('niveau', '-')}")
    else:
        st.info("Aucun profil trouvé.")

    st.divider()
    st.header("🕓 Historique")
    history = load_history(user_id)
    if not history:
        st.caption("Aucun plan généré pour l'instant.")
    else:
        for entry in reversed(history):
            with st.expander(f"📅 {entry['date']}"):
                p = entry.get("profile", {})
                st.write(f"🎯 {p.get('objectif', '-')} — {p.get('niveau', '-')}")
                n = entry.get("nutrition", {})
                st.write(f"🥗 {n.get('calories_journalieres', '-')} kcal/jour")
                t = entry.get("training", {})
                st.write(f"💪 {t.get('jours_entrainement', '-')} jours/semaine")
                v = entry.get("validation", {})
                st.write(f"✅ Score : {v.get('score', '-')}/100")

# Onglets
tab1, tab2 = st.tabs(["🏋️ Mon Programme", "📊 Check-in du jour"])

# ─── TAB 1 : PROGRAMME ───────────────────────────────────────────
with tab1:
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
        niveau = st.selectbox("📊 Niveau", ["Débutant", "Intermédiaire", "Avancé"])
        jours = st.select_slider("📅 Jours disponibles par semaine", options=[2, 3, 4, 5, 6], value=3)
        restrictions = st.multiselect("🥗 Restrictions alimentaires", [
            "Aucune", "Halal", "Végétarien", "Végétalien", "Sans gluten", "Sans lactose"
        ], default=["Aucune"])

    remarques = st.text_area("💬 Remarques (facultatif)", placeholder="Blessures, préférences...")

    if st.button("🚀 Générer mon programme", type="primary"):
        if not prenom:
            st.warning("Entre ton prénom pour continuer.")
        else:
            restrictions_str = ", ".join(restrictions) if restrictions else "Aucune"
            user_input = f"""
            Je m'appelle {prenom}, j'ai {age} ans, je pèse {poids}kg pour {taille}cm.
            Je suis un {sexe.lower()}. Mon objectif est : {objectif}.
            Mon niveau est : {niveau}. Je suis disponible {jours} jours par semaine.
            Restrictions alimentaires : {restrictions_str}.
            Remarques : {remarques if remarques else 'Aucune'}.
            """

            with st.spinner("Génération de ton programme..."):
                result = run_pipeline(user_id, user_input)

            if "error" in result:
                st.error(f"Erreur : {result['error']}")
            else:
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
                    for repas, items in n["repas"].items():
                        with st.expander(repas.replace("_", " ").capitalize()):
                            for item in items:
                                st.write(f"• {item}")
                    for conseil in n["conseils"]:
                        st.write(f"✅ {conseil}")

                with col2:
                    st.subheader("💪 Plan Entraînement")
                    t = result["training"]
                    st.metric("Jours/semaine", t["jours_entrainement"])
                    st.metric("Durée séance", f"{t['duree_seance_minutes']} min")
                    for jour, contenu in t["programme"].items():
                        with st.expander(f"{jour.replace('_', ' ').capitalize()} — {contenu['nom']}"):
                            for ex in contenu["exercices"]:
                                st.write(f"• **{ex['nom']}** — {ex['series']} séries × {ex['repetitions']} reps | repos {ex['repos_secondes']}s")
                    for conseil in t["conseils"]:
                        st.write(f"✅ {conseil}")

                st.subheader("✅ Validation")
                v = result["validation"]
                score = v["score"]
                couleur = "green" if score >= 80 else "orange" if score >= 60 else "red"
                st.markdown(f"**Score : :{couleur}[{score}/100]**")
                st.write(v["resume"])
                if v["problemes"]:
                    for p in v["problemes"]:
                        st.write(f"⚠️ {p}")
                if v["corrections"]:
                    for c in v["corrections"]:
                        st.write(f"🔧 {c}")

                st.rerun()

# ─── TAB 2 : CHECK-IN ────────────────────────────────────────────
with tab2:
    st.subheader("📊 Check-in du jour")

    if not profile_exists(user_id):
        st.warning("Génère d'abord un programme dans l'onglet Mon Programme.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            seance = st.selectbox("🏋️ T'as fait ta séance ?", ["Oui", "Partiellement", "Non"])
            energie = st.select_slider("⚡ Niveau d'énergie", options=[1, 2, 3, 4, 5], value=3)
            nutrition_ok = st.selectbox("🥗 T'as respecté le plan nutrition ?", ["Oui", "Partiellement", "Non"])

        with col2:
            poids_jour = st.number_input("⚖️ Poids du jour (kg)", min_value=30, max_value=200, value=75)
            commentaire = st.text_area("💬 Commentaire (facultatif)", placeholder="Comment tu te sens aujourd'hui ?")

        if st.button("✅ Envoyer mon check-in", type="primary"):
            checkin = {
                "seance": seance,
                "energie": energie,
                "nutrition_ok": nutrition_ok,
                "poids_jour": poids_jour,
                "commentaire": commentaire
            }

            save_checkin(user_id, checkin)

            data = load_profile(user_id)
            profile = data.get("profile", {})
            historique = load_checkins(user_id)

            with st.spinner("Analyse de ton check-in..."):
                result = analyze_checkin(profile, checkin, historique)

            if not result["success"]:
                st.error("Erreur lors de l'analyse.")
            else:
                a = result["analysis"]

                st.subheader("📋 Analyse du coach")
                st.write(a["analyse"])

                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Ajustements nutrition :**")
                    for adj in a["ajustements_nutrition"]:
                        st.write(f"🥗 {adj}")
                with col2:
                    st.write("**Ajustements entraînement :**")
                    for adj in a["ajustements_entrainement"]:
                        st.write(f"💪 {adj}")

                st.info(f"💬 {a['message_motivation']}")

                if a["alerte"]:
                    st.warning("⚠️ Ton coach détecte un signal préoccupant — fais attention à toi.")

                # Historique des check-ins
                st.divider()
                st.subheader("📈 Tes 7 derniers check-ins")
                checkins = load_checkins(user_id)
                if checkins:
                    for c in reversed(checkins[-7:]):
                        with st.expander(f"📅 {c.get('date', '-')}"):
                            st.write(f"🏋️ Séance : {c.get('seance', '-')}")
                            st.write(f"⚡ Énergie : {c.get('energie', '-')}/5")
                            st.write(f"🥗 Nutrition : {c.get('nutrition_ok', '-')}")
                            st.write(f"⚖️ Poids : {c.get('poids_jour', '-')} kg")
                            if c.get('commentaire'):
                                st.write(f"💬 {c.get('commentaire')}")