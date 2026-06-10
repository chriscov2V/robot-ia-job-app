import json
import os
import sys
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Erreur : OPENAI_API_KEY manquante.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# 1. Base de données de l'offre cible (La Fnac)
offre_fnac = {
    "entreprise": "Fnac",
    "poste": "Conseiller de vente Micro-Informatique",
    "description": "Nous recherchons un vendeur passionné par la tech pour conseiller nos clients sur l'espace ordinateurs et tablettes. Accueil, démonstration et vente de services (garanties, cartes de fidélité). Profil dynamique, sens du contact. Expérience en vente exigée."
}

# 2. Génération automatique de 10 profils très différents pour le test
profils_test = [
    {"id": 1, "nom": "Thomas (Vendeur Tech)", "metier": "Vendeur expert informatique chez Boulanger depuis 2 ans"},
    {"id": 2, "nom": "Amélie (Boulangère)", "metier": "Artisan boulangère-pâtissière, experte en cuisson du pain"},
    {"id": 3, "nom": "Lucas (Étudiant)", "metier": "Étudiant en école de commerce, passionné de jeux vidéo et de PC custom"},
    {"id": 4, "nom": "Sarah (Développeuse)", "metier": "Développeuse Python senior, experte en bases de données et IA"},
    {"id": 5, "nom": "Youssef (Chauffeur)", "metier": "Chauffeur de VTC indépendant, excellent sens du contact client"},
    {"id": 6, "nom": "Chloé (Commerciale)", "metier": "Commerciale terrain en assurance, habituée à vendre des contrats et services"},
    {"id": 7, "nom": "Kevin (Animateur)", "metier": "Animateur en centre de loisirs, très dynamique, adore le contact humain"},
    {"id": 8, "nom": "Léa (Designer)", "metier": "Graphiste / Designer UX-UI Freelance, maîtrise de Photoshop et Figma"},
    {"id": 9, "nom": "Maxime (Hôte d'accueil)", "metier": "Hôte d'accueil en grande surface, gestion du flux client et réclamations"},
    {"id": 10, "nom": "Emma (Manager Retail)", "metier": "Responsable de rayon prêt-à-porter, gestion d'équipe et d'indicateurs de vente"}
]

def main():
    print("⚡ DÉMARRAGE DU STRESS TEST : 10 PROFILS EN SÉRIE ⚡")
    print(f"Cible : {offre_fnac['poste']} chez {offre_fnac['entreprise']}\n")
    
    classement_general = []
    temps_debut_global = time.time()

    for p in profils_test:
        print(f"⏳ [Profil {p['id']}/10] Analyse en cours pour {p['nom']}...")
        temps_debut_ia = time.time()

        prompt = f"""
        Évalue la cohérence entre ce profil et cette offre d'emploi.
        PROFIL: {p['metier']}
        OFFRE: {offre_fnac['description']}

        Réponds au format JSON strict avec :
        - "score": nombre entier entre 0 et 100.
        - "verdict": "Postuler" ou "Passer".
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Tu es un algorithme de tri de CV en JSON strict."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            res = json.loads(response.choices[0].message.content)
            temps_ia = round(time.time() - temps_debut_ia, 2)
            
            print(f"   📊 Score calculé : {res.get('score')}/100 (en {temps_ia}s)")
            
            classement_general.append({
                "nom": p['nom'],
                "score": int(res.get('score', 0)),
                "verdict": res.get('verdict', 'Passer')
            })
            
        except Exception as e:
            print(f"   ❌ Erreur profil {p['nom']} : {e}")

    # 🔄 Tri des profils du meilleur au moins bon
    classement_general.sort(key=lambda x: x['score'], reverse=True)

    temps_total = round(time.time() - temps_debut_global, 2)

    print("\n" + "="*60)
    print(f"🏆 TABLEAU DE BORD FINAL (Généré en {temps_total} secondes) 🏆")
    print("="*60)
    
    for i, candidat in enumerate(classement_general, start=1):
        medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        print(f"{medaille} N°{i}: {candidat['nom']}")
        print(f"     🎯 Score : {candidat['score']}/100 | 🚦 Verdict : {candidat['verdict']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
