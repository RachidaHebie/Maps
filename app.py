from flask import Flask, render_template, request, jsonify
import folium
from geopy.geocoders import Nominatim

app = Flask(__name__)

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

# --- NOUVELLE ROUTE POUR L'ÉTAPE 3 ---
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

if __name__ == '__main__':
    app.run(debug=True)