import json
import pulp

def set_covering(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Get the points data from the JSON
    points_data = data["points_data"]

    # Create a binary variable for each point indicating if it is selected or not
    selectedFacilities = pulp.LpVariable.dicts("selectedFacilities", [obj['id'] for obj in points_data], cat=pulp.LpBinary)
    selectedPoints = pulp.LpVariable.dicts("selectedPoints", [obj['id'] for obj in points_data], cat=pulp.LpBinary)

    # Create the set covering problem
    set_covering_problem = pulp.LpProblem("SetCoveringProblem", pulp.LpMaximize)

    # Objective function: minimize the total number of selected points
    set_covering_problem += pulp.lpSum(selectedPoints[obj["id"]] for obj in points_data)

    # Constraints: all points must be covered
    for point_data in points_data:
        set_covering_problem += pulp.lpSum(selectedFacilities[point_id] for point_id in point_data["points_within_radius"]) >= selectedPoints[point_data["id"]]

    set_covering_problem += pulp.lpSum(selectedFacilities[obj['id']] for obj in points_data) <= data["maximumFacilities"]
    

    # Solve the problem
    set_covering_problem.solve()

    # Get the selected points
    selected_points = [obj['id'] for obj in points_data if selectedFacilities[obj['id']].value() == 1]
    total_points_covered = pulp.value(set_covering_problem.objective)
    result = {"result": selected_points, "total_points_covered": total_points_covered}
    return result

# Example usage:
json_file_path = "population_points.json"
selected_points = set_covering(json_file_path)
with open("exact_solution_MCLP.json", "w") as file:
    json.dump(selected_points, file, indent=2)
