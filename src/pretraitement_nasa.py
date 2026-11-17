"""
Prétraitement des données de la NASA Exoplanet Archive.

Ce script est lancé une seule fois (python -m src.pretraitement_nasa).
Il lit le fichier de la NASA, garde quelques systèmes choisis et les
convertit au format CSV de l'application.
"""
import pandas as pd

# Fichier téléchargé de la NASA Exoplanet Archive (table PSCompPars)
FICHIER_NASA = "donnees/nasa_exoplanetes.csv"

# Nom de l'étoile dans le fichier de la NASA → nom affiché dans l'application
SYSTEMES_CHOISIS = {
    "TRAPPIST-1": "TRAPPIST-1",
    "KOI-351": "Kepler-90",  # Kepler-90 porte encore son ancien nom de catalogue dans le fichier
    "47 UMa": "47 UMa",

}

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



if __name__ == "__main__":
  df_naza = lire_fichier_nasa(FICHIER_NASA)
  print(f"Fichier de la NASA lu : {len(df_naza)} planètes trouvées.")

  df_selection = selectionner_systemes(df_naza, SYSTEMES_CHOISIS)
  print(f"Systèmes choisis : {len(df_selection)} planètes conservées.")
  print(df_selection[["systeme", "pl_name", "hostname"]])  # test: Affiche les colonnes utiles