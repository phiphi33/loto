from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import aiohttp
from bs4 import BeautifulSoup
from datetime import timedelta

class LotoFDJSensor(SensorEntity):
    """Capteur pour les résultats du Loto FDJ."""
    
    def __init__(self, coordinator, sensor_type):
        self.coordinator = coordinator
        self._sensor_type = sensor_type
        self._attr_name = f"Loto {sensor_type}"
        self._attr_unique_id = f"loto_fdj_{sensor_type.lower()}"
    
    @property
    def state(self):
        """Retourne l'état du capteur."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._sensor_type)
        return None

class LotoDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinateur pour récupérer les données du loto."""
    
    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            logger,
            name="Loto FDJ",
            update_interval=timedelta(hours=1),
        )
    
    async def _async_update_data(self):
        """Récupère les derniers résultats du loto."""
        async with aiohttp.ClientSession() as session:
            async with session.get(FDJO_URL) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraction basée sur les sélecteurs du forum[1]
                boules = []
                for i in range(1, 6):
                    selector = f"#loto-results ul.result-full__list li.result-full__list-item:nth-child({i}) > span.game-ball"
                    element = soup.select_one(selector)
                    if element:
                        boules.append(element.text.strip())
                
                # Boule chance
                chance_selector = "#loto-results ul.result-full__list li.result-full__list-item:nth-child(6) > span.game-ball"
                chance_element = soup.select_one(chance_selector)
                chance = chance_element.text.strip() if chance_element else None
                
                # Date du tirage
                date_selector = "#loto-results div.fdj.Heading > h1.fdj.Title"
                date_element = soup.select_one(date_selector)
                date_tirage = date_element.text.strip() if date_element else None
                
                return {
                    "boule_1": boules[0] if len(boules) > 0 else None,
                    "boule_2": boules[1] if len(boules) > 1 else None,
                    "boule_3": boules[2] if len(boules) > 2 else None,
                    "boule_4": boules[3] if len(boules) > 3 else None,
                    "boule_5": boules[4] if len(boules) > 4 else None,
                    "boule_chance": chance,
                    "date_tirage": date_tirage,
                    "resultat_complet": " - ".join(boules) + f" * {chance}" if boules and chance else None
                }
