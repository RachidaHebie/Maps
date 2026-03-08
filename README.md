# Optimisation d'Itinéraires via la Théorie des Graphes

## Auteurs
* **HEBIE Tie Rachida**
* **COLOMBAIN Lili**

---

## Objectif du Projet
L'objectif principal de ce projet est l'application concrète des concepts de la **théorie des graphes** à des problématiques de navigation et de logistique. 

Nous avons modélisé un réseau de transport sous forme de graphe (sommets et arêtes pondérées) afin de résoudre des problèmes d'optimisation complexes, allant du trajet simple entre deux points à la planification de tournées multi-étapes.

---

## Aperçu

![Rendu]('static/rendu.png')

## Notre Approche Algorithmique

Pour répondre aux besoins de mobilité, nous avons implémenté deux piliers majeurs de l'algorithmique :

### 1. Recherche du Plus Court Chemin
Nous utilisons des algorithmes de type **Dijkstra** (ou A*) pour déterminer la trajectoire optimale entre un point de départ et une destination. L'utilisateur peut choisir deux critères d'optimisation :
* **Distance :** Minimisation du kilométrage total.
* **Temps :** Calcul basé sur la pondération des arêtes par la vitesse moyenne, permettant de trouver le trajet le plus rapide.

### 2. Problème du Voyageur de Commerce (TSP)
Pour les itinéraires incluant plusieurs points de passage, nous avons intégré une solution au **problème du commerçant**. L'algorithme calcule l'ordre de visite idéal pour passer par tous les points sélectionnés en minimisant le coût global (distance ou temps), illustrant ainsi la gestion de la complexité combinatoire dans les graphes complets.

---

## Installation et Lancement

### Prérequis
* **Python 3.x** installé.

### Lancement de l'application
Pour démarrer l'interface ou le script principal, exécutez la commande suivante à la racine du projet :

```bash
python3 app.py