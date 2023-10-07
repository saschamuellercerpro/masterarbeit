import json
import random
import math
import time

def load_data_from_json(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

def create_initial_feasible_solution_as_chromosome():
    elements_to_cover = [point['id'] for point in points_data]
    sets = [set(point['points_within_radius']) for point in points_data]
    selected_set_ids = []
    coverage_count = {element: 0 for element in elements_to_cover}
    for element in elements_to_cover:
        covering_sets = [s for s in sets if element in s]
        if not covering_sets:
            print("No set covers element:", element)
            continue
        selected_set = random.choice(covering_sets)
        selected_set_ids.append(sets.index(selected_set))
        for covered_element in selected_set:
            coverage_count[covered_element] += 1
    clone_selected_set_ids = selected_set_ids.copy()
    while clone_selected_set_ids:
        selected_set_id = random.choice(clone_selected_set_ids)
        clone_selected_set_ids.remove(selected_set_id)
        selected_set = sets[selected_set_id]
        remove_set_from_selected = True
        for covered_element in selected_set:
            if coverage_count[covered_element] < 2:
                remove_set_from_selected = False
                break
        if remove_set_from_selected:
            for covered_element in selected_set:
                coverage_count[covered_element] -= 1
            selected_set_ids.remove(selected_set_id)
    num_sets = len(sets)
    selected_sets_array = [1 if i in selected_set_ids else 0 for i in range(num_sets)]
    return selected_sets_array, coverage_count

def generate_initial_population(n):
    population = []
    for _ in range(n):
        solution, _ = create_initial_feasible_solution_as_chromosome()
        population.append(solution)
    return population

def fitness_function(solution):
    total_weight = 0
    for i, selected in enumerate(solution):
        if selected == 1:
            total_weight += points_data[i]['weight']
    return total_weight

def binary_tournament_selection(population):
    selected_solutions = []
    for _ in range(2):
        tournament_pool = random.sample(range(len(population)), 2)
        solution1, solution2 = tournament_pool
        fitness1 = fitness_function(population[solution1])
        fitness2 = fitness_function(population[solution2])
        if fitness1 < fitness2:
            selected_solutions.append(population[solution1])
        else:
            selected_solutions.append(population[solution2])
    return selected_solutions

def form_new_solution_by_crossover(solution1, solution2):
    child_solution = []
    fitness1 = fitness_function(solution1)
    fitness2 = fitness_function(solution2)
    probability = fitness2 / (fitness1 + fitness2)
    for i in range(len(solution1)):
        if solution1[i] == solution2[i]:
            child_solution.append(solution1[i])
        else:
            if random.random() < probability:
                child_solution.append(solution1[i])
            else:
                child_solution.append(solution2[i])
    return child_solution

def number_of_bits_mutated(mf, mc, mg, t):
    exponent = -4 * mg * (t - mc) / mf
    return mf / (1 + math.exp(exponent))

def s_elite(num_elite_sets=5):
    elite_sets = {}
    for point in points_data:
        element_id = point['id']
        sets_that_cover_point = []
        for other_point in points_data:
            if element_id in other_point['points_within_radius']:
                sets_that_cover_point.append(other_point['id'])
        sorted_sets = sorted(sets_that_cover_point, key=lambda set_id: points_data[set_id]['weight'])
        elite_sets[element_id] = sorted_sets[:num_elite_sets]
    union_of_elite_sets = set()
    for sets in elite_sets.values():
        union_of_elite_sets.update(sets)
    return union_of_elite_sets

def mutation(child_solution, elite_sets, mf, mc, mg, t):
    num_bits_to_mutate = int(number_of_bits_mutated(mf, mc, mg, t))
    sets_to_mutate = random.sample(sorted(elite_sets), num_bits_to_mutate)
    for set_id in sets_to_mutate:
        child_solution[set_id] = 1 - child_solution[set_id]
    return child_solution

def heuristic_feasibility_operator(child_solution):
    solution = child_solution.copy()
    covered_elements = set()
    weight_to_ratio = {}
    uncovered_elements = set()
    for i, selected in enumerate(child_solution):
        if selected:
            covered_elements.update(points_data[i]['points_within_radius'])
    all_elements = set(point['id'] for point in points_data)
    uncovered_elements = all_elements - covered_elements
    for point in points_data:
        set_id = point['id']
        set_weight = point['weight']
        covered_elements = point['points_within_radius']
        num_uncovered_elements_covered = len(set(covered_elements).intersection(uncovered_elements))
        if num_uncovered_elements_covered > 0:
            ratio = set_weight / num_uncovered_elements_covered
        else:
            ratio = float('inf')
        weight_to_ratio[set_id] = ratio
    sorted_sets = sorted(points_data, key=lambda point: weight_to_ratio[point['id']])
    for point in sorted_sets:
        set_id = point['id']
        covered_elements = set(point['points_within_radius'])
        common_elements = covered_elements.intersection(uncovered_elements)
        if common_elements:
            solution[set_id] = 1
            uncovered_elements -= common_elements
        if not uncovered_elements:
            break
    element_coverage_count = {element['id']: 0 for element in points_data}
    for i, selected in enumerate(solution):
        if selected:
            covered_elements = points_data[i]['points_within_radius']
            for covered_element in covered_elements:
                element_coverage_count[covered_element] += 1
    sorted_sets = sorted(points_data, key=lambda point: -weight_to_ratio[point['id']])
    for point in sorted_sets:
        set_id = point['id']
        covered_elements = set(point['points_within_radius'])
        if all(element_coverage_count[element] >= 2 for element in covered_elements):
            solution[set_id] = 0
            for covered_element in covered_elements:
                element_coverage_count[covered_element] -= 1
    return solution

def is_solution_in_population(solution, population):
    solution_tuple = tuple(solution)
    return solution_tuple in population

def replace_solution_above_average_fitness(population, child_solution):
    fitness_values = [fitness_function(solution) for solution in population]
    average_fitness = sum(fitness_values) / len(fitness_values)
    above_average_indices = [i for i, fitness in enumerate(fitness_values) if fitness > average_fitness]
    if above_average_indices:
        solution_to_replace_index = random.choice(above_average_indices)
        population[solution_to_replace_index] = child_solution
    return population

def convert_to_solution_format(binary_solution):
    selected_sets = []
    selected_weights = []
    for i, selected in enumerate(binary_solution):
        if selected:
            selected_sets.append(i)
            selected_weights.append(points_data[i]['weight'])
    total_weight = sum(selected_weights)
    result_dict = {
        "result": selected_sets,
        "total_weight": total_weight
    }
    return result_dict

def find_best_solution_in_population(population):
    best_solution = None
    best_fitness = float('-inf')
    for solution in population:
        fitness = fitness_function(solution)
        if fitness > best_fitness:
            best_fitness = fitness
            best_solution = solution
    return best_solution, best_fitness

def check_coverage(binary_solution):
    uncovered_elements = set(point['id'] for point in points_data)
    for i, selected in enumerate(binary_solution):
        if selected:
            covered_elements = set(points_data[i]['points_within_radius'])
            uncovered_elements -= covered_elements
    return len(uncovered_elements) == 0

json_file = "population_points.json"
data = load_data_from_json(json_file)
points_data = data["points_data"]
if __name__ == "__main__":
    initialSolutions = 100
    mf = 10
    mc = 500
    mg = 0.5
    Mutations = 1000
    elite_sets = s_elite()
    population = generate_initial_population(initialSolutions)
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
    best_solution, best_fitness = find_best_solution_in_population(population)
    best_solution = convert_to_solution_format(best_solution)
    with open("genetic_solution_LSCP.json", "w") as file:
        json.dump(best_solution, file, indent=2)
