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
const inputs = ['searchInput', 'start-node', 'end-node'];
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