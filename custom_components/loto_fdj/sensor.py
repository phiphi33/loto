async def _async_update_data(self):
    """Récupère les derniers résultats du loto."""
    try:
        # Utiliser l'URL spécifique du dernier tirage
        url = "https://www.fdj.fr/jeux-de-tirage/loto/resultats/mercredi-25-juin-2025"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # NOUVELLE MÉTHODE : Chercher dans tous les spans
                spans = soup.find_all('span')
                numbers_found = []
                
                for span in spans:
                    text = span.get_text().strip()
                    # Vérifier si c'est un numéro valide de loto
                    if text.isdigit() and 1 <= int(text) <= 49:
                        numbers_found.append(text)
                
                _LOGGER.debug(f"Numéros trouvés: {numbers_found}")
                
                # Prendre les 6 premiers numéros (5 boules + 1 chance)
                if len(numbers_found) >= 6:
                    boules = numbers_found[:5]  # Les 5 premières boules
                    chance = numbers_found[5]   # La 6ème est le numéro chance
                else:
                    _LOGGER.error(f"Pas assez de numéros trouvés: {len(numbers_found)}")
                    raise ValueError("Données insuffisantes")
                
                return {
                    "boule_1": boules[0],
                    "boule_2": boules[1],
                    "boule_3": boules[2],
                    "boule_4": boules[3],
                    "boule_5": boules[4],
                    "boule_chance": chance,
                    "date_tirage": "Mercredi 25 juin 2025",
                    "resultat_complet": " - ".join(boules) + f" * {chance}"
                }
                
    except Exception as err:
        _LOGGER.error("Erreur lors de la récupération des données: %s", err)
        raise
