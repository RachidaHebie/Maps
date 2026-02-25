from flask import Flask, render_template
import folium

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