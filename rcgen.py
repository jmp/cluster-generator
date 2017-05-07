#!/usr/bin/env python
"""
Random cluster generator.
Generates clusters with the given parameters.
Run with the --help option to see all the flags.
"""

from __future__ import print_function
from argparse import ArgumentParser
from os.path import basename
from random import gauss, randint, uniform, seed
from time import time

# Optional, for visualization
try:
    from matplotlib import pyplot
except ImportError:
    pyplot = None


def parse_args():
    """
    Parses and returns the command-line arguments.
    """
    parser = ArgumentParser(description="Generate random, two-dimensional Gaussian clusters.")
    parser.add_argument("--seed", type=int, default=int(time()), metavar="N",
                        help="random seed (default: current time)")
    parser.add_argument("--num-clusters", type=int, default=15, metavar="N",
                        help="number of clusters in the dataset (default: 15)")
    parser.add_argument("--min-points", type=int, default=200, metavar="N",
                        help="minimum number of points in a cluster (default: 100)")
    parser.add_argument("--max-points", type=int, default=1000, metavar="N",
                        help="maximum number of points in a cluster (default: 5000)")
    parser.add_argument("--min-x", type=int, default=1000, metavar="X",
                        help="minimum x coordinate for the cluster centers (default: 10000)")
    parser.add_argument("--max-x", type=int, default=2000, metavar="X",
                        help="maximum x coordinate for the cluster centers (default: 100000)")
    parser.add_argument("--min-y", type=int, default=1000, metavar="Y",
                        help="minimum y coordinate for the cluster centers (default: 10000)")
    parser.add_argument("--max-y", type=int, default=2000, metavar="Y",
                        help="maximum y coordinate for the cluster centers (default: 100000)")
    parser.add_argument("--min-sigma", type=float, default=5, metavar="SIGMA",
                        help="minimum standard deviation for cluster points (default: 5)")
    parser.add_argument("--max-sigma", type=float, default=100, metavar="SIGMA",
                        help="maximum standard deviation for cluster points (default: 50)")
    parser.add_argument("--points-file", default="points.txt", metavar="FILENAME",
                        help="output file for data points (default: points.txt)")
    parser.add_argument("--centroids-file", default="centroids.txt", metavar="FILENAME",
                        help="output file for ground truth centroids (default: centroids.txt)")

    return parser.parse_args()


def write_points_to_file(points, file):
    """
    Writes the given points to a file, one vector per line,
    with components separated by spaces.
    """
    for point in points:
        print(" ".join(str(component) for component in point), file=file)


def generate_cluster(num_points, mean_x, mean_y, sigma):
    """
    Generates a random Gaussian cluster with num_points.
    The cluster mean will be x, y and its standard deviation sigma.
    """
    return [(
        int(gauss(mean_x, sigma)),
        int(gauss(mean_y, sigma)),
    ) for _ in range(num_points)]


def generate_clusters(num_clusters, limits):
    """
    Generates the given number of clusters and returns the generated points
    and the ground truth cluster centers.
    """
    clusters = []
    ground_truth = []
    for _ in range(num_clusters):
        mean = (
            randint(limits["min_x"], limits["max_x"]),
            randint(limits["min_y"], limits["max_y"]),
        )
        sigma = uniform(limits["min_sigma"], limits["max_sigma"])
        points = generate_cluster(
            num_points=randint(limits["min_points"], limits["max_points"]),
            mean_x=mean[0],
            mean_y=mean[1],
            sigma=sigma,
        )
        clusters.append(points)
        ground_truth.append({
            'mean': mean,
            'sigma': sigma,
            'n': len(points),
        })
    return clusters, ground_truth


def print_parameters(args):
    """
    Prints the parameters used for generating the clusters.
    """
    print("Generated clusters using the following parameters:")
    script_name = basename(__file__)
    script_parameters = " ".join("--{}={}".format(key.replace("_", "-"), value) for key, value in vars(args).items())
    print("    {} {}".format(script_name, script_parameters))


def print_ground_truth(ground_truth):
    """
    Prints the ground truth, i.e. the cluster means, as well as
    other parameters used when generating the individual clusters.
    """
    print("Ground truth:")
    for number, cluster_data in enumerate(ground_truth):
        print("    Cluster {}:".format(number + 1))
        for key, value in cluster_data.items():
            print("        {}: {}".format(key, value))


def show_plot(points, centroids, title):
    """
    Display a scatter plot of the points and centroids, if matplotlib is available.
    """
    if pyplot is None:
        return
    pyplot.figure()
    pyplot.title(title)
    pyplot.xlabel(r'$x$')
    pyplot.ylabel(r'$y$').set_rotation(0)
    # Points
    pyplot.scatter(*zip(*points), c='k', s=2)
    # Ground truth
    for centroid in centroids:
        pyplot.scatter(*zip(*[centroid]), c='r', s=40)
    pyplot.show()


def run():
    """
    The main function that parses command-line arguments, generates
    the clusters, and writes that data in the output files.
    """

    args = parse_args()

    # Seed the random number generator
    seed(args.seed)

    # Generate the clusters
    clusters, ground_truth = generate_clusters(
        args.num_clusters,
        limits={
            "min_points": min(args.min_points, args.max_points),
            "max_points": args.max_points,
            "min_x": min(args.min_x, args.max_x),
            "max_x": args.max_x,
            "min_y": min(args.min_y, args.max_y),
            "max_y": args.max_y,
            "min_sigma": min(args.min_sigma, args.max_sigma),
            "max_sigma": args.max_sigma,
        }
    )

    points = [point for cluster in clusters for point in cluster]
    centroids = [cluster_data['mean'] for cluster_data in ground_truth]

    with open(args.points_file, "wt") as file:
        write_points_to_file(points, file)

    with open(args.centroids_file, "wt") as file:
        write_points_to_file(centroids, file)

    print_parameters(args)
    print_ground_truth(ground_truth)
    show_plot(points, centroids, r"$k={}$ random clusters".format(args.num_clusters))


if __name__ == "__main__":
    run()
