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

import networkx as nx

def travelling_salesman(G, coords_list):
    # 1. Préparation du graphe et des nœuds
    G_undirected = G.to_undirected()
    nodes_to_visit = [ox.distance.nearest_nodes(G, lon, lat) for lat, lon in coords_list]

    # 2. Calcul de l'ordre optimal (TSP)
    nodes_order = traveling_salesman_problem(G_undirected, nodes=nodes_to_visit, weight='length')

    tsp_coords = []
    total_dist_m = 0

    # 3. Calcul des stats et préparation des coordonnées
    for i in range(len(nodes_order) - 1):
        u, v = nodes_order[i], nodes_order[i+1]
        
        # On calcule la distance RÉELLE sur route entre deux étapes (même si on l'affiche en ligne droite)
        total_dist_m += nx.shortest_path_length(G, u, v, weight='length')
        
        # Ajout des coordonnées pour l'affichage
        tsp_coords.append([G.nodes[u]['y'], G.nodes[u]['x']])

    # On ajoute le dernier point de la liste
    last_node = nodes_order[-1]
    tsp_coords.append([G.nodes[last_node]['y'], G.nodes[last_node]['x']])

    # 4. Conversion des stats
    dist_km = round(total_dist_m / 1000, 2)
    # Estimation du temps : moyenne de 20 km/h en ville (incluant feux et trafic)
    duration_min = round((dist_km / 20) * 60)

    return {
        "status": "success",
        "coords": tsp_coords,
        "distance_km": dist_km,
        "duration_min": duration_min,
        "order": nodes_order
    }
    

def test_marchand_belfort():
    print("🚀 Démarrage du test : Algorithme du Marchand (TSP)")
    
    # 1. On récupère le graphe de Belfort
    G = get_city_graph("Belfort, France")

    # 2. Points de test mélangés (Gare -> IUT -> Lion -> Marché)
    # Dans cet ordre, c'est pas optimisé du tout !
    test_waypoints = [
        [47.63197082746643, 6.858827884305796], # A - Gare de Belfort
        [47.64454142848342, 6.857978086228185], # B - IUT (Technopôle) -> Loin au Nord-Ouest
        [47.64587288281944, 6.855428692980198], # C - Le Lion (Est) -> On revient en arrière
        [47.64888184453169, 6.849954414230187], # D - Marché des Vosges (Nord)
    ]

    # 3. Calcul de la tournée optimisée
    print("🧠 Calcul de l'ordre le plus court...")
    result = voyageur(G, test_waypoints)

    if result['status'] == 'success':
        # 4. Création de la carte de test
        m = folium.Map(location=[47.64, 6.85], zoom_start=14)

        # 5. Dessin du trajet optimisé
        folium.PolyLine(
            locations=result['coords'],
            color="#28a745", # Vert pour le côté "Eco"
            weight=6,
            opacity=0.8,
            
        ).add_to(m)

        # 6. Affichage des étapes avec des numéros
        for i, coord in enumerate(test_waypoints):
            # On crée une icône avec le numéro de l'étape
            folium.Marker(
                location=coord,
                popup=f"Étape : {i+1}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

        # 7. Sauvegarde et verdict
        filename = "test_marchand_belfort.html"
        m.save(filename)
        print(f"✅ Test terminé !")
        
        print(f"📂 Résultat généré dans : {filename}")
    else:
        print(f"❌ Erreur : {result.get('message')}")

if __name__ == "__main__":
    test_marchand_belfort()