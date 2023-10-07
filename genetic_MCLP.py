import json
import time
import math
import random

def euclidean_distance(point1, point2):
    return math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)

def enrich_data_with_nearest(percentage):
    for point in points_data:
        distances = [
            {
                'id': other_point['id'],
                'distance': euclidean_distance(point, other_point)
            }
            for other_point in points_data if other_point['id'] != point['id']
        ]
        num_nearest = int(len(distances) * percentage / 100)
        nearest_points = sorted(distances, key=lambda x: x['distance'])[:num_nearest]
        point['nearest_points'] = [item['id'] for item in nearest_points]
    return points_data

def fitness(solution):
    all_points_within_radius = [pt['points_within_radius'] for pt in solution]
    unique_points_within_radius = set(item for sublist in all_points_within_radius for item in sublist)
    return len(unique_points_within_radius)

def load_data_from_json(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

def generate_population(n, k):
    return [random.sample(points_data, k) for _ in range(n)]

def binary_tournament_selection():
    selected_solutions = []

    while len(selected_solutions) < len(population):
        solution1, solution2 = random.sample(population, 2)
        fitness1 = fitness(solution1)
        fitness2 = fitness(solution2)
        if fitness1 > fitness2:
            selected_solutions.append(solution1)
        else:
            selected_solutions.append(solution2)

    return selected_solutions

def single_point_crossover(population, crossover_rate):
    offspring_population = []

    while len(offspring_population) < len(population):
        parent1, parent2 = random.sample(selected_population, 2)
        if random.random() < crossover_rate:
            crossover_point = random.randint(1, len(parent1) - 1)
            offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
            offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
            offspring_population.append(offspring1)
            if len(offspring_population) < len(population):
                offspring_population.append(offspring2)

    return offspring_population

def mutate_solution(solution, mutation_rate):
    mutated_solution = solution.copy()
    
    for i, point in enumerate(mutated_solution):
        if random.random() < mutation_rate:
            random_nearest = random.choice(point['nearest_points'])
            nearest_point_data = next(p for p in points_data if p['id'] == random_nearest)
            mutated_solution[i] = nearest_point_data
            
    return mutated_solution

def mutate_population(population, mutation_rate):
    return [mutate_solution(solution, mutation_rate) for solution in population]

def select_best_solutions(population1, population2):
    combined_population = population1 + population2
    sorted_population = sorted(combined_population, key=fitness, reverse=True)
    return sorted_population[:len(population1)]


json_file = "population_points.json"
data = load_data_from_json(json_file)
points_data = data["points_data"]
if __name__ == "__main__":
    percentage_nearest_neighbours = 5
    enriched_data = enrich_data_with_nearest(percentage_nearest_neighbours)
    initial_solutions = 20
    crossover_rate = 0.9
    mutation_rate_initial = 0.05
    mutation_rate_final = 0.8
    k = 5
    population = generate_population(initial_solutions, k)
    previous_best_fitness = fitness(max(population, key=fitness))
    stagnant_counter = 0
    loop_counter = 0
    change_mutation_counter = 0

    start_time = time.perf_counter()

    while True:
        selected_population = binary_tournament_selection()
        mutated_population = mutate_population(selected_population, mutation_rate_initial)
        new_temp_population = single_point_crossover(mutated_population, crossover_rate)
        population = select_best_solutions(new_temp_population, population)

        best_solution_fitness = fitness(max(population, key=fitness))

        if best_solution_fitness == previous_best_fitness:
            stagnant_counter += 1
        else:
            stagnant_counter = 0

        if change_mutation_counter == 0 and stagnant_counter == 50:
            stagnant_counter = 0
            mutation_rate = mutation_rate_final
            change_mutation_counter += 1

        if change_mutation_counter >= 1 and stagnant_counter == 100:
            break

        previous_best_fitness = best_solution_fitness
        loop_counter += 1

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    best_solution = max(population, key=fitness)

    output_data = {
        "result": [point["id"] for point in best_solution],
        "total_points_covered": float(fitness(best_solution))
    }
    with open("genetic_solution_MCLP.json", "w") as file:
        json.dump(output_data, file, indent=2)

    print("Best solution:", best_solution)
    print("Best fitness:", fitness(best_solution))
    print("Elapsed time:", elapsed_time)
    print("Total loops:", loop_counter)
