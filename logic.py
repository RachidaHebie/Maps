import networkx as nx
from networkx.algorithms.approximation import traveling_salesman_problem


import osmnx as ox
import folium
import numpy as np  
import os


# ---------------------------------------- #
# --------- Le plus court chemin --------- #
# ---------------------------------------- #

# Récupère le graphe de Belfort et les données correspondantes 
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


# Calcule le plus court chemin et renvoie aussi la distance et le temps necessaire
def calculate_route(G, lat1, lon1, lat2, lon2):

    orig = ox.distance.nearest_nodes(G, lon1, lat1, False)
    dest = ox.distance.nearest_nodes(G, lon2, lat2, False)

    route = ox.routing.shortest_path(G, orig, dest, weight='length', cpus=1)
    

    gdf_edges = ox.utils_graph.route_to_gdf(G, route)
    
    route_coords = []
    for _, edge in gdf_edges.iterrows():
        if 'geometry' in edge:
            coords = list(edge['geometry'].coords)
            for p in coords:
                route_coords.append([p[1], p[0]])
        else:
            # Si c'est une ligne droite, on prend juste le point de départ
            pass

    final_coords = []
    for c in route_coords:
        if not final_coords or c != final_coords[-1]:
            final_coords.append(c)

    return {
        "status": "success",
        "coords": final_coords, # Ces coordonnées suivront les virages
        "distance_km": round(gdf_edges['length'].sum() / 1000, 2),
        "duration_min": int(gdf_edges['travel_time'].sum() / 60) if 'travel_time' in gdf_edges else 0
    }
 

# Test de la visualisation du trajet
def visualize_on_map(resultat_calcul):
    
    depart = resultat_calcul['coords'][0]
    m = folium.Map(location=depart, zoom_start=14)

    chemin = folium.PolyLine(
        locations=resultat_calcul['coords'], 
        color="blue", 
        weight=5, 
        opacity=0.8
    )
    
    chemin.add_to(m)

    folium.Marker(resultat_calcul['coords'][0], popup="Départ", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(resultat_calcul['coords'][-1], popup="Arrivée", icon=folium.Icon(color='red')).add_to(m)

    m.save("mon_itineraire.html")
    print("La carte a été générée : ouvre mon_itineraire.html dans ton navigateur !")


G = get_city_graph()
res = calculate_route(G, 47.638742628679125, 6.861235261467314, 47.63924143562703, 6.863434672713001)
visualize_on_map(res)


# ---------------------------------------- #
# --- Problème du Voyageur de Commerce --- #
# ---------------------------------------- #

def voyageur(G, nodes):
    