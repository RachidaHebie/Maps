import networkx as nx
import osmnx as ox
import folium
import numpy as np  
import os


def get_city_graph(place="Belfort, France", network_type="drive", cache_dir="Data"):
    
    os.makedirs(cache_dir, exist_ok=True)

    filename = f"{place.replace(', ', '_')}.graphml"
    filepath = os.path.join(cache_dir, filename)

    if os.path.exists(filepath):
        print(f"Chargement du graphe de {place} depuis le cache...")
        G = ox.load_graphml(filepath)
    else : 
        print(f"Téléchargement du graphe de {place} (ceci peut prendre une minute)...")
        G = ox.graph_from_place(place, network_type=network_type)

        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)

        ox.save_graphml(G, filepath=filepath)
        print(f"Graphe sauvegardé dans {filepath}")

    return G


def calculate_route(G, latitude1, longitude1, latitude2, longitude2):

    orig = ox.distance.nearest_nodes(G, longitude1, latitude1, False)
    dest = ox.distance.nearest_nodes(G, longitude2, latitude2, False)

    route = ox.routing.shortest_path(G, orig, dest, weight='length', cpus=1)

    route_coords = [[G.nodes[node]['y'], G.nodes[node]['x']] for node in route]
    
    # Calcul de la distance totale (en mètres)
    edge_lengths = ox.utils_graph.get_route_edge_attributes(G, route, "length")
    total_distance = sum(edge_lengths)

    # Calcul du temps total (en secondes)
    edge_times = ox.utils_graph.get_route_edge_attributes(G, route, "travel_time")
    total_time = sum(edge_times)

    return {
        "coords": route_coords,
        "distance_m": total_distance,
        "duration_s": total_time
    }
 