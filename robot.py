import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
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

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{filepath}' est introuvable.")
        sys.exit(1)

def main():
    print("🤖 ROBOT D'ANALYSE MULTI-PROFILS (CORRIGÉ)")
    print("="*40)
    print("1. Christdorian (Conseiller de Vente)")
    print("2. Sarah (Développeuse Python)")
    print("="*40)
    
    choix = input("👉 Choisissez le profil à traiter (1 ou 2) : ")
    
    if choix == "1":
        fichier_profil = "profile_christdorian.json"
        nom_utilisateur = "Christdorian"
    elif choix == "2":
        fichier_profil = "profile_sarah.json"
        nom_utilisateur = "Sarah"
    else:
        print("❌ Choix invalide. Arrêt.")
        sys.exit(0)

    print(f"\n🚀 Lancement du robot pour l'utilisateur : {nom_utilisateur}")
    
    profile = load_file(fichier_profil)
    jobs = load_json('jobs_list.json')
    
    tableau_des_scores = []

    for job in jobs:
        entreprise = job.get('entreprise', 'Inconnue')
        poste = job.get('poste', 'Non spécifié')
        description = job.get('description', '')
        
        print(f"⏳ [En cours] Analyse IA pour {entreprise}...")

        prompt = f"""
        Tu es un expert en recrutement. Évalue la cohérence entre ce profil de candidat et cette offre d'emploi.
        
        PROFIL CANDIDAT:
        {profile}

        OFFRE D'EMPLOI:
        Entreprise: {entreprise}
        Poste: {poste}
        Description: {description}

        CRITICAL: Réponds au format JSON strict avec ces clés :
        - "score": nombre entier entre 0 et 100.
        - "verdict": "Postuler" ou "Passer".
        - "lettre": une lettre de motivation personnalisée signée par le candidat.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Tu es un assistant de recrutement automatisé en JSON strict."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            resultat_json = json.loads(response.choices[0].message.content)
            
            score_extrait = int(resultat_json.get("score", 0))
            verdict_extrait = resultat_json.get("verdict")
            lettre_extraite = resultat_json.get("lettre")
            
            print(f"✅ Analyse finie pour {entreprise}.")
            
            # La variable est corrigée ici : entreprise (avec un i) !
            nom_fichier = f"lettre_{nom_utilisateur.lower()}_{entreprise.lower().replace(' ', '_')}.txt"
            with open(nom_fichier, "w", encoding="utf-8") as f:
                f.write(lettre_extraite)
            
            tableau_des_scores.append({
                "entreprise": entreprise,
                "poste": poste,
                "score": score_extrait,
                "verdict": verdict_extrait,
                "fichier": nom_fichier
            })
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement : {e}")

    print("\n" + "="*50)
    print(f"🏆 CLASSEMENT DES OFFRES POUR {nom_utilisateur.upper()} 🏆")
    print("="*50)

    tableau_des_scores.sort(key=lambda x: x['score'], reverse=True)

    for i, res in enumerate(tableau_des_scores, start=1):
        icone = "🔥" if res['score'] >= 70 else "⚠️"
        print(f"{i}. {icone} {res['entreprise']} - {res['poste']}")
        print(f"   🎯 Compatibilité : {res['score']}/100 | 🚦 Verdict : {res['verdict']}")
        print(f"   📄 Lettre : {res['fichier']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
