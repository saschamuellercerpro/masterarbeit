import json
import random
import math
import time

def load_data_from_json(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

def create_initial_feasible_solution_as_chromosome():
    # Create a list of elements to cover (in this case, point IDs)
    elements_to_cover = [point['id'] for point in points_data]

    # Create a list of sets that cover the elements (points_within_radius)
    sets = [set(point['points_within_radius']) for point in points_data]

    # Initialize an empty list to store the IDs of the selected sets
    selected_set_ids = []

    # Initialize a dictionary to keep track of the coverage count for each element
    coverage_count = {element: 0 for element in elements_to_cover}

    # Iterate through elements to cover
    for element in elements_to_cover:
        # Find sets that cover the element
        covering_sets = [s for s in sets if element in s]

        if not covering_sets:
            print("No set covers element:", element)
            continue

        # Randomly select a set that covers the element
        selected_set = random.choice(covering_sets)

        # Add the ID of the selected set to the list
        selected_set_ids.append(sets.index(selected_set))

        # Update coverage count for each element covered in the selected set
        for covered_element in selected_set:
            coverage_count[covered_element] += 1

    # Clone the selected_set_ids
    clone_selected_set_ids = selected_set_ids.copy()

    # Process the clone until it's empty
    while clone_selected_set_ids:
        # Randomly select an ID from the clone and remove it from the clone
        selected_set_id = random.choice(clone_selected_set_ids)
        clone_selected_set_ids.remove(selected_set_id)

        # Get the corresponding set using the ID
        selected_set = sets[selected_set_id]

        # Check coverage count for each element in the selected set
        remove_set_from_selected = True
        for covered_element in selected_set:
            if coverage_count[covered_element] < 2:
                remove_set_from_selected = False
                break

        # If coverage count condition is met, remove the set ID from selected_set_ids
        if remove_set_from_selected:
            for covered_element in selected_set:
                coverage_count[covered_element] -= 1
            selected_set_ids.remove(selected_set_id)

    # Create an array of 0s and 1s to represent selected sets
    num_sets = len(sets)
    selected_sets_array = [1 if i in selected_set_ids else 0 for i in range(num_sets)]

    # Commented out the check for selected sets covering all elements
    # if set(elements_to_cover) == set(element for set_id in selected_set_ids for element in sets[set_id]):
    #     print("Solution covers all elements.")
    # else:
    #     print("Solution does not cover all elements.")

    return selected_sets_array, coverage_count

def generate_initial_population(n):
    population = []
    for _ in range(n):
        solution, _ = create_initial_feasible_solution_as_chromosome()
        population.append(solution)
    return population

def fitness_function(solution):
    # Initialize the total weight to 0
    total_weight = 0

    # Iterate through the selected sets in the solution
    for i, selected in enumerate(solution):
        # If the set is selected (selected == 1), add its weight to the total
        if selected == 1:
            total_weight += points_data[i]['weight']

    return total_weight

def binary_tournament_selection(population):
    # Initialize the selected solutions
    selected_solutions = []

    # Perform two tournaments to select two solutions
    for _ in range(2):
        # Randomly select two solutions from the population
        tournament_pool = random.sample(range(len(population)), 2)
        solution1, solution2 = tournament_pool

        # Calculate the fitness of the two solutions using the fitness_function
        fitness1 = fitness_function(population[solution1])
        fitness2 = fitness_function(population[solution2])

        # Select the solution with the lower fitness
        if fitness1 < fitness2:
            selected_solutions.append(population[solution1])
        else:
            selected_solutions.append(population[solution2])

    return selected_solutions

def form_new_solution_by_crossover(solution1, solution2):
    # Initialize the child solution
    child_solution = []

    # Calculate the fitness of the two solutions
    fitness1 = fitness_function(solution1)
    fitness2 = fitness_function(solution2)
    probability = fitness2 / (fitness1 + fitness2)

    # Iterate through the genes of the solutions
    for i in range(len(solution1)):
        if solution1[i] == solution2[i]:
            # If genes are the same, inherit from either solution1 or solution2
                child_solution.append(solution1[i])
        else:
            # Genes are different, determine inheritance based on fitness ratio
            if random.random() < probability:
                child_solution.append(solution1[i])
            else:
                child_solution.append(solution2[i])

    return child_solution

def number_of_bits_mutated(mf, mc, mg, t):
    exponent = -4 * mg * (t - mc) / mf
    return mf / (1 + math.exp(exponent))

def s_elite(num_elite_sets=5):
    # Create a dictionary to store the top num_elite_sets sets for each element
    elite_sets = {}

    # Iterate through elements to cover
    for point in points_data:
        element_id = point['id']
        sets_that_cover_point = []

        # Find sets that cover the current point
        for other_point in points_data:
            if element_id in other_point['points_within_radius']:
                sets_that_cover_point.append(other_point['id'])

        # Sort the sets by weight in ascending order
        sorted_sets = sorted(sets_that_cover_point, key=lambda set_id: points_data[set_id]['weight'])

        # Select the top num_elite_sets sets
        elite_sets[element_id] = sorted_sets[:num_elite_sets]

    # Create a union of elite sets
    union_of_elite_sets = set()
    for sets in elite_sets.values():
        union_of_elite_sets.update(sets)

    return union_of_elite_sets

def mutation(child_solution, elite_sets, mf, mc, mg, t):
    # Calculate the number of bits to mutate using number_of_bits_mutated function
    num_bits_to_mutate = int(number_of_bits_mutated(mf, mc, mg, t))
    # Randomly select num_bits_to_mutate sets from elite_sets
    sets_to_mutate = random.sample(sorted(elite_sets), num_bits_to_mutate)
    # Iterate through the selected sets and flip their bit in the child solution
    for set_id in sets_to_mutate:
        child_solution[set_id] = 1 - child_solution[set_id]

    return child_solution

def heuristic_feasibility_operator(child_solution):
    # Create a copy of the child_solution as the initial solution
    solution = child_solution.copy()

    # Create a set to store the elements covered by the selected sets
    covered_elements = set()

    # Create a dictionary to store the weight-to-uncovered-ratio for each set
    weight_to_ratio = {}

    # Calculate the elements not covered by the selected sets
    uncovered_elements = set()

    # Iterate through the child solution and update the covered elements
    for i, selected in enumerate(child_solution):
        if selected:
            # Get the elements covered by the selected set
            covered_elements.update(points_data[i]['points_within_radius'])

    # Create a set of all elements to cover
    all_elements = set(point['id'] for point in points_data)

    # Calculate the elements not covered by the selected sets
    uncovered_elements = all_elements - covered_elements

    # Calculate the weight-to-uncovered-elements ratio for each set. At this point I am not sure (as it is also not specified in the paper by Beasley and Chu, 1996,
    # whether the weight-to-uncovered-elements ratio is to be recalculated once sets are added to the solution and the bottom part of the formula changes.
    # Since it has not been specified and it would turn the code more complex, I am going to assume that the weight-to-uncovered-elements ratio is not to be recalculated. 
    for point in points_data:
        set_id = point['id']
        set_weight = point['weight']
        covered_elements = point['points_within_radius']

        # Calculate the number of uncovered elements it would cover
        num_uncovered_elements_covered = len(set(covered_elements).intersection(uncovered_elements))

        # Calculate the weight-to-uncovered-elements ratio
        if num_uncovered_elements_covered > 0:
            ratio = set_weight / num_uncovered_elements_covered
        else:
            ratio = float('inf')  # Assign infinity if no uncovered elements are covered

        weight_to_ratio[set_id] = ratio

    # Sort sets by weight-to-ratio in ascending order
    sorted_sets = sorted(points_data, key=lambda point: weight_to_ratio[point['id']])

    # Iterate through sorted sets and add them to the solution until all elements are covered
    for point in sorted_sets:
        set_id = point['id']
        covered_elements = set(point['points_within_radius'])

        # Check if any uncovered elements are covered by this set
        common_elements = covered_elements.intersection(uncovered_elements)

        if common_elements:
            solution[set_id] = 1
            uncovered_elements -= common_elements

        # Break if all elements are covered
        if not uncovered_elements:
            break

   
    # Create a dictionary to store the count of each element covered by selected sets
    element_coverage_count = {element['id']: 0 for element in points_data}

    # Calculate how many times each element is covered by selected sets
    for i, selected in enumerate(solution):
        if selected:
            # Get the elements covered by the selected set
            covered_elements = points_data[i]['points_within_radius']

            # Update coverage count for each element covered in the selected set
            for covered_element in covered_elements:
                element_coverage_count[covered_element] += 1

    # Sort sets by weight-to-ratio in descending order
    sorted_sets = sorted(points_data, key=lambda point: -weight_to_ratio[point['id']])

    # Iterate through sorted sets and remove sets based on element coverage count
    for point in sorted_sets:
        set_id = point['id']
        covered_elements = set(point['points_within_radius'])

        # Check if all elements covered by this set have X >= 2
        if all(element_coverage_count[element] >= 2 for element in covered_elements):
            # Remove the set from the solution and decrease X by 1 for each covered element
            solution[set_id] = 0
            for covered_element in covered_elements:
                element_coverage_count[covered_element] -= 1

    return solution

def is_solution_in_population(solution, population):
    # Convert the solution list to a tuple for comparison
    solution_tuple = tuple(solution)

    # Check if the solution tuple is in the population
    return solution_tuple in population

def replace_solution_above_average_fitness(population, child_solution):
    # Calculate fitness for all solutions in the population
    fitness_values = [fitness_function(solution) for solution in population]

    # Calculate the average fitness of the population
    average_fitness = sum(fitness_values) / len(fitness_values)

    # Find indices of solutions with above-average fitness
    above_average_indices = [i for i, fitness in enumerate(fitness_values) if fitness > average_fitness]

    if above_average_indices:
        # Randomly select a solution with above-average fitness to replace
        solution_to_replace_index = random.choice(above_average_indices)

        # Replace the selected solution with the child_solution
        population[solution_to_replace_index] = child_solution

    return population

def convert_to_solution_format(binary_solution):
    # Initialize lists to store selected sets and their weights
    selected_sets = []
    selected_weights = []

    # Iterate through the binary solution and extract selected sets and their weights
    for i, selected in enumerate(binary_solution):
        if selected:
            selected_sets.append(i)
            selected_weights.append(points_data[i]['weight'])

    # Calculate the total weight of selected sets
    total_weight = sum(selected_weights)

    # Create the result dictionary in the desired format
    result_dict = {
        "result": selected_sets,
        "total_weight": total_weight
    }

    return result_dict

def find_best_solution_in_population(population):
    # Initialize variables to track the best solution and its fitness
    best_solution = None
    best_fitness = float('-inf')  # Initialize with negative infinity

    # Iterate through the population to find the best solution
    for solution in population:
        fitness = fitness_function(solution)
        if fitness > best_fitness:
            best_fitness = fitness
            best_solution = solution

    return best_solution, best_fitness

def check_coverage(binary_solution):
    # Create a set to store uncovered elements
    uncovered_elements = set(point['id'] for point in points_data)

    # Iterate through the binary solution and update uncovered elements
    for i, selected in enumerate(binary_solution):
        if selected:
            # Get the elements covered by the selected set
            covered_elements = set(points_data[i]['points_within_radius'])
            
            # Update uncovered elements by removing the covered ones
            uncovered_elements -= covered_elements

    # Check if all elements have been covered
    return len(uncovered_elements) == 0

json_file = "population_points.json"
data = load_data_from_json(json_file)
points_data = data["points_data"]
if __name__ == "__main__":

    initialSolutions = 100  # Number of solutions in the initial population
    mf=10
    mc=500
    mg=0.5
    Mutations = 1000

    # Use s_elite function to obtain elite sets
    elite_sets = s_elite()
    
    population = generate_initial_population(initialSolutions)
    
    # Perform genetic algorithm steps here, including binary tournament and crossover
start_time = time.perf_counter()
for t in range(Mutations):
    parent1, parent2 = binary_tournament_selection(population)
    child_solution = form_new_solution_by_crossover(parent1, parent2)
    child_solution = mutation(child_solution, elite_sets, mf, mc, mg, t)
    child_solution = heuristic_feasibility_operator(child_solution)
    population = replace_solution_above_average_fitness(population, child_solution)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print("Elapsed time:", elapsed_time)

best_solution, best_fitness=find_best_solution_in_population(population)

best_solution=convert_to_solution_format(best_solution)

with open("genetic_solution_LSCP.json", "w") as file:
    json.dump(best_solution, file, indent=2)





