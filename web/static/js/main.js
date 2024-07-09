// Inisialisasi peta
var map = L.map('map').setView([-6.2088, 106.8456], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
}).addTo(map);

// Menambahkan elemen loading screen
var loadingScreen = L.control({ position: 'topright' });

loadingScreen.onAdd = function (map) {
  var div = L.DomUtil.create('div', 'loading-screen');
  div.innerHTML = '<img src="URL_ANIMASI_LOADING" alt="Loading..." />';
  return div;
};

loadingScreen.addTo(map);

// Fungsi untuk menampilkan loading screen
function showLoading() {
  document.querySelector('.loading-screen').style.display = 'block';
}

// Fungsi untuk menyembunyikan loading screen
function hideLoading() {
  document.querySelector('.loading-screen').style.display = 'none';
}

// Fungsi untuk mendapatkan data dari API dan menampilkan rute di peta
function getRouteData() {
  showLoading();
  fetch('/real_world_route')
    .then(response => response.json())
    .then(data => {
      displayRoute(data);
      hideLoading();
    })
    .catch(error => {
      console.error('Error fetching route data:', error);
      hideLoading();
    });
}

// Fungsi untuk menampilkan rute di peta
function displayRoute(data) {
  var locations = data.locations;
  var route = data.route;
  var totalDistance = data.distance;

  var latlngs = [];
  for (let loc in locations) {
    latlngs.push([locations[loc][0], locations[loc][1]]);
  }

  // Menambahkan rute ke peta menggunakan OSRM API untuk mendapatkan rute jalan asli
  var waypoints = latlngs.map(latlng => latlng.reverse().join(',')).join(';'); // Reverse to get [lng, lat]
  var osrmUrl = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;

  fetch(osrmUrl)
    .then(response => response.json())
    .then(data => {
      if (data.routes && data.routes.length > 0) {
        var routeCoordinates = data.routes[0].geometry.coordinates.map(coord => [coord[1], coord[0]]);
        var polyline = L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);

        // Menambahkan marker dan popup untuk setiap lokasi
        for (let loc in locations) {
          L.marker([locations[loc][0], locations[loc][1]])
            .addTo(map)
            .bindPopup(`<b>${loc}</b><br>Latitude: ${locations[loc][0]}<br>Longitude: ${locations[loc][1]}`);
        }

        // Menambahkan informasi jarak total
        L.control.scale().addTo(map);
        L.popup()
          .setLatLng(routeCoordinates[0])
          .setContent(`<b>Total Distance: ${(data.routes[0].distance / 1000).toFixed(2)} km</b>`)
          .openOn(map);

        // Menampilkan jarak antar lokasi pada kartu
        displayDistances(data.routes[0].legs);
      } else {
        console.error('No routes found');
      }
    })
    .catch(error => console.error('Error fetching OSRM route:', error));
}

// Fungsi untuk menampilkan jarak antar lokasi pada kartu
function displayDistances(legs) {
  var distancesHtml = '<h4>Distances Between Locations</h4><ul>';
  legs.forEach((leg, index) => {
    distancesHtml += `<li>Leg ${index + 1}: ${(leg.distance / 1000).toFixed(2)} km</li>`;
  });
  distancesHtml += '</ul>';
  document.getElementById('distances-card').innerHTML = distancesHtml;
}

// Fungsi untuk menambahkan lokasi ke tabel
function addLocation() {
  var locationName = document.getElementById('locationName').value;
  var latitude = document.getElementById('latitude').value;
  var longitude = document.getElementById('longitude').value;

  if (locationName && latitude && longitude) {
    var tableBody = document.getElementById('locations-table-body');
    var newRow = tableBody.insertRow();

    var nameCell = newRow.insertCell(0);
    var latCell = newRow.insertCell(1);
    var lonCell = newRow.insertCell(2);

    nameCell.innerHTML = locationName;
    latCell.innerHTML = latitude;
    lonCell.innerHTML = longitude;

    // Clear the input fields
    document.getElementById('location-form').reset();

    // Close the modal
    $('#locationModal').modal('hide');
  } else {
    alert('Please fill all fields');
  }
}