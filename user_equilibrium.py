# This file is to solve the lower level user equilibrium using column generation
# Use the nonlinear programming package in scipy.optimize
# given the constraints for the contracted driver and the bonus for the contracted driver
import model
import time
import numpy as np
from scipy.optimize import minimize
from copy import deepcopy


def get_lower_level_solution(network, contracted_path, bonus, init_fracs):
    solution = None
    solution_success = False
    contracted_fracs = deepcopy(init_fracs)
    start_time = time.time()
    for iteration in range(20):
        solution = column_generation_user_equilibrium(network, contracted_path, contracted_fracs, bonus)
        temp_ans = solution["contract_profit_ratio"]

        difference_norm = np.linalg.norm(np.array(contracted_fracs) - np.array(temp_ans))

        if difference_norm < 0.05:
            solution_success = True
            end_time = time.time()
            print("Get converged solution, total time cost:", end_time - start_time)
            break

        update_ans = np.array(contracted_fracs) + (np.array(temp_ans) - np.array(contracted_fracs)) / (iteration + 1)
        contracted_fracs = update_ans.tolist()
        print(contracted_fracs, difference_norm)

    if not solution_success:
        end_time = time.time()
        print("Solution not converge! time cost:", end_time - start_time)
    return solution


def get_path_distribution_cost(x, path_set_dict, network):
    objective_value = network.get_path_distribution_objective_value(path_set_dict, x.tolist())
    return objective_value


def equality_constraint(x, start, end, value):
    temp_val = value - np.sum(x[start: end])
    return temp_val


def update_network_drivers(network, contracted_fracs):
    new_network = deepcopy(network)
    contracted_fracs = [1 - val for val in contracted_fracs]
    drivers_num = len(new_network.drivers)

    for idx in range(drivers_num):
        drivers = new_network.drivers[idx]
        new_network.drivers[idx + drivers_num] = deepcopy(drivers)
        total_drivers_amount = new_network.drivers[idx].drivers_amount
        new_network.drivers[idx + drivers_num].drivers_amount = \
            np.round((1 - contracted_fracs[idx]) * total_drivers_amount)
        new_network.drivers[idx].drivers_amount = np.round(contracted_fracs[idx] * total_drivers_amount)
        new_network.drivers[idx + drivers_num].drivers_id = idx + drivers_num
    return new_network


def get_initiate_path_set_and_flow(network, contracted_plan):
    path_set_dict = {}
    mid_index = int(len(network.drivers) / 2)

    path_flow_list = []
    for driver_id in network.drivers.keys():
        drivers = network.drivers[driver_id]
        path_flow_list.append(drivers.drivers_amount)
        if driver_id < mid_index:
            drivers_preference = drivers.links_preference
            average_preference = np.average(drivers_preference)
            path_chosen_list = []
            for link_pre in drivers_preference:
                if link_pre < average_preference:
                    path_chosen_list.append(1)
                else:
                    path_chosen_list.append(0)
            path_set_dict[driver_id] = [path_chosen_list]
        else:
            path_set_dict[driver_id] = [contracted_plan]
    return path_set_dict, path_flow_list


def column_generation_user_equilibrium(network, contracted_plan, contracted_fracs, bonus):
    network = update_network_drivers(network, contracted_fracs)

    contracted_path_list = [None, None, None, contracted_plan, contracted_plan, contracted_plan]

    path_set_dict, init_path_flow_list = get_initiate_path_set_and_flow(network, contracted_plan)

    objective_value_list = []
    previous_objective_function = 0

    for iter_idx in range(10):
        temp_path_set_dict = deepcopy(path_set_dict)
        opt_path_flow, opt_cost_value = get_optimal_path_distribution(path_set_dict,
                                                                      init_path_flow_list,
                                                                      network)
        objective_value_list.append(opt_cost_value)
        link_flow_distribution = model.get_link_vehicle_hours(path_set_dict, opt_path_flow)
        optimum_path = network.get_optimum_path(link_flow_distribution, contracted_path_list)

        total_paths = 0
        init_path_flow_list = []
        for driver_id in path_set_dict.keys():
            path_num = len(path_set_dict[driver_id])
            total_paths += (path_num + 1)
            path_set_dict[driver_id].append(optimum_path[driver_id])
            local_path_flows = opt_path_flow[driver_id * path_num: driver_id * path_num + path_num]

            update_proportion = 1 / pow(2, iter_idx + 2)
            update_path_flows = [(1 - update_proportion) * val for val in local_path_flows] +\
                                [np.sum(local_path_flows) * update_proportion]
            init_path_flow_list += update_path_flows

        if abs(previous_objective_function - opt_cost_value) < 0.0005 * abs(opt_cost_value):
            break
        previous_objective_function = opt_cost_value

    solution_state = model.get_solution_state(temp_path_set_dict, opt_path_flow,
                                              network, contracted_plan, contracted_fracs, bonus=bonus,
                                              output_figure=True)
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

    constraints_tuple = tuple(constraints_list)

    # objective_value = get_path_distribution_cost(x, path_set_dict, network)
    solution = minimize(get_path_distribution_cost, initiate_path, method="SLSQP", args=(path_set_dict, network),
                        bounds=bounds_list, constraints=constraints_tuple, options={"maxiter": 1000})
    function_value = solution.fun
    sol_path_distribution = solution.x
    # print("The best path is", sol_path_distribution, "the objective function is", function_value)
    return sol_path_distribution, function_value

