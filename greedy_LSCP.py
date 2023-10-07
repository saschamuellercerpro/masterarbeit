import json
import time

def load_data_from_json(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

def greedy_set_covering(points_data):
    selected_facilities = []
    uncovered_points = set(point["id"] for point in points_data)

    while len(uncovered_points) > 0:
        best_facility = None
        best_weight_per_coverage = float("inf")

        for facility in points_data:
            covered_points = set(facility["points_within_radius"]).intersection(uncovered_points)
            num_covered_points = len(covered_points)
            
            if num_covered_points == 0:
                continue

            weight_per_coverage = facility["weight"] / num_covered_points

            if weight_per_coverage < best_weight_per_coverage:
                best_facility = facility
                best_weight_per_coverage = weight_per_coverage
                

        if best_facility:
            selected_facilities.append(best_facility['id'])
            uncovered_points -= set(best_facility["points_within_radius"])

    total_weight = sum(point["weight"] for point in points_data if point["id"] in selected_facilities)

    return {"result": selected_facilities, "total_weight": total_weight}

json_file = "population_points.json"
data = load_data_from_json(json_file)

radius = data["radius"]
total_points = data["total_points"]
points_data = data["points_data"]

start_time = time.perf_counter()
selected_facilities = greedy_set_covering(points_data)
end_time = time.perf_counter()
elapsed_time = end_time - start_time

print("Elapsed time:", elapsed_time)

with open("greedy_solution_LSCP.json", "w") as file:
    json.dump(selected_facilities, file, indent=2)
