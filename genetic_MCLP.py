import json
import time
import math
import random

def euclidean_distance(point1, point2):
    """Compute the Euclidean distance between two points."""
    return math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)

def enrich_data_with_nearest(percentage):
    """Enriches each point data with the n% nearest points based on Euclidean distance."""
    
    # For each point, compute distance to every other point
    for point in points_data:
        distances = [
            {
                'id': other_point['id'],
                'distance': euclidean_distance(point, other_point)
            }
            for other_point in points_data if other_point['id'] != point['id']
        ]
        
        # Sort the distances and get the top n% of them
        num_nearest = int(len(distances) * percentage / 100)
        nearest_points = sorted(distances, key=lambda x: x['distance'])[:num_nearest]
        
        # Enrich the original point data
        point['nearest_points'] = [item['id'] for item in nearest_points]
    
    return points_data

def fitness(solution):
    """Compute the fitness of a solution based on the number of unique points_within_radius."""
    # Accumulate all points within radius for each point in the solution
    all_points_within_radius = [pt['points_within_radius'] for pt in solution]
    
    # Flatten the list and get unique points
    unique_points_within_radius = set(item for sublist in all_points_within_radius for item in sublist)
    
    return len(unique_points_within_radius)

def load_data_from_json(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

def generate_population(n, k):
    return [random.sample(points_data, k) for _ in range(n)]

def binary_tournament_selection():
    """Perform binary tournament selection on the population."""
    selected_solutions = []

    while len(selected_solutions) < len(population):
        # Randomly select two distinct solutions
        solution1, solution2 = random.sample(population, 2)

        # Calculate their fitness values
        fitness1 = fitness(solution1)
        fitness2 = fitness(solution2)

        # Append the solution with the higher fitness to the selected_solutions list
        if fitness1 > fitness2:
            selected_solutions.append(solution1)
        else:
            selected_solutions.append(solution2)

    return selected_solutions

def single_point_crossover(population, crossover_rate):
    """Perform single-point crossover on the selected_population."""
    offspring_population = []

    while len(offspring_population) < len(population):
        # Select two distinct parents
        parent1, parent2 = random.sample(selected_population, 2)

        # Decide if the crossover will be successful
        if random.random() < crossover_rate:
            # Choose a random crossover point
            crossover_point = random.randint(1, len(parent1) - 1)  # Avoid having the crossover point at the very start or end

            # Create the offspring by swapping genes beyond the crossover point
            offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
            offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

            # Append offspring to the new population
            offspring_population.append(offspring1)
            # Check if there's still room to add more solutions before appending the second offspring
            if len(offspring_population) < len(population):
                offspring_population.append(offspring2)

    return offspring_population

def mutate_solution(solution, mutation_rate):
    """Mutate a single solution based on the mutation rate."""
    mutated_solution = solution.copy()  # Create a copy to avoid changing the original solution
    
    for i, point in enumerate(mutated_solution):
        if random.random() < mutation_rate:
            # Choose a random nearest neighbor to replace the current point
            random_nearest = random.choice(point['nearest_points'])
            # Find the actual point data for this neighbor
            nearest_point_data = next(p for p in points_data if p['id'] == random_nearest)
            mutated_solution[i] = nearest_point_data
            
    return mutated_solution

def mutate_population(population, mutation_rate):
    """Apply mutation on the entire population."""
    return [mutate_solution(solution, mutation_rate) for solution in population]

def select_best_solutions(population1, population2):
    """Select the best solutions from two populations based on their fitness."""
    # Combine both populations
    combined_population = population1 + population2
    
    # Sort combined solutions based on their fitness in descending order
    sorted_population = sorted(combined_population, key=fitness, reverse=True)
    
    # Only retain the top solutions
    return sorted_population[:len(population1)]


json_file = "population_points.json"
data = load_data_from_json(json_file)
points_data = data["points_data"]
if __name__ == "__main__":
    # Using the function to enrich data
    percentage_nearest_neighbours = 5  # As an example, corresponds to mathematical N in master's thesis
    enriched_data = enrich_data_with_nearest(percentage_nearest_neighbours)
    initial_solutions = 20  # Number of solutions in the initial population
    crossover_rate = 0.9
    mutation_rate_initial = 0.05  # 5% mutation rate, corresponds to \mu_m in master's thesis
    mutation_rate_final=0.8
    k = 5   # Number of points in each solution vector, corresponds to p in master's thesis
    
    population=generate_population(initial_solutions, k)

    # Initialize loop variables
    previous_best_fitness = fitness(max(population, key=fitness))
    stagnant_counter = 0
    loop_counter = 0
    change_mutation_counter = 0  # Counter for tracking mutation rate change

    start_time = time.perf_counter()

    while True:  # Main loop
        # Existing evolutionary operations
        selected_population = binary_tournament_selection()
        mutated_population = mutate_population(selected_population, mutation_rate_initial)
        new_temp_population = single_point_crossover(mutated_population,crossover_rate)
        population = select_best_solutions(new_temp_population, population)

        # Check best solution's fitness in the current population
        best_solution_fitness = fitness(max(population, key=fitness))

        # Check if fitness hasn't changed
        if best_solution_fitness == previous_best_fitness:
            stagnant_counter += 1
        else:
            stagnant_counter = 0  # Reset counter if fitness has changed

        # Condition to change mutation rate after 50 stagnant iterations
        if change_mutation_counter == 0 and stagnant_counter == 50:
            stagnant_counter=0
            mutation_rate = mutation_rate_final
            change_mutation_counter += 1  # Increment this counter as mutation rate has been changed

        # Conditions to break the loop
        if change_mutation_counter >= 1 and stagnant_counter == 100:
            break

        # Store the best fitness of this iteration to compare in the next iteration
        previous_best_fitness = best_solution_fitness

        # Increment the loop counter
        loop_counter += 1

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # Extract the best solution from the final population
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