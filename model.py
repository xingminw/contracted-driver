import json
import numpy as np
import matplotlib.pyplot as plt


def passenger_demand_function(q_b, theta_b, f_b, w_b, beta_b):
    """
    get the passenger's demand (unit: vehicle*hour)
    :param q_b: constant demand for each demand (unit: vehicle*hour)
    :param theta_b: a coefficient, peak hour is smaller than off-peak
    :param f_b: travel fare
    :param w_b: waiting time
    :param beta_b: weight of the waiting time, $ per hour
    :return: the realistic passenger's demand
    """
    q_b = q_b * np.exp(-theta_b * (f_b + beta_b * w_b))
    return q_b


def get_waiting_time(vacant_hours, area, nu_b):
    """

    :param vacant_hours:
    :param area:
    :param nu_b:
    :return:
    """
    waiting_time = (np.sqrt(np.pi / 2)) / (2 * nu_b * np.sqrt(vacant_hours / area))
    return waiting_time


def get_passenger_demand(travel_demand, travel_fare, vehicle_hours,
                         passenger_demand_elastic, waiting_time_weight,
                         area, avg_speed, charge_proportion):
    """

    :param travel_demand:
    :param travel_fare:
    :param vehicle_hours:
    :param passenger_demand_elastic:
    :param waiting_time_weight:
    :param area:
    :param avg_speed:
    :param charge_proportion:
    :return:
    """
    # here try to get the passenger demand using the fixed point method
    average_trip_duration = 0.25

    left_hour = 0.001
    right_hour = vehicle_hours
    while 1:
        mid_hour = (left_hour + right_hour) / 2
        waiting_time = get_waiting_time(mid_hour, area=area, nu_b=avg_speed)
        passenger_demand = passenger_demand_function(travel_demand, passenger_demand_elastic,
                                                     travel_fare, waiting_time, waiting_time_weight)
        mid_val = vehicle_hours - passenger_demand * average_trip_duration - mid_hour

        if abs(mid_val) < 0.001:
            break
        if mid_val > 0:
            left_hour = mid_hour
        else:
            right_hour = mid_hour
    unit_revenue = passenger_demand * (1 - charge_proportion) * travel_fare / vehicle_hours
    return passenger_demand, unit_revenue


def get_link_vehicle_hours(path_set_dict, path_flow_list):
    """

    :param path_set_dict:
    :param path_flow_list:
    :return:
    """
    current_index = 0
    link_vehicle_hours = np.linspace(0, 0, 24)
    for driver_id in path_set_dict.keys():
        driver_path_set = path_set_dict[driver_id]
        for path in driver_path_set:
            link_vehicle_hours += np.array(path) * path_flow_list[current_index]
            current_index += 1
    return link_vehicle_hours.tolist()


def get_solution_state(path_set_dict, path_flow_list, network,
                       contracted_plan, contracted_fracs, bonus=0,
                       output_figure=False):
    solution_state = {}
    # get the total link flow:
    current_index = 0
    link_vehicle_hours = np.linspace(0, 0, 24)
    drivers_vehicle_hours_list = []
    for driver_id in path_set_dict.keys():
        driver_path_set = path_set_dict[driver_id]
        driver_vehicle_hours = np.linspace(0, 0, 24)

        for path in driver_path_set:
            link_vehicle_hours += np.array(path) * path_flow_list[current_index]
            driver_vehicle_hours += np.array(path) * path_flow_list[current_index]
            current_index += 1

        drivers_vehicle_hours_list.append(driver_vehicle_hours.tolist())

    solution_state["total_link_hours"] = link_vehicle_hours.tolist()
    solution_state["vehicle_link_hours"] = drivers_vehicle_hours_list
    link_revenue_list = network.get_link_revenue_list(solution_state["total_link_hours"])

    # get base demand and realistic demand
    base_demand_list = []
    realistic_demand_list = []
    total_platform_benefit = 0
    total_passenger_benefit = 0

    for link_id in range(len(link_vehicle_hours)):
        link = network.links[link_id]
        link_demand = link.get_link_base_demand()
        total_passenger_benefit += link.get_link_passenger_total_benefit(link_vehicle_hours[link_id])
        link_realistic_demand, unit_revenue = \
            link.get_link_passenger_demand_and_unit_revenue(link_vehicle_hours[link_id])
        base_demand_list.append(link_demand)
        total_platform_benefit += \
            link_vehicle_hours[link_id] * unit_revenue * link.platform_charge / (1 - link.platform_charge)
        realistic_demand_list.append(link_realistic_demand)
    solution_state["base_demand"] = base_demand_list
    solution_state["realized_demand"] = realistic_demand_list
    # solution_state["passenger_benefits"] = total_passenger_benefit

    mid_value = int(len(path_set_dict) / 2) - 1
    paths_num = len(path_set_dict[0])
    temp_index = 0

    equilibrium_cost_list = []
    drivers_num_list = []
    total_path_profit_list = []
    equilibrium_path_list = []

    total_driver_profit = 0
    for driver_id in path_set_dict.keys():
        path_profit_list = []
        for path in path_set_dict[driver_id]:
            drivers = network.drivers[driver_id]

            if driver_id > mid_value:
                local_bonus = bonus
            else:
                local_bonus = 0
            driver_cost = drivers.get_path_cost(path, local_bonus)
            driver_revenue = np.sum(np.array(path) * np.array(link_revenue_list))
            driver_profit = driver_revenue - driver_cost
            path_profit_list.append(driver_profit)

        total_path_profit_list.append(path_profit_list)
        driver_paths_distribution = path_flow_list[temp_index * paths_num:
                                                   temp_index * paths_num + paths_num].tolist()

        local_agg_driver_benefit = np.sum(np.array(driver_paths_distribution) * np.array(path_profit_list))
        total_driver_profit += local_agg_driver_benefit
        local_driver_nums = np.sum(driver_paths_distribution)
        if local_driver_nums > 0:
            equilibrium_cost_list.append(local_agg_driver_benefit / local_driver_nums)
        else:
            equilibrium_cost_list.append(0)
        equilibrium_path_list.append(driver_paths_distribution)
        drivers_num_list.append(local_driver_nums)

        temp_cost_list = []
        for temp_num_idx in range(len(driver_paths_distribution)):
            if driver_paths_distribution[temp_num_idx] > 1:
                temp_cost_list.append(path_profit_list[temp_num_idx])

        # print(temp_cost_list)
        if len(temp_cost_list) > 0:
            if np.var(temp_cost_list) > 5:
                print("Not equilibrium!!!")
        temp_index += 1
    solution_state["equilibrium_path_flow"] = equilibrium_path_list
    solution_state["drivers_distribute"] = drivers_num_list

    driver_types = int(len(drivers_num_list) / 2)
    contracted_drivers_num = drivers_num_list[driver_types: 2 * driver_types]

    solution_state["equilibrium_benefit"] = equilibrium_cost_list

    user_num = int(len(equilibrium_cost_list) / 2)
    lambda_const = 0.1
    bonus_benchmark = 25
    contract_profit_ratio_list = []
    for temp_id in range(user_num):
        contract_val = np.exp(lambda_const * equilibrium_cost_list[temp_id + user_num]) * bonus / bonus_benchmark
        freelance_val = np.exp(lambda_const * equilibrium_cost_list[temp_id])
        contract_profit_ratio_list.append(contract_val / (contract_val + freelance_val))

    solution_state["contract_profit_ratio"] = contract_profit_ratio_list
    solution_state["path_profit"] = total_path_profit_list
    solution_state["driver_profits"] = total_driver_profit
    solution_state["platform_profits"] = total_platform_benefit - np.sum(contracted_drivers_num) * bonus

    if output_figure:
        plt.figure(dpi=200, figsize=[13.5, 7.5])
        total_width = 0.9
        n = int(len(solution_state["vehicle_link_hours"]) / 2)
        width = total_width / n
        x = np.arange(24)
        x = x - (total_width - width) / 2

        plt.bar(0, 1, [0], color=(0, 0, 1), alpha=0.1, label="Contracted Periods")

        y_lim_max = 0
        for driver_idx in range(n):
            local_vehicle_hours = np.array(solution_state["vehicle_link_hours"][driver_idx]) + \
                                  np.array(solution_state["vehicle_link_hours"][driver_idx + n])

            y_lim_max = np.max([y_lim_max, 1.05 * np.max(local_vehicle_hours)])
            plt.bar(x + driver_idx * width, local_vehicle_hours,
                    width=width, label="Driver Class " + str(driver_idx) + " (Contracted)")
            plt.bar(x + driver_idx * width, solution_state["vehicle_link_hours"][driver_idx],
                    width=width, label="Driver Class " + str(driver_idx) + " (Freelance)")

        for plan_idx in range(len(contracted_plan)):
            plan_val = contracted_plan[plan_idx]
            if plan_val > 0:
                plt.fill_between([plan_idx - 0.5, plan_idx + 0.5], [y_lim_max, y_lim_max], color=(0, 0, 1), alpha=0.1)

        plt.text(0, 0.8 * y_lim_max, "Bonus: " + str(np.round(bonus, 2)) + "$\n"
                 + "Platform Profits: " + str(int(solution_state["platform_profits"] / 1000)) + "k$\n"
                 + "Drivers Profits: " + str(int(total_driver_profit / 1000)) + "k$\n", fontsize=14)

        plt.xlabel("Hour")
        plt.ylabel("Number of Vehicles")
        plt.ylim([0, y_lim_max])
        plt.xlim([-1, 24])
        plt.legend(loc='upper right')

        plt.xticks(np.linspace(0, 23, 24).tolist(), [str(int(val + 1)) for val in np.linspace(0, 23, 24).tolist()])
        plt.savefig("data/figure/link_distribution.png")
        plt.close()

        plt.figure(dpi=200, figsize=[10, 6])
        plt.plot(base_demand_list, ".-", label="Base demand")
        plt.plot(realistic_demand_list, ".-", label="Realized demand")
        plt.xlabel("Hour")
        plt.ylabel("Demand (hr)")
        plt.savefig("data/figure/realized_demand.png")
        plt.xlim([-1, 24])
        plt.legend()
        plt.xticks(np.linspace(0, 23, 24).tolist(), [str(int(val + 1)) for val in np.linspace(0, 23, 24).tolist()])
        plt.close()

        with open("data/figure/solution.json", "w") as temp_file:
            json.dump(solution_state, temp_file)

    return solution_state


if __name__ == '__main__':
    pass

