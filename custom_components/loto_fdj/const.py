from homeassistant.const import Platform

DOMAIN = "loto_fdj"
PLATFORMS: list[Platform] = [Platform.SENSOR]
DEFAULT_NAME = "Loto FDJ"
UPDATE_INTERVAL = 3600  # 1 heure
FDJO_URL = "https://www.fdj.fr/jeux-de-tirage/loto/resultats/mercredi-25-juin-2025"

