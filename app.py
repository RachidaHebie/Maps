from flask import Flask, render_template, request, jsonify
import folium
from logic import get_city_graph 
from logic import calculate_route 
from geopy.geocoders import Nominatim

app = Flask(__name__)

print("Chargement du réseau routier...")
G = get_city_graph("Belfort, France")

# Initialisation du géocodeur en dehors des fonctions
geolocator = Nominatim(user_agent="ecoroute_belfort")



@app.route('/')
def index():
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
    # On récupère l'adresse envoyée par le JavaScript
    data = request.get_json()
    adresse_saisie = data.get('address')
    
    # On utilise ta logique de recherche limitée à Belfort
    location = geolocator.geocode(
        f"{adresse_saisie}, Belfort, France", 
        viewbox=[(47.66, 6.82), (47.61, 6.88)], 
        bounded=1
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
    
    data = request.get_json()
    
   
    # 1. On récupère les listes [lat, lon]
    start_list = data.get('start') # Résultat: [47.63, 6.85]
    end_list = data.get('end')     # Résultat: [47.64, 6.86]

    # 2. On extrait chaque coordonnée par son index
    lat1 = start_list[0]
    lon1 = start_list[1]
    lat2 = end_list[0]
    lon2 = end_list[1]

    # 3. On appelle ta fonction avec les 5 arguments attendus
    result = calculate_route(G, lat1, lon1, lat2, lon2)
    '''
    # 4. Si le calcul a réussi, on ajoute la partie "Argent/Eco"
    if result['status'] == 'success':
        dist_km = result['distance']
        # Calcule le coût ici avec ta formule !
        cout_final = (dist_km / 100) * conso * prix
        
        # On ajoute cette info au dictionnaire de résultat
        result['fuel_cost'] = round(cout_final, 2)
    '''
    # 5. On renvoie tout au Frontend
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

