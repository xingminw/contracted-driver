# This file is to solve the lower level user equilibrium using column generation
# Use the nonlinear programming package in scipy.optimize
# given the constraints for the contracted driver and the bonus for the contracted driver
import model
import numpy as np
from initiate import initiate_network
from scipy.optimize import minimize


def get_path_distribution_cost(x, path_set_dict, network):
    objective_value = network.get_path_distribution_objective_value(path_set_dict, x.tolist())
    return objective_value


def main():
    network = initiate_network(reload=False)
    path_set_dict = {0: [[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]],
                     1: [[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]]}
    x = np.array([4000, 1000, 500, 500])

    objective_value = get_path_distribution_cost(x, path_set_dict, network)
    print(objective_value)


if __name__ == '__main__':
    main()

