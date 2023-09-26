import numpy as np
import json
import matplotlib.pyplot as plt
import os

def generate_population_points(n):
    center_x, center_y = 0, 0
    max_distance = 500  # Maximum distance from the center

    points = []
    for i in range(n):
        generated=False
        while not generated:
            # Generate random radii from the center following a Gaussian distribution
            radii = np.random.normal(loc=0, scale=max_distance/2)

            # Generate random angles in radians
            angle = np.random.uniform(0, 2*np.pi)

            # Calculate the x and y coordinates of the point
            x_coord = center_x + radii * np.cos(angle)
            y_coord = center_y + radii * np.sin(angle)

            # Check if the point is within the acceptable range, and add it to the list with an ID and weight
            if abs(x_coord) <= max_distance and abs(y_coord) <= max_distance:
                weight = np.random.randint(1, 4)  # Generate a random weight from 0 to 3
                points.append({"id": i, "x": x_coord, "y": y_coord, "weight": weight})
                generated=True

    return points

def distance(point1, point2):
    x1, y1 = point1["x"], point1["y"]
    x2, y2 = point2["x"], point2["y"]
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def points_within_radius(all_points, center_point, radius):
    within_radius = [point for point in all_points if distance(center_point, point) <= radius]
    return within_radius

def all_points_with_radii(points, radius=50, total_points=100,maximumFacilities=5):
    points_with_radii = {
        "radius": radius,
        "maximumFacilities":maximumFacilities,
        "total_points": total_points,
        "points_data": []
    }
    for point in points:
        nearby_points = points_within_radius(points, point, radius)
        points_with_radii["points_data"].append({
            "id": point["id"],
            "x": point["x"],
            "y": point["y"],
            "weight": point["weight"],  # Include the weight in the points_data dictionary
            "points_within_radius": [p["id"] for p in nearby_points]
        })
    return points_with_radii

# Example usage with 100 points:
num_points = 100
points = generate_population_points(num_points)
radius = 125
maximumFacilities=5

# Get the dictionary of points with their respective lists of points within the specified radius
points_with_radii = all_points_with_radii(points, radius, total_points=num_points,maximumFacilities=maximumFacilities)

# Save the points data to a JSON file
with open("population_points.json", "w") as file:
    json.dump(points_with_radii, file, indent=2)
os.remove("exact_solution_LSCP.json")
os.remove("exact_solution_MCLP.json")