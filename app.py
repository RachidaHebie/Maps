from flask import Flask, render_template, request, jsonify
import folium
<<<<<<< HEAD
from logic import get_city_graph
=======
from logic import get_city_graph 
>>>>>>> 9bb33ae20227ab742bff3bfcacf464bd0e2752ba
from logic import calculate_route 
from geopy.geocoders import Nominatim


app = Flask(__name__)

print("Chargement du réseau routier...")
G = get_city_graph("Belfort, France")
geolocator = Nominatim(user_agent="ecoroute_belfort")


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Route principale - affiche la page d'accueil avec la carte interactive.

    Génère une carte Folium centrée sur Belfort, puis injecte le HTML rendu
    et le nom de l'objet carte dans le template `index.html`

    Returns:
        str: Page HTML complète générée par le template `index.html`.
    """

    ma_carte = folium.Map(
        location=[47.6397, 6.8638],
        zoom_start=15,
        tiles="OpenStreetMap"
    )

    map_name = ma_carte.get_name()
    carte_html = ma_carte.get_root().render()

    return render_template(
        "index.html",
        map_html=carte_html,
        map_name=map_name
    )


@app.route('/geocode', methods=['POST'])
def geocode():
    """
    Route API - convertit une adresse textuelle en coordonnées GPS.

    Reçoit un JSON avec une clé `address`, effectue une géolocalisation via
    Nominatim en restreignant les résultats à la zone de Belfort,
    et retourne les coordonnées trouvées.

    Corps de la requête (JSON):
        address (str): L'adresse ou le lieu saisi par l'utilisateur.

    Returns:
        JSON: 
            - Succès : {"lat": float, "lng": float, "display_name": str}
            - Échec  : {"error": "Lieu introuvable à Belfort"}
    """

    data = request.get_json()
    adresse_saisie = data.get('address')
    
    location = geolocator.geocode(
        f"{adresse_saisie}, Belfort, France", 
        viewbox=[(47.66, 6.82), (47.61, 6.88)], 
        bounded=1.1
    )
    
    if location:
        return jsonify({
            "lat": location.latitude, 
            "lng": location.longitude,
            "display_name": location.address
        })
    
    return jsonify({"error": "Lieu introuvable à Belfort"}), 404


@app.route('/calculate', methods=['POST'])
def handle_request():
    """
    Route API - calcule l'itinéraire le plus court entre deux points GPS.

    Reçoit un JSON avec les coordonnées de départ et d'arrivée, appelle
    `calculate_route` depuis le module `logic`, puis enrichit le résultat
    avec le coût en carburant estimé si le calcul a réussi.

    Corps de la requête (JSON):
        start (list): Coordonnées du départ  [lat, lon].
        end   (list): Coordonnées d'arrivée  [lat, lon].

    Returns:
        JSON: Résultat de `calculate_route` enrichi de :
            - "fuel_cost" (float) : Coût estimé du trajet en carburant (€),
                                    calculé avec les variables `conso` et `prix`.

    Note:
        Les variables `conso` (consommation en L/100km) et `prix` (prix du
        carburant en €/L) doivent être définies ou passées dans la requête
        pour que le calcul du coût soit correct.
    """
    
    data = request.get_json()
    
    start_list = data.get('start') 
    end_list = data.get('end')    

    lat1 = start_list[0]
    lon1 = start_list[1]
    lat2 = end_list[0]
    lon2 = end_list[1]

    result = calculate_route(G, lat1, lon1, lat2, lon2)
    
    '''
    # Argent/Eco
    if result['status'] == 'success':
        dist_km = result['distance_km']
        cout_final = (dist_km / 100) * conso * prix
        result['fuel_cost'] = round(cout_final, 2)
    '''
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

