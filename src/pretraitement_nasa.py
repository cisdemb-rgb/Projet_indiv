"""
Prétraitement des données de la NASA Exoplanet Archive.

Ce script est lancé une seule fois (python -m src.pretraitement_nasa).
Il lit le fichier de la NASA, garde quelques systèmes choisis et les
convertit au format CSV de l'application.
"""
import pandas as pd
import numpy as np
from src.chargeur_csv import COLONNES_tous, valider_csv


# Fichier téléchargé de la NASA Exoplanet Archive (table PSCompPars)
FICHIER_NASA = "donnees/nasa_exoplanetes.csv"
FICHIER_SORTIE = "donnees/systemes_nasa.csv"

# Nom de l'étoile dans le fichier de la NASA → nom affiché dans l'application
SYSTEMES_CHOISIS = {
    "TRAPPIST-1": "TRAPPIST-1",
    "KOI-351": "Kepler-90",  # Kepler-90 porte encore son ancien nom de catalogue dans le fichier
    "47 UMa": "47 UMa",

}
MASSE_SOLEIL_EN_TERRES = 332946.0487  # 1 masse solaire = 332 946 masses terrestres
RAYON_SOLEIL_EN_TERRES = 109          # 1 rayon solaire = 109 rayons terrestres (colonne taille)
RAYON_SOLEIL_EN_UA = 0.00464913       # 1 rayon solaire en unités astronomiques (colonne rayon)
RAYON_TERRE_EN_UA = 0.00004263521         # 1 rayon terrestre en unités astronomiques (colonne rayon)


def lire_fichier_nasa(chemin):
    """
    Lit le fichier CSV de la NASA en ignorant les lignes de commentaires.

    Args:
        chemin (str): Chemin vers le fichier de la NASA.

    Returns:
        pd.DataFrame: Une ligne par planète.

    Raises:
        ValueError: Si le fichier est introuvable ou vide.
    """
    try:
        # Les 18 premières lignes commencent par # : ce sont des explications, pas des données
        df = pd.read_csv(chemin, comment="#")
    except FileNotFoundError:
        raise ValueError(f"Le fichier de la NASA « {chemin} » est introuvable.")
    except pd.errors.EmptyDataError:
        raise ValueError(f"Le fichier de la NASA « {chemin} » est vide.")
    return df


def selectionner_systemes(df, systemes):
    """
    Garde seulement les planètes des systèmes choisis et ajoute la colonne « systeme ».

    Args:
        df (pd.DataFrame): Toutes les planètes du fichier de la NASA.
        systemes (dict[str, str]): Nom de l'étoile dans le fichier → nom affiché.

    Returns:
        pd.DataFrame: Les planètes des systèmes choisis.

    Raises:
        ValueError: Si un système choisi n'existe pas dans le fichier.
    """
    selection = df[df["hostname"].isin(systemes.keys())].copy()  # copy : pour ne pas modifier df

    manquants = [nom for nom in systemes if nom not in selection["hostname"].values]
    if manquants:
        raise ValueError(f"Systèmes introuvables dans le fichier de la NASA : {manquants}")

    selection["systeme"] = selection["hostname"].map(systemes)  # Remplace chaque hostname par son nom affiché
    return selection

def creer_etoiles(selection):
    """
    Crée une ligne au format de l'application pour l'étoile de chaque système

    Args:
        selection (pd.DataFrame): Les planètes des systèmes choisis.

    Returns:
        pd.DataFrame: Le même DataFrame avec une ligne qui correspond à l'étoile .
    """
    etoiles = selection.groupby("systeme", as_index=False).agg(
        hostname =("hostname", "first"), # On prend le premier hostname pour chaque système
        st_rad =("st_rad", "mean"),  # On prend la moyenne du rayon des étoiles (st_rad) pour chaque système
        st_mass =("st_mass", "mean"), # On prend la moyenne de la masse des étoiles (st_mass) pour chaque système
        
    )  


    return pd.DataFrame({
        "systeme": etoiles["systeme"],
        "type": "AstreFixe",
        "nom": etoiles["hostname"],
        "masse": etoiles["st_mass"]*MASSE_SOLEIL_EN_TERRES,  # conversion en masses terrestres
        "couleur": "Yellow",  # couleur par défaut pour les étoiles
        "taille": etoiles["st_rad"] * RAYON_SOLEIL_EN_TERRES,  # conversion en rayons terrestres
        "rayon": etoiles["st_rad"] * RAYON_SOLEIL_EN_UA,  # conversion en unités astronomiques
        "actif": "true",  # toutes les étoiles sont actives
        "distance": 0.0,  
        "periode": 0.0,  
        "phase": 0.0,
    })

def creer_planetes(selection):
    """
    Crée une ligne au format de l'application pour chaque planète du système choisi.

    Args:
        selection (pd.DataFrame): Les planètes des systèmes choisis.

    Returns:
        pd.DataFrame: Le même DataFrame avec une ligne par planète.
    """
    return pd.DataFrame({
        "systeme": selection["systeme"],
        "type": "AstreFixe",
        "nom": selection["pl_name"],
        "masse": selection["pl_bmasse"],  # déjà en masses terrestres
        "couleur": "",  # couleur aléatoire
        "taille": selection["pl_rade"],  # déjà en rayons terrestres
        "rayon": selection["pl_rade"] * RAYON_TERRE_EN_UA,  # conversion en unités astronomiques
        "actif": "true",  # toutes les planètes sont actives
        "distance": selection["pl_orbsmax"],  # distance de l'étoile en parsecs
        "periode": selection["pl_orbper"],  # période orbitale en jours
        "phase": 0.0,  
    })

def assembler_systemes(etoiles, planetes):
    """
    Assemble les étoiles et les planètes dans un seul DataFrame.

    Args:
        etoiles (pd.DataFrame): Les étoiles des systèmes choisis.
        planetes (pd.DataFrame): Les planètes des systèmes choisis.

    Returns:
        pd.DataFrame: Un DataFrame avec une ligne par astre (étoile ou planète).
    """
    systemes = pd.concat([etoiles, planetes], ignore_index=True)
    systemes = systemes.sort_values(by="systeme", kind="stable", ignore_index=True) # tri par système pour que les étoiles apparaissent avant les planètes
   
    return systemes.reindex(columns=["systeme"] + COLONNES_tous)  # réorganise les colonnes pour correspondre à l'ordre attendu par l'application


if __name__ == "__main__":
  df_naza = lire_fichier_nasa(FICHIER_NASA)
  print(f"Fichier de la NASA lu : {len(df_naza)} planètes trouvées.")

  df_selection = selectionner_systemes(df_naza, SYSTEMES_CHOISIS)
  #print(f"Systèmes choisis : {len(df_selection)} planètes conservées.")
  #print(df_selection[["systeme", "pl_name", "hostname"]])  # test: Affiche les colonnes utiles
  etoiles = creer_etoiles(df_selection) 
 
  planètes = creer_planetes(df_selection)
  systemes = assembler_systemes(etoiles, planètes)

  #print(etoiles)  # test: Affiche les étoiles créées
  #print(planètes)  # test: Affiche les planètes créées
  print(systemes)  # test: Affiche les systèmes créés