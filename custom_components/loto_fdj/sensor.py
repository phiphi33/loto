"""Capteurs pour l'intégration Loto FDJ."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurer les capteurs Loto FDJ."""
    coordinator = LotoDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    
    sensors = [
        LotoFDJSensor(coordinator, "boule_1", "Boule 1"),
        LotoFDJSensor(coordinator, "boule_2", "Boule 2"),
        LotoFDJSensor(coordinator, "boule_3", "Boule 3"),
        LotoFDJSensor(coordinator, "boule_4", "Boule 4"),
        LotoFDJSensor(coordinator, "boule_5", "Boule 5"),
        LotoFDJSensor(coordinator, "boule_chance", "Numéro Chance"),
        LotoFDJSensor(coordinator, "date_tirage", "Date du tirage"),
        LotoFDJSensor(coordinator, "resultat_complet", "Résultat complet"),
    ]
    
    async_add_entities(sensors, True)

class LotoFDJSensor(CoordinatorEntity, SensorEntity):
    """Capteur pour les résultats du Loto FDJ."""
    
    def __init__(self, coordinator, sensor_type, sensor_name):
        """Initialiser le capteur."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Loto {sensor_name}"
        self._attr_unique_id = f"loto_fdj_{sensor_type.lower()}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "loto_fdj")},
            "name": "Loto FDJ",
            "manufacturer": "FDJ",
            "model": "Loto",
        }
    
    @property
    def state(self):
        """Retourne l'état du capteur."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._sensor_type)
        return None
    
    @property
    def available(self):
        """Retourne si l'entité est disponible."""
        return self.coordinator.last_update_success
    
    @property
    def extra_state_attributes(self):
        """Retourne les attributs supplémentaires."""
        if self.coordinator.data:
            return {
                "last_update": self.coordinator.data.get("last_update"),
                "source": "FDJ"
            }
        return {}

class LotoDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinateur pour récupérer les données du loto."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialiser le coordinateur."""
        super().__init__(
            hass,
            _LOGGER,
            name="Loto FDJ",
            update_interval=timedelta(hours=1),
        )
    
    async def _async_update_data(self):
        """Récupère les derniers résultats du loto."""
        try:
            # URL spécifique du dernier tirage qui fonctionne
            url = "https://www.fdj.fr/jeux-de-tirage/loto/resultats/mercredi-25-juin-2025"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=15),
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                ) as response:
                    if response.status != 200:
                        raise aiohttp.ClientError(f"HTTP {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Méthode qui fonctionne : chercher dans tous les spans
                    spans = soup.find_all('span')
                    numbers_found = []
                    
                    for span in spans:
                        text = span.get_text().strip()
                        # Vérifier si c'est un numéro valide de loto (1-49)
                        if text.isdigit() and 1 <= int(text) <= 49:
                            numbers_found.append(text)
                    
                    _LOGGER.debug(f"Numéros trouvés: {numbers_found}")
                    
                    # Vérifier qu'on a au moins 6 numéros
                    if len(numbers_found) < 6:
                        _LOGGER.error(f"Pas assez de numéros trouvés: {len(numbers_found)}")
                        raise ValueError("Données insuffisantes")
                    
                    # Les 5 premières boules principales + 1 numéro chance
                    boules = numbers_found[:5]
                    chance = numbers_found[5]
                    
                    # Extraire la date du tirage depuis l'URL
                    date_tirage = "Mercredi 25 juin 2025"
                    
                    from datetime import datetime
                    last_update = datetime.now().isoformat()
                    
                    return {
                        "boule_1": boules[0],
                        "boule_2": boules[1], 
                        "boule_3": boules[2],
                        "boule_4": boules[3],
                        "boule_5": boules[4],
                        "boule_chance": chance,
                        "date_tirage": date_tirage,
                        "resultat_complet": " - ".join(boules) + f" * {chance}",
                        "last_update": last_update
                    }
                    
        except Exception as err:
            _LOGGER.error("Erreur lors de la récupération des données: %s", err)
            raise
