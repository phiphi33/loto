# Loto FDJ - Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/phiphi33/loto)](https://github.com/phiphi33/loto/releases)

Intégration Home Assistant pour afficher les résultats du Loto français (FDJ) directement dans votre tableau de bord.

## Fonctionnalités

- **Résultats en temps réel** : Récupération automatique des derniers tirages
- **Capteurs multiples** : Boules principales (1-5) et boule chance séparées
- **Mise à jour automatique** : Actualisation après chaque tirage (Lundi, Mercredi, Samedi)
- **Interface intuitive** : Configuration via l'interface utilisateur Home Assistant
- **Compatible HACS** : Installation simplifiée

## Installation

### Via HACS (Recommandé)

1. Ouvrez HACS dans Home Assistant
2. Allez dans **Intégrations**
3. Cliquez sur **Explorer et télécharger des dépôts**
4. Recherchez "**Loto FDJ**"
5. Cliquez sur **Télécharger**
6. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez les fichiers depuis [Releases](https://github.com/phiphi33/loto/releases)
2. Copiez le dossier `loto_fdj` dans `custom_components/`
3. Redémarrez Home Assistant

## Configuration

1. Dans Home Assistant, allez dans **Configuration** > **Intégrations**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez "**Loto FDJ**"
4. Suivez les instructions de configuration

## Capteurs disponibles

L'intégration crée automatiquement les capteurs suivants :

| Capteur | Description | Valeur exemple |
|---------|-------------|----------------|
| `sensor.loto_boule_1` | Première boule principale | `7` |
| `sensor.loto_boule_2` | Deuxième boule principale | `14` |
| `sensor.loto_boule_3` | Troisième boule principale | `23` |
| `sensor.loto_boule_4` | Quatrième boule principale | `31` |
| `sensor.loto_boule_5` | Cinquième boule principale | `45` |
| `sensor.loto_boule_chance` | Boule chance | `8` |
| `sensor.loto_date_tirage` | Date du tirage | `Mercredi 25 juin 2025` |
| `sensor.loto_resultat_complet` | Résultat formaté | `7 - 14 - 23 - 31 - 45 * 8` |

## Utilisation dans les cartes

### Carte entités simple
type: entities
title: Résultats Loto FDJ
entities:

    sensor.loto_resultat_complet

    sensor.loto_date_tirage

### Carte personnalisée (boules visuelles)
type: picture-elements
image: /local/loto_background.png
elements:

    type: state-label
    entity: sensor.loto_boule_1
    style:
    top: 50%
    left: 15%

## Automatisations

Exemple d'automatisation pour être notifié des nouveaux résultats :

automation:

    alias: "Notification résultats Loto"
    trigger:

        platform: state
        entity_id: sensor.loto_resultat_complet
        action:

        service: notify.mobile_app
        data:
        title: "Nouveaux résultats Loto !"
        message: "{{ states('sensor.loto_resultat_complet') }}"

## Développement

Contributions bienvenues ! Pour contribuer :

1. Fork ce dépôt
2. Créez une branche feature (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Créez une Pull Request

## Support

- [Issues GitHub](https://github.com/phiphi33/loto/issues)
- [Forum Home Assistant](https://community.home-assistant.io/)

## Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

**Note :** Cette intégration utilise les données publiques du site FDJ. Elle n'est pas affiliée à la Française des Jeux.

