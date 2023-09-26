import json
import matplotlib.pyplot as plt

def plot_points_with_radii(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    radius = data["radius"]
    total_points = data["total_points"]
    points_data = data["points_data"]

    points = [{"id": point_data["id"], "x": point_data["x"], "y": point_data["y"]} for point_data in points_data]

    # Plot the points and the circles with the specified radius
    x_coords, y_coords = zip(*[(point["x"], point["y"]) for point in points])
    plt.scatter(x_coords, y_coords, s=5, color='blue')
    
    # Add the IDs next to the points
    for point in points:
        plt.text(point["x"], point["y"], str(point["id"]), fontsize=8, ha='left', va='bottom', color='black')
        
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Population Points with Radii (Total Points: {total_points})')
    plt.grid(True)
    plt.show()

# Example usage:
json_file_path = "population_points.json"
plot_points_with_radii(json_file_path)
