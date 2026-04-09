# Fitness Coach Agent

Un agent IA qui joue le rôle d'un coach fitness et nutrition personnel.
Tu décris ton profil en quelques phrases, il génère un plan alimentaire et un programme d'entraînement adaptés, puis valide que les deux sont cohérents.

## Pourquoi ce projet

Mes projets précédents sur GitHub étaient tous des expériences en notebooks — comprendre RAG, tester la fiabilité des LLMs, observer le comportement des modèles.

Ce projet, c'est l'étape d'après : construire un vrai agent qui applique ce que j'ai appris, et voir les vrais blocages qu'on rencontre quand on sort des notebooks.

## Ce que j'ai trouvé intéressant

Le fait de travailler sur chaque sous-agent indépendamment (profiling, nutrition, entraînement, validation) et de voir tout s'orchestrer en synchronisation dans le pipeline final. C'est là qu'on comprend vraiment ce que "système multi-agent" veut dire.

## Architecture

User Input → Profiling Agent → Nutrition Agent + Training Agent → Validation Agent → Memory Layer

- Profiling Agent : extrait âge, poids, objectif, niveau, restrictions
- Nutrition Agent : génère le plan alimentaire
- Training Agent : génère le programme d'entraînement
- Validation Agent : vérifie la cohérence entre les deux plans, retry si JSON invalide
- Memory Layer : profil persisté entre les sessions

## Stack

- Python
- Groq API (LLaMA 3.3 70B)
- LLM wrapper swappable vers OpenAI en une ligne
- Streamlit
- JSON validation + retry loop

## Lancer en local

git clone https://github.com/iyadlhassani-stack/fitness-coach-agent
cd fitness-coach-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

Crée un fichier .env avec GROQ_API_KEY=ta_clé_ici puis lance : streamlit run app.py

## Demo live

https://fitness-coach-agent-nefltzs6ugczebssuayuuh.streamlit.app
