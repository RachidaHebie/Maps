import networkx as nx
import osmnx as ox
import folium
import numpy as np 
import os
from index import get_city_graph


# 2. Définir les points de départ et d'arrivée
orig = (47.6397, 6.8645)
dest = (47.6450, 6.8520)


G = id.get_city_graph()
# 3. Trouver le chemin
orig_node = ox.distance.nearest_nodes(G, orig[1], orig[0])
dest_node = ox.distance.nearest_nodes(G, dest[1], dest[0])
path = nx.shortest_path(G, orig_node, dest_node, weight="length")
path_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in path]

# 4. Créer la carte
m = folium.Map(location=orig, zoom_start=14)

# Ajouter les marqueurs et le trajet
folium.Marker(orig, popup="Départ", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(dest, popup="Arrivée", icon=folium.Icon(color="red")).add_to(m)
folium.PolyLine(path_coords, color="blue", weight=5, popup="Trajet").add_to(m)

# 5. Sauvegarder et ouvrir
m.save("carte_trajet.html")
print("Carte générée : ouvre 'carte_trajet.html' dans ton navigateur !")