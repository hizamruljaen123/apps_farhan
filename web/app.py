from flask import Flask, jsonify, render_template, Response
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

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
