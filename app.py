from flask import Flask, render_template
import folium
import get_city_graph from logic
import calculate_route from logic

app = Flask(__name__)

@app.route('/')
def index():
    # Coordonnées de Belfort : 47.6397, 6.8638
    # On initialise la carte sur Belfort avec un zoom de 13
    ma_carte = folium.Map(
        location=[47.6397, 6.8638], 
        zoom_start=15,
        tiles="OpenStreetMap",
        zoom_control=False # On cache les boutons +/- pour un look plus "Google Maps"
    )

    # On convertit la carte en HTML pour l'injecter dans le template
    carte_en_html = ma_carte._repr_html_()

    return render_template('index.html', map_html=carte_en_html)

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/calculate', methods=['POST'])
def handle_request():
    
    data = request.get_json()
    
   
    start_coords = data.get('start') # [lat, lon]
    end_coords = data.get('end')     # [lat, lon]
    conso = data.get('consumption', 6.0) 
    prix = data.get('fuel_price', 1.80)

    
    result = calculate_route(G, start_coords, end_coords)
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