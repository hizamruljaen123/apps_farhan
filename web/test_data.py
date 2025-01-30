import numpy as np
import random
import osmnx as ox
import networkx as nx
import pandas as pd
import folium
import os
import plotly.graph_objects as go
from itertools import chain

# Load the Excel file
file_path = "combined_rice_supply_table.xlsx"
data = pd.read_excel(file_path)

# Coordinates dictionary provided
coordinate_cache = {
    "Sawang, kec. Peudada, kab. Bireuen": [5.2019429, 96.5543952],
    "Menasah Teungah, kec. Peudada, kab. Bireuen": [5.195865, 96.6079797],
    "Tebing Tinggi, Sumatera Utara": [3.3280636, 99.0717245],
    "Menasah Baroh": [5.194311, 96.594662],
    "Lhokseumawe": [5.1720557, 97.0252365],
    "Medan": [3.6424541, 98.5870941],
    "Matang": [5.1824847, 96.3672607],
    "Juli keude dua, kec. Juli, kab. Bireuen": [5.1709529, 96.6858125],
    "Takengon": [4.6309607, 96.8465678],
    "Kisaran": [2.9835893, 99.6257536],
    "Bireuen": [5.1988976, 96.6097626],
    "Tebing Tinggi": [3.3281518, 99.1129273]
}

# Create a dictionary of locations with their coordinates
locations = {loc: tuple(coords) for loc, coords in coordinate_cache.items()}

# Function to calculate Haversine distance
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0  # Earth radius in kilometers

    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c

# Calculate the distance matrix using Haversine formula
def calculate_distance_matrix(locations):
    num_locations = len(locations)
    keys = list(locations.keys())
    distance_matrix = np.zeros((num_locations, num_locations))
    for i in range(num_locations):
        for j in range(num_locations):
            if i != j:
                distance_matrix[i, j] = haversine(locations[keys[i]], locations[keys[j]])
    return distance_matrix

distance_matrix = calculate_distance_matrix(locations)

# Genetic Algorithm Parameters
POPULATION_SIZE = 200
MUTATION_RATE = 0.02
GENERATIONS = 100
TOURNAMENT_SIZE = 5
ELITISM_RATE = 0.1

# Function to initialize a population of routes
def initialize_population(population_size, num_locations, start_index):
    return [
        [start_index] + random.sample(list(range(num_locations))[1:], num_locations - 1)
        for _ in range(population_size)
    ]

# Optimized function to evaluate the fitness of each route in the population
def evaluate_population(population, distance_matrix):
    fitness_scores = []
    for route in population:
        total_distance = np.sum(distance_matrix[route[:-1], route[1:]]) + distance_matrix[route[-1], route[0]]
        if total_distance == 0:
            fitness_scores.append(float('inf'))  # Avoid division by zero
        else:
            fitness_scores.append(1 / total_distance)
    return fitness_scores

# Tournament selection
def tournament_selection(population, fitness_scores, tournament_size):
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(range(len(population)), tournament_size)
        selected.append(population[max(tournament, key=lambda i: fitness_scores[i])])
    return selected

# Improved crossover function (Ordered Crossover - OX)
def ordered_crossover(parent1, parent2):
    size = len(parent1)
    if size < 2:
        return parent1[:]  # No crossover possible
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end] = parent1[start:end]
    
    remaining = [item for item in parent2 if item not in child]
    for i in chain(range(start), range(end, size)):
        child[i] = remaining.pop(0)
    
    return child

# Improved mutation function (Swap Mutation)
def swap_mutation(route, mutation_rate):
    for i in range(1, len(route)):
        if random.random() < mutation_rate:
            j = random.randint(1, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route

# Main genetic algorithm function
def genetic_algorithm(distance_matrix, population_size, mutation_rate, generations, start_index, tournament_size, elitism_rate):
    num_locations = len(distance_matrix)
    population = initialize_population(population_size, num_locations, start_index)
    best_route = None
    best_distance = float('inf')
    
    for generation in range(generations):
        fitness_scores = evaluate_population(population, distance_matrix)
        
        # Elitism
        elitism_size = int(population_size * elitism_rate)
        elite = sorted(zip(population, fitness_scores), key=lambda x: x[1], reverse=True)[:elitism_size]
        new_population = [route for route, _ in elite]
        
        # Selection
        selected = tournament_selection(population, fitness_scores, tournament_size)
        
        # Crossover and Mutation
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child = ordered_crossover(parent1, parent2)
            child = swap_mutation(child, mutation_rate)
            new_population.append(child)
        
        population = new_population
        
        best_fitness = max(fitness_scores)
        current_best_route = population[fitness_scores.index(best_fitness)]
        current_best_distance = 1 / best_fitness if best_fitness != float('inf') else float('inf')
        
        if current_best_distance < best_distance:
            best_distance = current_best_distance
            best_route = current_best_route
        
        print(f"Generation {generation + 1}: Best Route Distance: {current_best_distance:.2f} km")
    
    return best_route, best_distance

# Function to create Plotly visualization and save as HTML
def create_plotly_plot(locations, best_route, distance_matrix, filename):
    keys = list(locations.keys())
    coords = [locations[keys[i]] for i in best_route]
    coords.append(locations[keys[best_route[0]]])  # close the loop
    latitudes, longitudes = zip(*coords)

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode='ISO-3',
        lat=latitudes,
        lon=longitudes,
        mode='lines+markers+text',
        text=[f"{i+1} {keys[best_route[i]]}" for i in range(len(best_route))],
        marker=dict(size=8)
    ))

    for i in range(len(best_route)):
        mid_lat = (latitudes[i] + latitudes[(i + 1) % len(best_route)]) / 2
        mid_lon = (longitudes[i] + longitudes[(i + 1) % len(best_route)]) / 2
        distance = distance_matrix[best_route[i]][best_route[(i + 1) % len(best_route)]]
        fig.add_trace(go.Scattergeo(
            locationmode='ISO-3',
            lat=[mid_lat],
            lon=[mid_lon],
            mode='text',
            text=[f"{distance:.2f} km"],
            textposition="top center"
        ))

    fig.update_layout(
        title=f"Shortest Route Distance: {sum(distance_matrix[best_route[i]][best_route[(i + 1) % len(best_route)]] for i in range(len(best_route))):.2f} km",
        geo=dict(
            projection_scale=5,
            center=dict(lat=np.mean(latitudes), lon=np.mean(longitudes)),
            showland=True,
            landcolor="rgb(243, 243, 243)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(217, 217, 217)"
        )
    )

    fig.write_html(filename)

# Improved function to get real-world route
def get_real_world_route(locations, best_route):
    keys = list(locations.keys())
    
    # Define the bounding box based on coordinates
    north = max([coord[0] for coord in locations.values()])
    south = min([coord[0] for coord in locations.values()])
    east = max([coord[1] for coord in locations.values()])
    west = min([coord[1] for coord in locations.values()])
    
    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    
    route = []
    
    for i in range(len(best_route)):
        start = best_route[i]
        end = best_route[(i + 1) % len(best_route)]
        start_node = ox.distance.nearest_nodes(G, locations[keys[start]][1], locations[keys[start]][0])
        end_node = ox.distance.nearest_nodes(G, locations[keys[end]][1], locations[keys[end]][0])
        try:
            route.extend(nx.shortest_path(G, start_node, end_node, weight='length'))
        except nx.NetworkXNoPath:
            print(f"No path found between {keys[start]} and {keys[end]}")
    
    return route, G

# Improved function to create Folium map
def create_folium_map(locations, best_route, route, G, filename):
    keys = list(locations.keys())
    center_lat = sum(loc[0] for loc in locations.values()) / len(locations)
    center_lon = sum(loc[1] for loc in locations.values()) / len(locations)

    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

    for i, key in enumerate(keys):
        folium.Marker(
            location=locations[key],
            popup=f"{key} ({best_route.index(i)+1})",
            icon=folium.Icon(color='green' if i == best_route[0] else 'blue')
        ).add_to(folium_map)

    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
    folium.PolyLine(locations=route_coords, color='red', weight=2.5, opacity=0.8).add_to(folium_map)

    os.makedirs('static/maps', exist_ok=True)
    folium_map.save(os.path.join('static/maps', filename))

# Main execution
if __name__ == "__main__":
    # Run Genetic Algorithm
    start_index = 0  # You may want to choose a specific starting point
    best_route, best_distance = genetic_algorithm(distance_matrix, POPULATION_SIZE, MUTATION_RATE, GENERATIONS, start_index, TOURNAMENT_SIZE, ELITISM_RATE)

    # Create Plotly plot and save it
    create_plotly_plot(locations, best_route, distance_matrix, 'optimized_route_plot.html')

    # Get real-world route using OSMnx
    real_world_route, G = get_real_world_route(locations, best_route)

    # Create Folium map and save it
    create_folium_map(locations, best_route, real_world_route, G, 'optimized_route_map.html')

    # Display results
    print("Optimized Route:")
    for i in best_route:
        location = list(locations.keys())[i]
        print(f"{data[data['Alamat Kilang Padi'] == location]['Pemilik Kilang Padi'].values[0]} - {location}")
    print(f"Total Distance: {best_distance:.2f} km")
