"""Configuration flow pour Loto FDJ."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import aiohttp
from bs4 import BeautifulSoup

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_NAME, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("name", default=DEFAULT_NAME): str,
        vol.Optional("update_interval", default=UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=300, max=86400)  # 5 min à 24h
        ),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional("update_interval", default=UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=300, max=86400)
        ),
        vol.Optional("show_date", default=True): bool,
        vol.Optional("show_complete_result", default=True): bool,
    }
)

async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Valide que nous pouvons nous connecter à FDJ."""
    try:
        # Utiliser l'URL qui fonctionne d'après nos tests
        url = "https://www.fdj.fr/jeux-de-tirage/loto/resultats/mercredi-25-juin-2025"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            ) as response:
                if response.status != 200:
                    _LOGGER.error("HTTP Error: %s", response.status)
                    raise CannotConnect
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Vérifier qu'on peut extraire les numéros (méthode qui fonctionne)
                spans = soup.find_all('span')
                numbers_found = []
                
                for span in spans:
                    text = span.get_text().strip()
                    if text.isdigit() and 1 <= int(text) <= 49:
                        numbers_found.append(text)
                
                _LOGGER.debug(f"Validation: {len(numbers_found)} numéros trouvés")
                
                # Vérifier qu'on a au moins 6 numéros (5 boules + 1 chance)
                if len(numbers_found) < 6:
                    _LOGGER.error("Pas assez de numéros trouvés lors de la validation")
                    raise InvalidData
                    
    except aiohttp.ClientError as err:
        _LOGGER.error("Erreur de connexion à FDJ: %s", err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.error("Erreur inattendue lors de la validation: %s", err)
        raise InvalidData from err

    return {"title": data.get("name", DEFAULT_NAME)}

class LotoFDJConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestionnaire du flux de configuration pour Loto FDJ."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gérer l'étape initiale."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", 
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "name": DEFAULT_NAME,
                    "update_interval": str(UPDATE_INTERVAL // 60)
                }
            )

        errors = {}

        try:
            info = await validate_connection(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidData:
            errors["base"] = "invalid_data"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Erreur inattendue")
            errors["base"] = "unknown"
        else:
            # Vérifier si l'intégration existe déjà
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "name": DEFAULT_NAME,
                "update_interval": str(UPDATE_INTERVAL // 60)
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LotoFDJOptionsFlowHandler:
        """Créer le flux d'options."""
        return LotoFDJOptionsFlowHandler(config_entry)

class LotoFDJOptionsFlowHandler(config_entries.OptionsFlow):
    """Gestionnaire du flux d'options pour Loto FDJ."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialiser le flux d'options."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gérer les options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Récupérer les options actuelles ou les valeurs par défaut
        current_options = self.config_entry.options
        
        options_schema = vol.Schema(
            {
                vol.Optional(
                    "update_interval",
                    default=current_options.get("update_interval", UPDATE_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=300, max=86400)),
                vol.Optional(
                    "show_date",
                    default=current_options.get("show_date", True)
                ): bool,
                vol.Optional(
                    "show_complete_result",
                    default=current_options.get("show_complete_result", True)
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "current_interval": str(current_options.get("update_interval", UPDATE_INTERVAL) // 60)
            }
        )

class CannotConnect(HomeAssistantError):
    """Erreur de connexion."""

class InvalidData(HomeAssistantError):
    """Données invalides."""


