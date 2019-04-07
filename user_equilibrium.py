# This file is to solve the lower level user equilibrium using column generation
# Use the nonlinear programming package in scipy.optimize
# given the constraints for the contracted driver and the bonus for the contracted driver
import model
import numpy as np
from initiate import initiate_network
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from copy import deepcopy


def get_path_distribution_cost(x, path_set_dict, network):
    objective_value = network.get_path_distribution_objective_value(path_set_dict, x.tolist())
    return objective_value


def equality_constraint(x, start, end, value):
    temp_val = np.sum(x[start: end]) - value
    return temp_val


def column_generation_user_equilibrium():
    network = initiate_network(reload=False)
    path_set_dict = {0: [[0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]],
                     1: [[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]],
                     2: [[1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]]}

    total_paths = len(path_set_dict)
    objective_value_list = []
    previous_objective_function = 0

    for iter_idx in range(10):
        temp_path_set_dict = deepcopy(path_set_dict)
        initiate_path_distribution = np.linspace(0, 0, total_paths)
        opt_path_flow, opt_cost_value = get_optimal_path_distribution(path_set_dict,
                                                                      initiate_path_distribution,
                                                                      network)
        objective_value_list.append(opt_cost_value)
        link_flow_distribution = model.get_link_vehicle_hours(path_set_dict, opt_path_flow)
        optimum_path = network.get_optimum_path(link_flow_distribution)

        total_paths = 0
        for driver_id in path_set_dict.keys():
            path_num = len(path_set_dict[driver_id])
            total_paths += (path_num + 1)
            path_set_dict[driver_id].append(optimum_path[driver_id])

        if abs(previous_objective_function - opt_cost_value) < 0.002 * abs(opt_cost_value):
            break
        previous_objective_function = opt_cost_value

    solution_state = model.get_solution_state(temp_path_set_dict, opt_path_flow, network)
    return solution_state


def get_optimal_path_distribution(path_set_dict, initiate_path, network):
    bounds_list = []
    constraints_list = []
    current_cursor = 0

    for driver_id in path_set_dict.keys():
        local_constraint_dict = {"type": "eq"}
        drivers_num = network.drivers[driver_id].drivers_amount
        path_nums = len(path_set_dict[driver_id])
        local_constraint_dict["fun"] = equality_constraint
        local_constraint_dict["args"] = (current_cursor, current_cursor + path_nums, drivers_num)
        current_cursor += path_nums
        constraints_list.append(local_constraint_dict)
        for idx in range(path_nums):
            bounds_list.append((0, drivers_num))
    bounds_tuple = tuple(bounds_list)
    constraints_tuple = tuple(constraints_list)

    # objective_value = get_path_distribution_cost(x, path_set_dict, network)
    solution = minimize(get_path_distribution_cost, initiate_path, method="SLSQP",
                        bounds=bounds_tuple, args=(path_set_dict, network),
                        constraints=constraints_tuple)
    function_value = solution.fun
    sol_path_distribution = solution.x
    print("The best path is", sol_path_distribution, "the objective function is", function_value)
    return sol_path_distribution, function_value


if __name__ == '__main__':
    column_generation_user_equilibrium()

