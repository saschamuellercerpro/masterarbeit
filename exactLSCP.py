import json
import pulp

def set_covering(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    points_data = data["points_data"]
    selected = pulp.LpVariable.dicts("Selected", [obj['id'] for obj in points_data], cat=pulp.LpBinary)
    set_covering_problem = pulp.LpProblem("SetCoveringProblem", pulp.LpMinimize)
    set_covering_problem += pulp.lpSum(selected[obj["id"]]*obj["weight"] for obj in points_data)

    for point_data in points_data:
        set_covering_problem += pulp.lpSum(selected[point_id] for point_id in point_data["points_within_radius"]) >= 1

    set_covering_problem.solve()
    selected_points = [obj['id'] for obj in points_data if selected[obj['id']].value() == 1]
    total_weight = pulp.value(set_covering_problem.objective)
    result = {"result": selected_points, "total_weight": total_weight}
    return result

json_file_path = "population_points.json"
selected_points = set_covering(json_file_path)
with open("exact_solution_LSCP.json", "w") as file:
    json.dump(selected_points, file, indent=2)
