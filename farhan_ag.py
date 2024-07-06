import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import osmnx as ox
from deap import base, creator, tools, algorithms
from matplotlib.animation import FuncAnimation
import pickle
import os
import time  # Import modul time untuk mengatur jeda

# Function to download or load the street network graph for Jakarta
def load_or_download_graph(place_name):
    filename = f"{place_name}_graph.graphml"
    if os.path.exists(filename):
        G = ox.load_graphml(filename)
    else:
        G = ox.graph_from_place(place_name, network_type='drive')
        ox.save_graphml(G, filename)
    return G

# Define the place name
place_name = "Jakarta, Indonesia"
G = load_or_download_graph(place_name)

# Plot graf jaringan dengan warna jalan abu-abu
fig, ax = plt.subplots(figsize=(12, 12))
ox.plot_graph(G, ax=ax, show=False, close=False, edge_color='gray')

# Tentukan beberapa titik di sekitar Jakarta
locations = {
    "Plaza Indonesia": (-6.1931, 106.8217),
    "Grand Indonesia": (-6.1964, 106.8233),
    "Ragunan Zoo": (-6.3116, 106.8205),
    "Gelora Bung Karno": (-6.2183, 106.8018),
    "Gandaria City Mall": (-6.2443, 106.7842),
    "Jakarta International Expo": (-6.1406, 106.8448),
    "Pondok Indah Mall": (-6.2636, 106.7826)
}

# Plot titik-titik lokasi dengan warna berbeda
for name, coord in locations.items():
    x, y = coord[1], coord[0]  # Use longitude and latitude directly
    ax.scatter(x, y, label=name, s=100)


plt.legend()
plt.title('Graf Jaringan Jakarta dengan Lokasi Penting')
plt.show()

# Tambahkan jeda 5 detik sebelum melanjutkan
print("Menunggu 5 detik sebelum melanjutkan proses...")
time.sleep(5)

# # Fungsi untuk mendapatkan node terdekat
# def get_nearest_node(graph, point):
#     try:
#         node = ox.distance.nearest_nodes(graph, point[1], point[0])
#         return node
#     except Exception as e:
#         print(f"Node tidak ditemukan untuk koordinat: {point}, Error: {e}")
#         return None

# # Dapatkan node terdekat untuk setiap lokasi
# nodes = {}
# for name, coord in locations.items():
#     node = get_nearest_node(G, coord)
#     if node:
#         nodes[name] = node
#     else:
#         print(f"Tidak dapat menemukan node untuk {name}")

# points = list(nodes.values())
# location_names = list(nodes.keys())

# if len(points) < 2:
#     print("Tidak cukup node yang ditemukan untuk melanjutkan.")
#     exit()

# # Verifikasi rute antara setiap pasangan titik
# print("Memverifikasi rute antara titik-titik...")
# distance_matrix = np.zeros((len(points), len(points)))
# for i, p1 in enumerate(points):
#     for j, p2 in enumerate(points):
#         try:
#             distance_matrix[i, j] = nx.shortest_path_length(G, p1, p2, weight='length')
#         except nx.NetworkXNoPath:
#             print(f"Tidak ditemukan rute antara {location_names[i]} dan {location_names[j]}")
#             distance_matrix[i, j] = np.inf

# print("Matriks jarak telah dihitung.")

# # Inisialisasi DEAP
# creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
# creator.create("Individual", list, fitness=creator.FitnessMin)

# print("Inisialisasi DEAP selesai.")

# toolbox = base.Toolbox()
# toolbox.register("indices", random.sample, range(len(points)), len(points))
# toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
# toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# def evaluate(individual):
#     distance = 0
#     for i in range(len(individual) - 1):
#         if distance_matrix[individual[i]][individual[i+1]] == np.inf:
#             return np.inf,  # Tidak ada rute yang valid
#         distance += distance_matrix[individual[i]][individual[i+1]]
#     if distance_matrix[individual[-1]][individual[0]] == np.inf:
#         return np.inf,  # Tidak ada rute yang valid
#     distance += distance_matrix[individual[-1]][individual[0]]  # Kembali ke titik awal
#     return distance,

# toolbox.register("mate", tools.cxOrdered)
# toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
# toolbox.register("select", tools.selTournament, tournsize=3)
# toolbox.register("evaluate", evaluate)

# # Parameter GA
# population_size = 100
# crossover_prob = 0.8
# mutation_prob = 0.2
# num_generations = 100

# # Setup plot for animation
# fig, ax = plt.subplots(figsize=(12, 12))

# def update_graph(frame):
#     print(f"Iterasi {frame}...")
#     ax.clear()
#     # Algoritma evolusi
#     offspring = algorithms.varAnd(population, toolbox, cxpb=crossover_prob, mutpb=mutation_prob)
#     fits = toolbox.map(toolbox.evaluate, offspring)
#     for fit, ind in zip(fits, offspring):
#         ind.fitness.values = fit
#         print(f"Evaluasi individu: {ind}, Fitness: {fit}")
#     population[:] = toolbox.select(offspring, k=len(population))
    
#     # Individu terbaik
#     best_individual = tools.selBest(population, k=1)[0]
#     best_route = [points[i] for i in best_individual]
    
#     # Plot graph
#     ax.set_title(f"Iteration {frame}")
#     ox.plot_graph(G, ax=ax, show=False, close=False, edge_color='gray')
#     for name, node in nodes.items():
#         x, y = G.nodes[node]['x'], G.nodes[node]['y']
#         ax.plot(x, y, 'o', color='red', markersize=10)
#         ax.text(x, y, name, fontsize=12, ha='right')
    
#     route_edges = []
#     for i in range(len(best_individual) - 1):
#         try:
#             route_edges.extend(list(zip(nx.shortest_path(G, best_route[i], best_route[i+1], weight='length')[:-1], 
#                                         nx.shortest_path(G, best_route[i], best_route[i+1], weight='length')[1:])))
#         except nx.NetworkXNoPath:
#             print(f"Tidak ditemukan rute antara node {best_route[i]} dan {best_route[i+1]}")
#             continue
#     try:
#         route_edges.extend(list(zip(nx.shortest_path(G, best_route[-1], best_route[0], weight='length')[:-1], 
#                                     nx.shortest_path(G, best_route[-1], best_route[0], weight='length')[1:])))
#     except nx.NetworkXNoPath:
#         print(f"Tidak ditemukan rute antara node {best_route[-1]} dan {best_route[0]}")
    
#     # Menggambar rute dengan warna biru
#     nx.draw_networkx_edges(G, pos=nx.get_node_attributes(G, 'xy'), edgelist=route_edges, edge_color='blue', width=2, ax=ax)
#     nx.draw_networkx_nodes(G, pos=nx.get_node_attributes(G, 'xy'), nodelist=best_route, node_color='b', ax=ax)
#     print(f"Best individual: {best_individual}, Best route: {best_route}")

# print("Memulai animasi pencarian rute...")
# ani2 = FuncAnimation(fig, update_graph, frames=num_generations, repeat=False)
# plt.show()

# print("Proses selesai.")
