// URL dell'API
const apiUrl = 'https://api.skateresults.app/events';

// Variabile per tenere traccia dei dati degli eventi
let eventsData = [];

// Elementi DOM
const dropdown = document.getElementById('event-dropdown');
const eventDetailsDiv = document.getElementById('event-details');
const eventNameSpan = document.getElementById('event-name');
const eventIdSpan = document.getElementById('event-id');
const eventSlugSpan = document.getElementById('event-slug');
const eventStartDateSpan = document.getElementById('event-start-date');
const eventEndDateSpan = document.getElementById('event-end-date');
const downloadButton = document.getElementById('download-json');

// Funzione per ottenere gli eventi dall'API
async function fetchEvents() {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Errore nella richiesta API');
        }
        const data = await response.json();
        eventsData = data.items;

        // Ordina gli eventi per data di inizio, dalla più recente alla meno recente
        eventsData.sort((a, b) => new Date(b.dateBegin) - new Date(a.dateBegin));

        // Popola il dropdown con gli eventi
        populateDropdown(eventsData);
    } catch (error) {
        console.error('Errore:', error);
    }
}

// Funzione per popolare il dropdown con gli eventi
function populateDropdown(events) {
    events.forEach(event => {
        const option = document.createElement('option');
        option.value = event.id;
        option.text = `${event.name} (${event.dateBegin})`;
        dropdown.appendChild(option);
    });
}

// Gestore dell'evento di cambio del dropdown
dropdown.addEventListener('change', function() {
    const selectedId = this.value;

    if (selectedId) {
        const selectedEvent = eventsData.find(event => event.id === selectedId);
        if (selectedEvent) {
            // Mostra i dettagli dell'evento selezionato
            eventNameSpan.textContent = selectedEvent.name;
            eventIdSpan.textContent = selectedEvent.id;
            eventSlugSpan.textContent = selectedEvent.slug;
            eventStartDateSpan.textContent = selectedEvent.dateBegin;
            eventEndDateSpan.textContent = selectedEvent.dateEnd;
            eventDetailsDiv.style.display = 'block';
        }
    } else {
        // Nascondi i dettagli se nessun evento è selezionato
        eventDetailsDiv.style.display = 'none';
    }
});

// Funzione per scaricare il file JSON degli eventi
downloadButton.addEventListener('click', function() {
    const blob = new Blob([JSON.stringify(eventsData, null, 2)], { type: 'application/json' });
    saveAs(blob, 'events_data.json');
});

// Mostra il bottone di download quando i dati sono pronti
function enableDownloadButton() {
    downloadButton.style.display = 'block';
}

// Inizializza l'interfaccia
fetchEvents().then(enableDownloadButton);
