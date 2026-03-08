const searchInput = document.getElementById('searchInput');
const mainBar = document.getElementById('mainBar');
const directionsTrigger = document.getElementById('directionsTrigger');
const fullNavPanel = document.getElementById('full-nav-panel');
const closeBtn = document.getElementById('close-btn');

// 1. Fonction de recherche (ton pont avec Python)
async function searchLocation(address) {
    if (!address || address === "Ma position") return;

    let searchAddress = address;
    if (!address.toLowerCase().includes("belfort")) {
        searchAddress = address + ", Belfort";
    }

    try {
        const response = await fetch('/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: searchAddress })
        });

        const data = await response.json();

        if (data.lat && data.lng) {
            // Utilise 'map' (nom forcé dans app.py)
            map.setView([data.lat, data.lng], 15);
            L.marker([data.lat, data.lng]).addTo(map)
                .bindPopup(data.display_name).openPopup();
        } else {
            alert("Lieu introuvable à Belfort : " + address);
        }
    } catch (error) {
        console.error("Erreur communication serveur:", error);
    }
}

// 2. Écouteurs pour la touche ENTRÉE sur les 3 champs
const inputs = ['searchInput'];
inputs.forEach(id => {
    document.getElementById(id).addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchLocation(this.value);
        }
    });
});

// 3. Gestion de l'interface (Ouverture/Fermeture du panneau)
const openCard = () => {
    fullNavPanel.classList.remove('d-none');
    mainBar.style.borderRadius = "8px 8px 0 0";
};

searchInput.addEventListener('focus', openCard);
directionsTrigger.addEventListener('click', openCard);

closeBtn.addEventListener('click', () => {
    fullNavPanel.classList.add('d-none');
    mainBar.style.borderRadius = "8px";
});

// 4. Style des boutons de transport
const modes = document.querySelectorAll('.mode-btn');
modes.forEach(mode => {
    mode.addEventListener('click', () => {
        modes.forEach(m => m.style.color = "grey");
        mode.style.color = "#1a73e8";
    });
});

async function calculateRoute() {
    const startAddr = document.getElementById('start-node').value;
    const endAddr = document.getElementById('end-node').value;

    if (!startAddr || !endAddr) {
        alert("Veuillez remplir le départ et l'arrivée");
        return;
    }

    try {
        // Étape A : On géocode le départ et l'arrivée en parallèle
        const [resStart, resEnd] = await Promise.all([
            fetch('/geocode', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ address: startAddr + ", Belfort" }) }),
            fetch('/geocode', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ address: endAddr + ", Belfort" }) })
        ]);

        const dataStart = await resStart.json();
        const dataEnd = await resEnd.json();

        if (dataStart.error || dataEnd.error) {
            alert("Une des adresses est introuvable");
            return;
        }

        // Étape B : On appelle ton moteur de calcul (Personne A !)
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: [dataStart.lat, dataStart.lng],
                end: [dataEnd.lat, dataEnd.lng],
                consumption: 6.5, // Tu pourras lier ça à un input plus tard
                fuel_price: 1.85
            })
        });

        const routeData = await response.json();

        if (routeData.status === "success") {
            // Étape C : DESSINER SUR LA CARTE

            // 1. On efface l'ancien trajet s'il existe
            if (currentPolyline) { map.removeLayer(currentPolyline); }

            // 2. On trace le nouveau (Leaflet utilise L.polyline)
            currentPolyline = L.polyline(routeData.coords, {
                color: '#1a73e8',
                weight: 6,
                opacity: 0.8
            }).addTo(map);

            // 3. On ajuste la vue pour voir tout le trajet
            map.fitBounds(currentPolyline.getBounds());



            if (routeData.status === "success") {



                // 2. On affiche le panneau de résumé
                const summaryPanel = document.getElementById('route-summary');
                summaryPanel.classList.remove('d-none');

                // 3. On injecte les valeurs reçues du Python
                document.getElementById('res-distance').innerText = routeData.distance_km;

                // Petite sécurité : si la durée est de 0, on affiche "< 1"
                const duration = routeData.duration_min;
                document.getElementById('res-duration').innerText = duration > 0 ? duration : "< 1";

                // 4. Bonus : Ajuster la vue pour que l'utilisateur voie tout
                map.fitBounds(currentPolyline.getBounds(), { padding: [50, 50] });
            }
        }

    } catch (error) {
        console.error("Erreur globale:", error);
    }
}

// 6. On lie la fonction au clic du bouton
document.getElementById('btn-calculer').addEventListener('click', calculateRoute);