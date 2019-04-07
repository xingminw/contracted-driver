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


def get_solution_state(path_set_dict, path_flow_list, network):
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
    print(solution_state)

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

    plt.figure()
    plt.plot(solution_state["total_link_hours"], ".-")
    for vehicle_flow in solution_state["vehicle_link_hours"]:
        plt.plot(vehicle_flow, ".-")
    plt.show()
    return solution_state

