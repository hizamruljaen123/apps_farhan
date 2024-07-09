// Inisialisasi peta
var map = L.map('map').setView([-6.2088, 106.8456], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
}).addTo(map);

// Menambahkan elemen loading screen
var loadingScreen = L.control({ position: 'topright' });

loadingScreen.onAdd = function (map) {
  var div = L.DomUtil.create('div', 'loading-screen');
  div.innerHTML = '<img src="https://media.tenor.com/dHAJxtIpUCoAAAAi/loading-animation.gif" alt="Loading..." />';
  return div;
};

loadingScreen.addTo(map);

// Fungsi untuk menampilkan dan menyembunyikan loading screen
function toggleLoading(show) {
  document.querySelector('.loading-screen').style.display = show ? 'block' : 'none';
}

// Fungsi untuk mendapatkan data dari API dan menampilkan rute di peta
function getRouteData() {
  toggleLoading(true);
  fetch('/real_world_route')
    .then(response => response.json())
    .then(data => {
      displayRoute(data);
      toggleLoading(false);
    })
    .catch(error => {
      console.error('Error fetching route data:', error);
      toggleLoading(false);
    });
}

// Fungsi untuk menampilkan rute di peta
function displayRoute(data) {
  const { locations, route, distance: totalDistance } = data;
  const latlngs = Object.values(locations).map(loc => [loc[0], loc[1]]);

  // Menambahkan rute ke peta menggunakan OSRM API untuk mendapatkan rute jalan asli
  const waypoints = latlngs.map(latlng => latlng.reverse().join(',')).join(';');
  const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;

  fetch(osrmUrl)
    .then(response => response.json())
    .then(data => {
      if (data.routes && data.routes.length > 0) {
        displayRealWorldRoute(data.routes[0], locations, route, totalDistance);
      } else {
        console.error('No routes found');
      }
    })
    .catch(error => console.error('Error fetching OSRM route:', error));
}

// Fungsi untuk menampilkan rute jalan nyata di peta
function displayRealWorldRoute(routeData, locations, route, totalDistance) {
  const routeCoordinates = routeData.geometry.coordinates.map(coord => [coord[1], coord[0]]);

  // Hapus rute sebelumnya dari peta
  if (window.currentPolyline) {
    map.removeLayer(window.currentPolyline);
  }

  // Tambahkan rute ke peta
  window.currentPolyline = L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);

  // Tambahkan marker dan popup untuk setiap lokasi
  route.forEach((node, index) => {
    const locName = node;
    const loc = locations[locName];
    L.marker([loc[0], loc[1]])
      .addTo(map)
      .bindPopup(`<b>${locName}</b><br>Latitude: ${loc[0]}<br>Longitude: ${loc[1]}`);
  });

  // Tambahkan informasi jarak total
  L.control.scale().addTo(map);
  L.popup()
    .setLatLng(routeCoordinates[0])
    .setContent(`<b>Jarak Total: ${totalDistance.toFixed(2)} km</b>`)
    .openOn(map);

  // Pusatkan peta pada rute
  map.fitBounds(window.currentPolyline.getBounds());

  // Menampilkan jarak antar lokasi pada kartu
  displayDistances(routeData.legs, route);
}

// Fungsi untuk menampilkan jarak antar lokasi pada kartu
function displayDistances(legs, routeNames) {
  let distancesHtml = '<h4>Jarak Antara Lokasi</h4><ul>';
  legs.forEach((leg, index) => {
    const distance = (leg.distance / 1000).toFixed(2);
    distancesHtml += `<li>Dari ${routeNames[index % routeNames.length]} ke ${routeNames[(index + 1) % routeNames.length]}: ${distance} km</li>`;
  });
  distancesHtml += '</ul>';
  document.getElementById('distances-card').innerHTML = distancesHtml;
}

// Fungsi untuk menambahkan lokasi ke tabel utama
function addLocationToTable(locationName, latitude, longitude) {
  const tableBody = document.getElementById('locations-table-body');
  const newRow = tableBody.insertRow();

  newRow.insertCell(0).innerText = locationName;
  newRow.insertCell(1).innerText = latitude;
  newRow.insertCell(2).innerText = longitude;

  const actionCell = newRow.insertCell(3);
  const deleteButton = document.createElement('button');
  deleteButton.className = 'btn btn-sm btn-danger';
  deleteButton.innerText = 'Delete';
  deleteButton.onclick = () => tableBody.deleteRow(newRow.rowIndex - 1);
  actionCell.appendChild(deleteButton);
}

// Fungsi untuk menambahkan lokasi dari modal ke tabel utama
function addLocation() {
  const locationName = document.getElementById('locationName').value;
  const latitude = document.getElementById('latitude').value;
  const longitude = document.getElementById('longitude').value;

  if (locationName && latitude && longitude) {
    addLocationToTable(locationName, latitude, longitude);
    document.getElementById('location-form').reset();
  } else {
    alert('Please fill all fields');
  }
}

// Fungsi untuk mencari lokasi berdasarkan nama wilayah menggunakan API Nominatim
function searchLocation() {
  const locationName = document.getElementById('locationName').value;
  const locationSuggestions = document.getElementById('locationSuggestions');
  locationSuggestions.innerHTML = '<a class="list-group-item list-group-item-action">Loading...</a>';

  if (locationName.length < 3) {
    locationSuggestions.innerHTML = '';
    return;
  }

  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${locationName}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      locationSuggestions.innerHTML = '';
      const searchResultsTableBody = document.getElementById('search-results-table-body');
      searchResultsTableBody.innerHTML = '';
      data.forEach(location => {
        const suggestionItem = document.createElement('a');
        suggestionItem.className = 'list-group-item list-group-item-action';
        suggestionItem.innerText = location.display_name;
        suggestionItem.onclick = () => {
          document.getElementById('locationName').value = location.display_name;
          document.getElementById('latitude').value = location.lat;
          document.getElementById('longitude').value = location.lon;
          locationSuggestions.innerHTML = '';
        };
        locationSuggestions.appendChild(suggestionItem);

        // Add to search results table
        const newRow = searchResultsTableBody.insertRow();
        newRow.insertCell(0).innerText = location.display_name;
        newRow.insertCell(1).innerText = location.lat;
        newRow.insertCell(2).innerText = location.lon;

        const actionCell = newRow.insertCell(3);
        const addButton = document.createElement('button');
        addButton.className = 'btn btn-sm btn-primary';
        addButton.innerText = 'Add';
        addButton.onclick = () => {
          addLocationToTable(location.display_name, location.lat, location.lon);
          document.getElementById('locationName').value = '';
          document.getElementById('latitude').value = '';
          document.getElementById('longitude').value = '';
          searchResultsTableBody.innerHTML = '';
          $('#locationModal').modal('hide');
        };
        actionCell.appendChild(addButton);
      });
    })
    .catch(error => {
      console.error('Error fetching location data:', error);
      locationSuggestions.innerHTML = '';
    });
}

// Fungsi untuk mendapatkan rute dari daftar lokasi di tabel utama
function getRouteFromList() {
  const tableBody = document.getElementById('locations-table-body');
  const locations = Array.from(tableBody.rows).map(row => ({
    name: row.cells[0].innerText,
    lat: parseFloat(row.cells[1].innerText),
    lon: parseFloat(row.cells[2].innerText),
  }));

  if (locations.length < 2) {
    alert('Please add at least two locations to get a route.');
    return;
  }

  toggleLoading(true);

  fetch('/getroutesfromlist', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ locations })
  })
    .then(response => response.json())
    .then(data => {
      console.log(data, "DARI API");
      toggleLoading(false);
      getRealWorldRoute(data);
    })
    .catch(error => {
      console.error('Error fetching route from list:', error);
      toggleLoading(false);
    });
}

// Fungsi untuk mendapatkan rute jalan nyata dari OSRM
function getRealWorldRoute(data) {
  const { locations, route, distance: totalDistance, route_names: routeNames } = data;

  const waypoints = route.map((node, index) => {
    const loc = locations[routeNames[index % routeNames.length]];
    return [loc[1], loc[0]].join(','); // [lon, lat]
  }).join(';');

  const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;

  fetch(osrmUrl)
    .then(response => response.json())
    .then(data => {
      if (data.routes && data.routes.length > 0) {
        displayRealWorldRoute(data.routes[0], locations, routeNames, totalDistance);
      } else {
        console.error('No routes found');
      }
    })
    .catch(error => console.error('Error fetching OSRM route:', error));
}

// Fungsi untuk menampilkan rute jalan nyata di peta
function displayRealWorldRoute(routeData, locations, routeNames, totalDistance) {
  const routeCoordinates = routeData.geometry.coordinates.map(coord => [coord[1], coord[0]]);

  // Hapus rute sebelumnya dari peta
  if (window.currentPolyline) {
    map.removeLayer(window.currentPolyline);
  }

  // Tambahkan rute ke peta
  window.currentPolyline = L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);

  // Tambahkan marker dan popup untuk setiap lokasi
  routeNames.forEach((locName, index) => {
    const loc = locations[locName];
    L.marker([loc[0], loc[1]])
      .addTo(map)
      .bindPopup(`<b>${locName}</b><br>Latitude: ${loc[0]}<br>Longitude: ${loc[1]}`);
  });

  // Tambahkan informasi jarak total
  L.control.scale().addTo(map);
  L.popup()
    .setLatLng(routeCoordinates[0])
    .setContent(`<b>Jarak Total: ${totalDistance.toFixed(2)} km</b>`)
    .openOn(map);

  // Pusatkan peta pada rute
  map.fitBounds(window.currentPolyline.getBounds());

  // Menampilkan jarak antar lokasi pada kartu
  displayDistances(routeData.legs, routeNames);
}

// Fungsi untuk menampilkan jarak antar lokasi pada kartu
function displayDistances(legs, routeNames) {
  let distancesHtml = '<h4>Jarak Antara Lokasi</h4><ul>';
  legs.forEach((leg, index) => {
    const distance = (leg.distance / 1000).toFixed(2);
    distancesHtml += `<li>Dari ${routeNames[index % routeNames.length]} ke ${routeNames[(index + 1) % routeNames.length]}: ${distance} km</li>`;
  });
  distancesHtml += '</ul>';
  document.getElementById('distances-card').innerHTML = distancesHtml;
}

// Fungsi untuk menyimpan rute
function saveRoute() {
  const tableBody = document.getElementById('locations-table-body');
  const routeName = document.getElementById('routeName').value;
  const totalDistance = window.totalDistance || 0; // Total distance should be set when displaying the route
  const routes = Array.from(tableBody.rows).map((row, index) => ({
    name: row.cells[0].innerText,
    lat: parseFloat(row.cells[1].innerText),
    lon: parseFloat(row.cells[2].innerText),
    sequence: index
  }));

  if (!routeName) {
    alert('Please enter a route name.');
    return;
  }

  if (routes.length < 2) {
    alert('Please add at least two locations to save a route.');
    return;
  }

  fetch('/save_routes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ route_name: routeName, distance: totalDistance, routes })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showModal();
        setTimeout(() => {
          hideModal();
          $('#routeModal').modal('hide');
        }, 3000);
      } else {
        console.error('Error saving route:', data.error);
      }
    })
    .catch(error => {
      console.error('Error saving route:', error);
    });
}

// Fungsi untuk membuka modal daftar rute
function openRoutesListModal() {
  fetch('/get_routes_list')
    .then(response => response.json())
    .then(data => {
      const routesListContainer = document.getElementById('routes-list-container');
      routesListContainer.innerHTML = '';
      data.routes.forEach(route => {
        const listItem = document.createElement('a');
        listItem.className = 'list-group-item list-group-item-action';
        listItem.innerText = route.name;
        listItem.onclick = function() {
          showRouteDetails(route.id);
        };
        routesListContainer.appendChild(listItem);
      });
      $('#routesListModal').modal('show');
    })
    .catch(error => console.error('Error fetching routes list:', error));
}

// Fungsi untuk menampilkan detail rute dalam bentuk tabel
function showRouteDetails(routeId) {
  fetch(`/get_route_details/${routeId}`)
    .then(response => response.json())
    .then(data => {
      const routeDetailsTableBody = document.getElementById('route-details-table-body');
      routeDetailsTableBody.innerHTML = '';
      data.routes.forEach(route => {
        const newRow = routeDetailsTableBody.insertRow();
        const nameCell = newRow.insertCell(0);
        const latCell = newRow.insertCell(1);
        const lonCell = newRow.insertCell(2);
        nameCell.innerText = route.name;
        latCell.innerText = route.lat;
        lonCell.innerText = route.lon;
      });
      document.getElementById('loadRouteButton').onclick = function() {
        loadRouteOnMap(data.routes);
      };
      $('#routeDetailsModal').modal('show');
    })
    .catch(error => console.error('Error fetching route details:', error));
}

// Fungsi untuk memuat rute ke peta
function loadRouteOnMap(routes) {
  const latlngs = routes.map(route => [route.lat, route.lon]);
  const waypoints = latlngs.map(latlng => latlng.reverse().join(',')).join(';'); // Reverse to get [lng, lat]

  const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;

  fetch(osrmUrl)
    .then(response => response.json())
    .then(data => {
      if (data.routes && data.routes.length > 0) {
        const routeCoordinates = data.routes[0].geometry.coordinates.map(coord => [coord[1], coord[0]]);

        // Hapus rute sebelumnya dari peta
        if (window.currentPolyline) {
          map.removeLayer(window.currentPolyline);
        }

        // Tambahkan rute ke peta
        window.currentPolyline = L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);

        // Tambahkan marker dan popup untuk setiap lokasi
        routes.forEach((route, index) => {
          L.marker([route.lat, route.lon])
            .addTo(map)
            .bindPopup(`<b>${route.name}</b><br>Latitude: ${route.lat}<br>Longitude: ${route.lon}`);
        });

        // Pusatkan peta pada rute
        map.fitBounds(window.currentPolyline.getBounds());

        // Menampilkan jarak total dan jarak antar lokasi
        const totalDistance = data.routes[0].distance / 1000; // in km
        let distancesHtml = `<h4>Jarak Antara Lokasi</h4><ul>`;
        data.routes[0].legs.forEach((leg, index) => {
          const from = routes[index].name;
          const to = routes[index + 1] ? routes[index + 1].name : routes[0].name;
          const distance = (leg.distance / 1000).toFixed(2);
          distancesHtml += `<li>Dari ${from} ke ${to}: ${distance} km</li>`;
        });
        distancesHtml += `</ul><p><b>Jarak Total: ${totalDistance.toFixed(2)} km</b></p>`;
        document.getElementById('distances-card').innerHTML = distancesHtml;

        // Menampilkan rute di tabel utama dan sembunyikan kolom Delete
        const tableBody = document.getElementById('locations-table-body');
        tableBody.innerHTML = '';
        routes.forEach((route, index) => {
          const newRow = tableBody.insertRow();
          const nameCell = newRow.insertCell(0);
          const latCell = newRow.insertCell(1);
          const lonCell = newRow.insertCell(2);
          nameCell.innerText = route.name;
          latCell.innerText = route.lat;
          lonCell.innerText = route.lon;
        });

        document.querySelectorAll('.delete-column').forEach(column => {
          column.style.display = 'none';
        });

        $('#routeDetailsModal').modal('hide');
      } else {
        console.error('No routes found');
      }
    })
    .catch(error => console.error('Error fetching OSRM route:', error));
}

// Fungsi untuk mengembalikan kolom Delete
function showDeleteColumn() {
  document.querySelectorAll('.delete-column').forEach(column => {
    column.style.display = '';
  });
}

function saveTransport() {
  const tableBody = document.getElementById('transportTableBody');
  const rows = tableBody.getElementsByTagName('tr');
  const transportData = Array.from(rows).map(row => {
    const cells = row.getElementsByTagName('td');
    return {
      nama_kendaraan: cells[0].innerText || cells[0].children[0].value,
      plat_nomor: cells[1].innerText || cells[1].children[0].value,
      kondisi: cells[2].innerText || cells[2].children[0].value,
      nama_supir: cells[3].innerText || cells[3].children[0].value,
      nomor_telepon: cells[4].innerText || cells[4].children[0].value,
      status_keberangkatan: cells[5].innerText || cells[5].children[0].value
    };
  });

  fetch('/save_transport', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ transport: transportData })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showModalAngkutan('Data angkutan berhasil disimpan.');
      setTimeout(() => {
        hideModalAngkutan();
        showTransportModal(); // Reload table
      }, 3000);
    } else {
      console.error('Error saving transport:', data.error);
    }
  })
  .catch(error => console.error('Error saving transport:', error));
}

// Function to show transport modal and fetch data
function showTransportModal() {
  fetch('/angkutan_list')
    .then(response => response.json())
    .then(data => {
      populateTransportTable(data);
      $('#transportModal').modal('show');
    })
    .catch(error => console.error('Error fetching angkutan list:', error));
}

// Function to populate transport table
function populateTransportTable(data) {
  const tableBody = document.getElementById('transportTableBody');
  tableBody.innerHTML = ''; // Clear existing rows

  data.forEach(item => {
    const newRow = tableBody.insertRow();

    newRow.insertCell(0).innerText = item.nama_kendaraan;
    newRow.insertCell(1).innerText = item.plat_nomor;
    newRow.insertCell(2).innerText = item.kondisi;
    newRow.insertCell(3).innerText = item.nama_supir;
    newRow.insertCell(4).innerText = item.nomor_telepon;
    newRow.insertCell(5).innerText = item.status_keberangkatan;

    const actionCell = newRow.insertCell(6);
    actionCell.innerHTML = '<button class="btn btn-sm btn-danger" onclick="deleteRow(this)">Hapus</button>';
  });
}

// Function to add transport row
function addTransportRow() {
  const tableBody = document.getElementById('transportTableBody');
  const newRow = tableBody.insertRow();

  newRow.insertCell(0).innerHTML = '<input type="text" class="form-control" placeholder="Nama Kendaraan">';
  newRow.insertCell(1).innerHTML = '<input type="text" class="form-control" placeholder="Plat Nomor">';
  newRow.insertCell(2).innerHTML = '<input type="text" class="form-control" placeholder="Kondisi">';
  newRow.insertCell(3).innerHTML = '<input type="text" class="form-control" placeholder="Nama Supir">';
  newRow.insertCell(4).innerHTML = '<input type="text" class="form-control" placeholder="Nomor Telepon">';
  newRow.insertCell(5).innerHTML = '<input type="text" class="form-control" placeholder="Status Keberangkatan">';

  const actionCell = newRow.insertCell(6);
  actionCell.innerHTML = '<button class="btn btn-sm btn-danger" onclick="deleteRow(this)">Hapus</button>';
}

// Function to delete row
function deleteRow(button) {
  const row = button.parentNode.parentNode;
  row.parentNode.removeChild(row);
}

// Function to show modal angkutan with a message
function showModalAngkutan(message) {
  const modalHtml = `
    <div class="modal fade" id="messageModal" tabindex="-1" role="dialog" aria-labelledby="messageModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="messageModalLabel">Informasi</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            ${message}
          </div>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  $('#messageModal').modal('show');
  setTimeout(() => {
    $('#messageModal').modal('hide');
  }, 3000);
}

function hideModalAngkutan() {
  $('#messageModal').modal('hide');
  document.getElementById('messageModal').remove();
}

let scheduleData = {}; // Placeholder for schedule data

// Function to load schedule count and update the calendar
// Function to load schedule count and update the calendar
function loadScheduleCount() {
  const year = $('#yearSelect').val();
  const month = $('#monthSelect').val();
  const date = `${year}-${String(month).padStart(2, '0')}`;

  fetch(`/get_schedule_count/${date}`)
    .then(response => response.json())
    .then(data => {
      data.forEach(item => {
        const { date, count } = item;
        const dayElement = $(`#day-${date}`);
        if (dayElement.length) {
          dayElement.addClass('has-schedule');
          dayElement.append(`<div class="schedule-count">${count} Jadwal</div>`);
        }
      });
    })
    .catch(error => {
      console.error('Error fetching schedule count:', error);
    });
}


// Function to generate calendar with year and month selection
function generateCalendar() {
  const calendar = $('#calendar');
  calendar.empty();
  const today = new Date();
  const year = $('#yearSelect').val() || today.getFullYear();
  const month = $('#monthSelect').val() - 1 || today.getMonth();  // Subtract 1 to get the correct month index

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  // Fill calendar with empty days until the first day of the month
  for (let i = 0; i < firstDay.getDay(); i++) {
    calendar.append('<div class="calendar-day"></div>');
  }

  // Fill calendar with days of the month
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    calendar.append(`<div class="calendar-day" id="day-${dateStr}" onclick="loadScheduleByDate('${dateStr}')">${day}</div>`);
  }

  loadScheduleCount(); // Load schedule count after generating calendar
  loadScheduleData();
}



// Function to show calendar modal and initialize year and month selection
function showCalendarModal() {
  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1;  // Add 1 to get the correct month value

  const yearSelect = $('#yearSelect');
  const monthSelect = $('#monthSelect');

  // Populate year selection
  yearSelect.empty();  // Clear existing options
  for (let i = currentYear - 10; i <= currentYear + 10; i++) {
    yearSelect.append(new Option(i, i));
  }
  yearSelect.val(currentYear);

  // Populate month selection
  monthSelect.empty();  // Clear existing options
  for (let i = 1; i <= 12; i++) {
    monthSelect.append(new Option(new Date(0, i - 1).toLocaleString('default', { month: 'long' }), i));
  }
  monthSelect.val(currentMonth);

  generateCalendar();
  $('#scheduleModal').modal('show');
}


// Add event listeners for year and month selection
$('#yearSelect').on('change', generateCalendar);
$('#monthSelect').on('change', generateCalendar);

// Modify the function to populate schedule table to include the date
function showSchedule(date) {
  const formattedDate = new Date(date).toLocaleDateString('id-ID', {
    weekday: 'long',
    year: 'numeric',
    month: 'numeric',
    day: 'numeric'
  });
  $('#scheduleDate').text(`Jadwal ${formattedDate}`);

  fetch(`/get_schedule_by_date/${date}`)
    .then(response => response.json())
    .then(data => {
      populateScheduleTable(data, date);
      $('#scheduleTableContainer').show();
    })
    .catch(error => {
      console.error('Error fetching schedule data:', error);
    });
}

function populateScheduleTable(data, date) {
  const tableBody = $('#scheduleTableBody');
  tableBody.empty();

  data.forEach(item => {
    const newRow = `<tr>
                      <td>${item.nama_kendaraan}</td>
                      <td>${item.barang}</td>
                      <td>${item.jumlah_ton}</td>
                      <td>${item.nama_rute}</td>
                      <td><span class="schedule-date">${date}</span></td>
                      <td><button class="btn btn-sm btn-danger" onclick="deleteRow(this)">Hapus</button></td>
                    </tr>`;
    tableBody.append(newRow);
  });
}

function loadTransportList() {
  fetch('/angkutan_list')
    .then(response => response.json())
    .then(data => {
      const transportSelect = document.getElementById('transportSelect');
      window.transportOptions = data.map(item => 
        `<option value="${item.id}">${item.nama_kendaraan} - ${item.plat_nomor}</option>`
      ).join('');
      transportSelect.innerHTML = window.transportOptions;
    })
    .catch(error => console.error('Error fetching transport list:', error));
}

function loadRouteList() {
  fetch('/get_route_list')
    .then(response => response.json())
    .then(data => {
      const routeSelect = document.getElementById('routeSelect');
      window.routeOptions = data.map(item => 
        `<option value="${item.id}">${item.name}</option>`
      ).join('');
      routeSelect.innerHTML = window.routeOptions;
    })
    .catch(error => console.error('Error fetching route list:', error));
}

function addScheduleRow() {
  const date = $('#scheduleDate').text().split(' ')[2];
  const transportSelectOptions = window.transportOptions || ''; // Use the global variable
  const routeSelectOptions = window.routeOptions || ''; // Use the global variable
  
  const newRow = `<tr>
                    <td>
                      <select class="form-control">
                        ${transportSelectOptions}
                      </select>
                    </td>
                    <td><input type="text" class="form-control" placeholder="Barang"></td>
                    <td><input type="text" class="form-control" placeholder="Jumlah Ton"></td>
                    <td>
                      <select class="form-control">
                        ${routeSelectOptions}
                      </select>
                    </td>
                    <td>${date}</td>
                    <td><button class="btn btn-sm btn-danger" onclick="deleteRow(this)">Hapus</button></td>
                  </tr>`;
  $('#scheduleTableBody').append(newRow);
}

// Initial call to load the transport list
loadTransportList();
loadRouteList();

function convertDateToYMD(dateStr) {
  const [day, month, year] = dateStr.split('/');
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}

function saveSchedule() {
  const tableBody = $('#scheduleTableBody');
  const rows = tableBody.find('tr');
  const scheduleData = rows.map(function() {
    const cells = $(this).find('td');
    return {
      id_angkutan: cells.eq(0).find('select').val(),
      barang: cells.eq(1).find('input').val(),
      jumlah_ton: cells.eq(2).find('input').val(),
      id_rute: cells.eq(3).find('select').val(),
      date: convertDateToYMD(cells.eq(4).text())
    };
  }).get();

  fetch('/save_schedule', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ schedule: scheduleData })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      $('#scheduleModal').modal('hide');
      loadScheduleData();
    } else {
      console.error('Error saving schedule:', data.error);
    }
  })
  .catch(error => console.error('Error saving schedule:', error));
}

function loadScheduleByDate(date) {
  const formattedDate = new Date(date).toLocaleDateString('id-ID', {
    weekday: 'long',
    year: 'numeric',
    month: 'numeric',
    day: 'numeric'
  });
  $('#scheduleDate').text(`Jadwal ${formattedDate}`);

  fetch(`/get_schedule_by_date/${date}`)
    .then(response => response.json())
    .then(data => {
      populateScheduleTable(data, date);
      $('#scheduleTableContainer').show();
    })
    .catch(error => {
      console.error('Error fetching schedule data:', error);
    });
}

// Fungsi untuk memuat data jadwal
function loadScheduleData() {
  const year = $('#yearSelect').val();
  const month = $('#monthSelect').val();
  const date = `${year}-${(String(month).padStart(2, '0'))}`;

  showLoading();
  fetch(`/get_schedule/${date}`)
    .then(response => response.json())
    .then(data => {
      scheduleData = {};
      data.forEach(item => {
        const date = item.tanggal;
        if (!scheduleData[date]) {
          scheduleData[date] = [];
        }
        scheduleData[date].push(item);
      });
      updateCalendar();
      hideLoading();
    })
    .catch(error => {
      console.error('Error loading schedule data:', error);
      hideLoading();
    });
}

// Fungsi untuk memperbarui kalender dengan data jadwal
function updateCalendar(data) {
  for (const dateData of data) {
    const date = dateData.tanggal;
    if (dateData.count > 0) {
      const dayElement = $(`#day-${date}`);
      if (dayElement.length > 0) {
        dayElement.addClass('has-schedule');
        dayElement.css({
          'background-color': 'teal',
          'color': 'white',
          'font-weight': 'bold'
        });
        dayElement.append(`<span class="schedule-count">${dateData.count}</span>`);
      }
    }
  }
}


// Event listener for adding a row
document.getElementById('addRowButton').addEventListener('click', addScheduleRow);

// Event listener for saving schedule
document.getElementById('saveScheduleButton').addEventListener('click', saveSchedule);

// Load transport list when the modal is shown
$('#scheduleModal').on('shown.bs.modal', loadTransportList);

// Initial call to load the transport list when the page loads
document.addEventListener('DOMContentLoaded', loadTransportList);




function showLoading() {
  document.querySelector('.loading-screen').style.display = 'block';
}
function hideLoading() {
  document.querySelector('.loading-screen').style.display = 'none';
}

function openRouteModal() {
  $('#routeModal').modal('show');
}

function showModal() {
  $('#successModal').modal('show');
}

function hideModal() {
  $('#successModal').modal('hide');
}
