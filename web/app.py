from flask import Flask, jsonify, render_template, Response, render_template, request
import numpy as np
import random
from geopy.distance import great_circle
import folium
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
import os
import mysql.connector
from datetime import datetime


app = Flask(__name__)

# Konfigurasi koneksi MySQL
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'ag_data'
}
# Define the coordinates for 10 locations in Jakarta (latitude, longitude)
locations = {
    "Monas": (-6.1753924, 106.8271528),
    "Kota Tua": (-6.1352, 106.8133),
    "Ancol": (-6.1235, 106.8307),
    "Taman Mini": (-6.3025, 106.8954),
    "Ragunan Zoo": (-6.3113, 106.8201),
    "Senayan": (-6.2251, 106.7986),
    "Kemang": (-6.2607, 106.8123),
    "Pluit": (-6.1256, 106.7909),
    "Pondok Indah": (-6.2766, 106.7886),
    "Cibubur": (-6.3674, 106.9012)
}
# Establish database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)
# Calculate the distance matrix using Haversine formula
def calculate_distance_matrix(locations):
    num_locations = len(locations)
    distance_matrix = np.zeros((num_locations, num_locations))

    keys = list(locations.keys())
    for i in range(num_locations):
        for j in range(num_locations):
            if i != j:
                distance_matrix[i][j] = great_circle(locations[keys[i]], locations[keys[j]]).kilometers

    return distance_matrix

distance_matrix = calculate_distance_matrix(locations)

# Genetic Algorithm Parameters
POPULATION_SIZE = 100
MUTATION_RATE = 0.1
GENERATIONS = 50

# Function to initialize a population of routes
def initialize_population(population_size, num_locations, start_index):
    population = []
    for _ in range(population_size):
        route = list(range(num_locations))
        route.remove(start_index)
        random.shuffle(route)
        route.insert(0, start_index)  # Ensure the start point is always the first
        population.append(route)
    return population

# Function to evaluate the fitness of each route in the population
def evaluate_population(population, distance_matrix):
    fitness_scores = []
    for route in population:
        distance = 0
        for i in range(len(route) - 1):
            distance += distance_matrix[route[i]][route[i+1]]
        distance += distance_matrix[route[-1]][route[0]]  # Return to the starting point
        fitness_scores.append(1 / distance)  # Inverse of total distance as fitness
    return fitness_scores

# Function to perform selection based on fitness scores (roulette wheel selection)
def selection(population, fitness_scores):
    return random.choices(population, weights=fitness_scores, k=len(population))

# Function to perform crossover between two routes
def crossover(route1, route2):
    start_index = route1[0]  # Ensure the start point remains fixed
    start_index_cross = random.randint(1, len(route1) - 2)
    end_index_cross = random.randint(start_index_cross, len(route1) - 1)
    child_p1 = route1[start_index_cross:end_index_cross]
    child = [start_index] + [item for item in route2 if item not in child_p1]
    return child[:start_index_cross] + child_p1 + child[start_index_cross:]

# Function to perform mutation on a route
def mutate(route, mutation_rate):
    for i in range(1, len(route)):  # Start from 1 to keep the start point fixed
        if random.random() < mutation_rate:
            j = random.randint(1, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route

# Function to run the genetic algorithm and yield the best route for each generation
def genetic_algorithm(distance_matrix, population_size, mutation_rate, generations, start_index):
    num_locations = len(distance_matrix)
    population = initialize_population(population_size, num_locations, start_index)
    
    for generation in range(generations):
        fitness_scores = evaluate_population(population, distance_matrix)
        new_population = []

        # Elitism: Keep the best route from the current population
        best_route_index = np.argmax(fitness_scores)
        new_population.append(population[best_route_index])
        
        print(f"Generation {generation + 1}: Best Route Distance: {1 / fitness_scores[best_route_index]:.2f} km")

        while len(new_population) < population_size:
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            new_population.append(child)

        population = new_population

        # Yield the best route of the current generation
        fitness_scores = evaluate_population(population, distance_matrix)
        best_route_index = np.argmax(fitness_scores)
        yield population[best_route_index], 1 / fitness_scores[best_route_index]

# Function to create Matplotlib visualization and save as PNG
def create_matplotlib_plot(locations, best_route, distance_matrix, filename):
    keys = list(locations.keys())
    latitudes = [locations[keys[i]][0] for i in best_route] + [locations[keys[best_route[0]]][0]]
    longitudes = [locations[keys[i]][1] for i in best_route] + [locations[keys[best_route[0]]][1]]

    fig, ax = plt.subplots(figsize=(25, 10))
    plt.plot(longitudes, latitudes, marker='o')
    offset_x = 0
    offset_y = 10
    visited = set()
    for i in range(len(best_route) - 1):  # Adjusted to iterate correctly until the second-to-last element
        label = f"{i+1} {keys[best_route[i]]}"
        if i == 0:
            plt.annotate(f"{label} (Start Point)", (longitudes[i], latitudes[i]), textcoords="offset points", xytext=(offset_x,offset_y), ha='center')
        else:
            if keys[best_route[i]] in visited:
                continue
            plt.annotate(label, (longitudes[i], latitudes[i]), textcoords="offset points", xytext=(offset_x,offset_y), ha='center')
        visited.add(keys[best_route[i]])

        # Add distance annotation along the line with white background and black text
        mid_x = (longitudes[i] + longitudes[i + 1]) / 2
        mid_y = (latitudes[i] + latitudes[i + 1]) / 2
        distance_between_points = distance_matrix[best_route[i]][best_route[i + 1]]
        plt.text(mid_x, mid_y, f"{distance_between_points:.2f} km", fontsize=9, ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2'))

    # Distance from last point to first point
    mid_x = (longitudes[-2] + longitudes[-1]) / 2
    mid_y = (latitudes[-2] + latitudes[-1]) / 2
    distance_between_points = distance_matrix[best_route[-1]][best_route[0]]
    plt.text(mid_x, mid_y, f"{distance_between_points:.2f} km", fontsize=9, ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2'))

    plt.title(f"Shortest Route Distance: {1 / evaluate_population([best_route], distance_matrix)[0]:.2f} km")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    # Save the plot to a file
    if not os.path.exists('static/plot'):
        os.makedirs('static/plot')
    filepath = os.path.join('static/plot', filename)
    plt.savefig(filepath, format='png')
    plt.close()

def get_real_world_route(locations, best_route):
    G = ox.graph_from_place('Jakarta, Indonesia', network_type='drive')
    keys = list(locations.keys())
    route = []
    
    for i in range(len(best_route) - 1):
        start_node = ox.distance.nearest_nodes(G, locations[keys[best_route[i]]][1], locations[keys[best_route[i]]][0])
        end_node = ox.distance.nearest_nodes(G, locations[keys[best_route[i + 1]]][1], locations[keys[best_route[i + 1]]][0])
        route.extend(nx.shortest_path(G, start_node, end_node, weight='length'))
    
    return route, G


# API
# Function to get the shortest route data
@app.route('/shortest_route')
def get_shortest_route():
    global distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS
    start_index = 0  # Modify this to choose a different starting point
    ga_generator = genetic_algorithm(distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS, start_index)
    best_route, best_distance = next(ga_generator)
    
    route_data = {
        'route': best_route,
        'distance': best_distance,
        'locations': locations
    }
    
    return jsonify(route_data)

# Function to get the real-world route data
@app.route('/real_world_route')
def real_world_route():
    global distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS
    start_index = 0  # Modify this to choose a different starting point
    ga_generator = genetic_algorithm(distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS, start_index)
    best_route, best_distance = next(ga_generator)
    
    real_world_route, G = get_real_world_route(locations, best_route)
    
    real_world_route_data = {
        'route': real_world_route,
        'distance': best_distance,
        'locations': locations
    }
    
    return jsonify(real_world_route_data)

@app.route('/plot')
def get_plot():
    global locations, distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS
    start_index = 0  # Modify this to choose a different starting point
    ga_generator = genetic_algorithm(distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS, start_index)
    best_route, _ = next(ga_generator)

    # Create plot and save it with a fixed filename
    create_matplotlib_plot(locations, best_route, distance_matrix, 'plot.png')

    return jsonify({'message': 'Plot generated and saved as plot.png'})

@app.route('/getroutesfromlist', methods=['POST'])
def get_routes_from_list():
    data = request.json
    input_locations = data['locations']

    # Buat dictionary baru dari input lokasi
    input_dict = {loc['name']: (loc['lat'], loc['lon']) for loc in input_locations}

    # Hitung distance matrix baru dari input lokasi
    distance_matrix = calculate_distance_matrix(input_dict)
    
    # Run Genetic Algorithm
    start_index = 0  # Memulai dari lokasi pertama dalam input lokasi
    ga_generator = genetic_algorithm(distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS, start_index)
    best_route, best_distance = next(ga_generator)

    # Konversi best_route ke nama lokasi
    best_route_names = [list(input_dict.keys())[i] for i in best_route]

    # Dapatkan real world route menggunakan OSMnx
    real_world_route, G = get_real_world_route(input_dict, best_route)

    route_data = {
        'route': real_world_route,
        'distance': best_distance,
        'locations': input_dict,
        'route_names': best_route_names
    }

    return jsonify(route_data)

# Route untuk mendapatkan daftar rute
@app.route('/get_routes_list', methods=['GET'])
def get_routes_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT route_id as id, route_name as name FROM routes")
    routes = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({'routes': routes})

# Route untuk mendapatkan detail rute berdasarkan ID rute
@app.route('/get_route_details/<int:route_id>', methods=['GET'])
def get_route_details(route_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, lat, lon FROM route_points WHERE route_id = %s ORDER BY sequence", (route_id,))
    routes = [{'name': row[0], 'lat': row[1], 'lon': row[2]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({'routes': routes})

# Route untuk menyimpan rute baru
@app.route('/save_routes', methods=['POST'])
def save_routes():
    data = request.json
    route_name = data.get('route_name')
    distance = data.get('distance')
    routes = data.get('routes')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert rute ke tabel routes
    cursor.execute("INSERT INTO routes (route_name, total_distance) VALUES (%s, %s)", (route_name, distance))
    route_id = cursor.lastrowid

    # Insert detail rute ke tabel route_points
    for route in routes:
        cursor.execute("INSERT INTO route_points (route_id, name, lat, lon, sequence) VALUES (%s, %s, %s, %s, %s)",
                       (route_id, route['name'], route['lat'], route['lon'], route['sequence']))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# Route untuk mendapatkan daftar angkutan
@app.route('/angkutan_list', methods=['GET'])
def angkutan_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM transport')
    transport_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(transport_data)

# Route untuk menyimpan data angkutan
@app.route('/save_transport', methods=['POST'])
def save_transport():
    transport_data = request.json['transport']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hapus data yang ada
    cursor.execute('DELETE FROM transport')

    # Insert data angkutan baru
    for transport in transport_data:
        cursor.execute('''
            INSERT INTO transport (nama_kendaraan, plat_nomor, kondisi, nama_supir, nomor_telepon, status_keberangkatan)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (transport['nama_kendaraan'], transport['plat_nomor'], transport['kondisi'], transport['nama_supir'], transport['nomor_telepon'], transport['status_keberangkatan']))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})

# Route untuk mendapatkan data jadwal
@app.route('/get_schedule', methods=['GET'])
def get_schedule():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        jadwal.id, 
        transport.nama_kendaraan, 
        jadwal.barang, 
        jadwal.jumlah_ton, 
        routes.route_name AS nama_rute 
    FROM jadwal 
    JOIN transport ON jadwal.id_angkutan = transport.id 
    JOIN routes ON jadwal.id_rute = routes.route_id 
    WHERE jadwal.tanggal = %s
    """
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    cursor.execute(query, (date,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({date: result})

@app.route('/get_schedule/<year_month>', methods=['GET'])
def get_scheduleDate(year_month):
    year, month = year_month.split('-')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        jadwal.id, 
        transport.nama_kendaraan, 
        jadwal.barang, 
        jadwal.jumlah_ton, 
        routes.route_name AS nama_rute 
    FROM jadwal 
    JOIN transport ON jadwal.id_angkutan = transport.id 
    JOIN routes ON jadwal.id_rute = routes.route_id 
    WHERE YEAR(jadwal.tanggal) = %s AND MONTH(jadwal.tanggal) = %s
    """
    cursor.execute(query, (year, month))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/get_schedule_by_date/<date>', methods=['GET'])
def get_schedule_by_date(date):
    # date parameter will be in the format 'YYYY-MM-DD'
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        jadwal.id, 
        DATE_FORMAT(jadwal.tanggal, '%%Y-%%m-%%d') as tanggal,
        transport.nama_kendaraan, 
        jadwal.barang, 
        jadwal.jumlah_ton, 
        routes.route_name AS nama_rute 
    FROM jadwal 
    JOIN transport ON jadwal.id_angkutan = transport.id 
    JOIN routes ON jadwal.id_rute = routes.route_id 
    WHERE jadwal.tanggal = %s
    """
    cursor.execute(query, (date,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    data = request.get_json()
    schedule = data.get('schedule', [])

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for item in schedule:
            id_angkutan = item.get('id_angkutan')
            id_rute = item.get('id_rute')
            barang = item.get('barang')
            jumlah_ton = item.get('jumlah_ton')
            date_str = item.get('date')

            # Convert date from 'YYYY-MM-DD' string to date object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Logging for debugging
            print(f"Inserting schedule: id_angkutan={id_angkutan}, id_rute={id_rute}, barang={barang}, jumlah_ton={jumlah_ton}, tanggal={date_obj}")

            query = """
                INSERT INTO jadwal (tanggal, id_angkutan, id_rute, barang, jumlah_ton)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (date_obj, id_angkutan, id_rute, barang, jumlah_ton))

        conn.commit()
        response = {'success': True}
    except mysql.connector.Error as err:
        conn.rollback()
        response = {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

    return jsonify(response)



# Route untuk mendapatkan jumlah jadwal berdasarkan bulan dan tahun
@app.route('/get_schedule_count/<year_month>', methods=['GET'])
def get_schedule_count(year_month):
    year, month = year_month.split('-')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        DATE_FORMAT(tanggal, '%Y-%m-%d') as date,
        COUNT(*) as count
    FROM jadwal 
    WHERE YEAR(tanggal) = %s AND MONTH(tanggal) = %s
    GROUP BY tanggal
    """
    cursor.execute(query, (year, month))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)




@app.route('/get_route_list', methods=['GET'])
def get_route_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT route_id AS id, route_name as name FROM routes')
    route_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(route_data)
# Front End


@app.route('/')
def routes():
    return render_template('routes.html')
if __name__ == '__main__':
    app.run(debug=True)


