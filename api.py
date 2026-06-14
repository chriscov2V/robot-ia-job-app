import json
import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("❌ Erreur : OPENAI_API_KEY manquante dans le .env")

client = OpenAI(api_key=api_key)

# 1. Initialisation de l'application
app = FastAPI(title="Moteur de Candidature IA - Production")

# 2. SÉCURITÉ CORS (Étape 0 indispensable pour Bubble)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Structure des données reçues de Bubble (V2 avec URL)
class RequeteCandidat(BaseModel):
    profil: str
    entreprise: str
    poste: str
    url: str  # Remplacement de description par url

# 🛠️ FONCTION ROBOT : Va lire le contenu du lien web automatiquement
def extraire_texte_url(url: str) -> str:
    try:
        # On simule un vrai navigateur web pour éviter d'être bloqué par les sites
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Nettoyage du HTML pour ne garder que le texte propre de l'annonce
        soup = BeautifulSoup(response.text, "html.parser")
        
        # On supprime le bruit (scripts, styles, menus de navigation)
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        texte_brut = soup.get_text(separator=" ")
        # On nettoie les espaces vides en trop
        texte_propre = re.sub(r'\s+', ' ', texte_brut).strip()
        
        # Sécurité : Si le site bloque totalement le robot et renvoie du vide
        if len(texte_propre) < 100:
            return "[Erreur] Impossible d'extraire un contenu suffisant de cette URL (Protection anti-robot ou page dynamique)."
            
        return texte_propre[:8000] # On limite à 8000 caractères pour ne pas exploser les tokens
        
    except Exception as e:
        print(f"⚠️ Erreur lors du scraping de l'URL : {e}")
        return f"[Erreur] Le serveur n'a pas réussi à lire le lien automatiquement : {str(e)}"

# 4. Point d'entrée de l'analyse (POST)
@app.post("/analyser")
def analyser_offre(donnees: RequeteCandidat):
    print(f"📡 [PROD] Nouvelle requête reçue pour l'entreprise : {donnees.entreprise}")
    print(f"🌐 [PROD] Tentative de lecture de l'URL : {donnees.url}")
    
    # Appel de notre robot de lecture
    description_annonce = extraire_texte_url(donnees.url)
    
    prompt = f"""
    Tu es un expert en recrutement. Évalue la cohérence entre ce profil et cette offre d'emploi.
    
    PROFIL:
    {donnees.profil}

    OFFRE:
    Entreprise: {donnees.entreprise}
    Poste: {donnees.poste}
    Contenu extrait de l'annonce : {description_annonce}

    Réponds au format JSON strict avec exactement ces clés :
    - "score": nombre entier entre 0 et 100.
    - "verdict": "Postuler" ou "Passer".
    - "lettre": une lettre de motivation personnalisée et percutante.
    - "suggestions": une liste (tableau) de 3 métiers ou types d'emplois alternatifs recommandés qui correspondent PARFAITEMENT aux vraies compétences du profil du candidat (surtout utile si le score est bas).
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
            "lettre": resultat_json.get("lettre", ""),
            "suggestions": resultat_json.get("suggestions", [])
        }
        
    except Exception as e:
        print(f"❌ [PROD] Erreur critique lors du traitement IA : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Le moteur de production est en ligne et configuré pour Bubble !"}