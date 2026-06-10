import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key.startswith("sk-proj-PROPRE_CLE"):
    print("❌ Erreur : OPENAI_API_KEY manquante dans le .env")
    sys.exit(1)

client = OpenAI(api_key=api_key)

def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{filepath}' est introuvable.")
        sys.exit(1)

def main():
    print("🧠 [OpenAI] Analyse de l'offre et rédaction de la lettre...")
    
    profile = load_file('profile.json')
    job = load_file('job_to_analyze.txt')

    prompt = f"""
    Tu es un expert en recrutement. Évalue la cohérence entre ce profil de candidat et cette offre d'emploi.
    
    PROFIL CANDIDAT:
    {profile}

    OFFRE D'EMPLOI:
    {job}

    Fournis ta réponse en deux parties distinctes :
    1. L'ANALYSE : Score/100, Verdict, Points forts, Points faibles.
    2. LA LETTRE DE MOTIVATION : Rédige une lettre de motivation (ou mail de candidature) personnalisée, moderne, directe et percutante. Mets en avant l'expérience en vente et le passage chez Boulanger pour balayer l'écart de diplôme. Pas de blabla inutile, va droit au but pour donner envie de lire le CV.
    
    CRITICAL: Signe IMPÉRATIVEMENT la lettre à la fin avec ces coordonnées exactes (ne mets pas de crochets, écris-les telles quelles) :
    Christdorian Ouakoube  
    07 69 93 53 99  
    Christdorian.o@icloud.com
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un coach en recrutement expert qui aide un candidat à décrocher un entretien en étant ultra-percutant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        full_text = response.choices[0].message.content
        
        print("\n=== RÉSULTAT DE L'IA ===")
        print(full_text)
        print("==========================")
        
        with open("lettre_motivation.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
        print("\n💾 La réponse et la lettre ont été sauvegardées dans 'lettre_motivation.txt' avec tes coordonnées !")
        
    except Exception as e:
        print(f"❌ Erreur avec l'API OpenAI : {e}")

if __name__ == "__main__":
    main()
