import numpy as np


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


def get_link_vehicle_hours(path_set_dict, path_flow_dict):
    pass
