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


def calculate_driver_revenue(eta, fare, demand, vehicle_hours):
    """

    :param eta:
    :param fare:
    :param demand:
    :param vehicle_hours:
    :return:
    """
    revenue = (1 - eta) * fare * demand / vehicle_hours
    return revenue


def get_passenger_demand(travel_demand, travel_fare, vehicle_hours,
                         passenger_demand_elastic, waiting_time_weight,
                         area, avg_speed):
    """

    :param travel_demand:
    :param travel_fare:
    :param vehicle_hours:
    :param passenger_demand_elastic:
    :param waiting_time_weight:
    :param area:
    :param avg_speed:
    :return:
    """
    # here try to get the passenger demand using the fixed point method
    average_trip_duration = 0.15
    vacant_hours = vehicle_hours

    while 1:
        waiting_time = get_waiting_time(vacant_hours, area=area, nu_b=avg_speed)
        passenger_demand = passenger_demand_function(travel_demand, passenger_demand_elastic,
                                                     travel_fare, waiting_time, waiting_time_weight)
        next_vacant_hours = vehicle_hours - passenger_demand * average_trip_duration
        if next_vacant_hours < 0:
            correct_flag = False
            break
        vacant_hours = next_vacant_hours
        if abs(vacant_hours - next_vacant_hours) < 0.01:
            correct_flag = True
            break

    if correct_flag is True:
        unit_revenue = passenger_demand * 0.8 * 20 / vehicle_hours
        return passenger_demand, unit_revenue

    left_hour = 0.001
    right_hour = vehicle_hours
    while 1:
        mid_hour = (left_hour + right_hour) / 2
        waiting_time = get_waiting_time(mid_hour, area=area, nu_b=avg_speed)
        passenger_demand = passenger_demand_function(travel_demand, passenger_demand_elastic,
                                                     travel_fare, waiting_time, waiting_time_weight)
        mid_val = vehicle_hours - passenger_demand * average_trip_duration

        if abs(mid_val) < 0.001:
            break
        if mid_val > 0:
            left_hour = mid_hour
        else:
            right_hour = mid_hour
    unit_revenue = passenger_demand * 0.8 * 20 / vehicle_hours
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
    print("length of path_flow_list", len(path_flow_list))
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
    print("Link revenue list", link_revenue_list)
    print("Link vehicle hours", solution_state["total_link_hours"])

    # get base demand and realistic demand
    base_demand_list = []
    realistic_demand_list = []
    for link_id in range(len(link_vehicle_hours)):
        link = network.links[link_id]
        link_demand = link.demand
        link_realistic_demand, unit_revenue = \
            link.get_link_passenger_demand_and_unit_revenue(link_vehicle_hours[link_id])
        base_demand_list.append(link_demand)
        realistic_demand_list.append(link_realistic_demand)
    solution_state["base_demand"] = base_demand_list
    solution_state["realized_demand"] = realistic_demand_list

    mid_value = int(len(path_set_dict) / 2) - 1
    paths_num = len(path_set_dict[0])
    temp_index = 0
    for driver_id in path_set_dict.keys():
        path_profit_list = []
        for path in path_set_dict[driver_id]:
            drivers = network.drivers[driver_id]

            if driver_id > mid_value:
                local_bonus = bonus
            else:
                local_bonus = 0

            print(path)
            driver_cost = drivers.get_path_cost(path, local_bonus)
            driver_revenue = np.sum(np.array(path) * np.array(link_revenue_list))
            driver_profit = driver_revenue - driver_cost
            print("driver cost", driver_cost, "driver revenue", driver_revenue, "driver profit", driver_profit)
            path_profit_list.append(driver_profit)

        driver_paths_distribution = path_flow_list[temp_index * paths_num: temp_index * paths_num + paths_num]
        temp_index += 1
        print([int(val) for val in path_profit_list])
        print([int(val) for val in driver_paths_distribution])
        print()

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

        plt.text(0, 0.9 * y_lim_max, "Bonus: " + str(np.round(bonus, 2)) + "$", fontsize=14)

        plt.xlabel("Hour")
        plt.ylabel("Number of Vehicles")
        plt.ylim([0, y_lim_max])
        plt.xlim([-1, 24])
        plt.legend()
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

    return solution_state

