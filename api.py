import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("❌ Erreur : OPENAI_API_KEY manquante dans le .env")

client = OpenAI(api_key=api_key)

# 1. Initialisation de l'application
app = FastAPI(title="Moteur de Candidature IA - Production")

# 2. SÉCURITÉ CORS (Étape 0 indispensable pour Bubble)
# On autorise toutes les origines (*) pour le développement, ce qui permettra à Bubble de se connecter sans blocage.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Structure des données reçues de Bubble
class RequeteCandidat(BaseModel):
    profil: str
    entreprise: str
    poste: str
    description: str

# 4. Point d'entrée de l'analyse (POST)
@app.post("/analyser")
def analyser_offre(donnees: RequeteCandidat):
    print(f"📡 [PROD] Nouvelle requête reçue pour l'entreprise : {donnees.entreprise}")
    
    prompt = f"""
    Tu es un expert en recrutement. Évalue la cohérence entre ce profil et cette offre d'emploi.
    
    PROFIL:
    {donnees.profil}

    OFFRE:
    Entreprise: {donnees.entreprise}
    Poste: {donnees.poste}
    Description: {donnees.description}

    Réponds au format JSON strict avec exactement ces clés :
    - "score": nombre entier entre 0 et 100.
    - "verdict": "Postuler" ou "Passer".
    - "lettre": une lettre de motivation personnalisée et percutante.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Tu es un algorithme de recrutement en JSON strict."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        resultat_json = json.loads(response.choices[0].message.content)
        print(f"✅ [PROD] Analyse terminée avec succès pour {donnees.entreprise} (Score: {resultat_json.get('score')})")
        
        return {
            "statut": "succes",
            "score": int(resultat_json.get("score", 0)),
            "verdict": resultat_json.get("verdict", "Passer"),
            "lettre": resultat_json.get("lettre", "")
        }
        
    except Exception as e:
        print(f"❌ [PROD] Erreur critique lors du traitement IA : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Le moteur de production est en ligne et configuré pour Bubble !"}
