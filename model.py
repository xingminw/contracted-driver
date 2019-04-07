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
    waiting_time = (np.sqrt(np.pi / 2)) / (2 * nu_b * np.sqrt(vacant_hours / area))
    return waiting_time


def calculate_driver_revenue(eta, fare, demand, vehicle_hours):
    revenue = (1 - eta) * fare * demand / vehicle_hours
    return revenue


def get_passenger_demand(travel_demand, travel_fare, vehicle_hours,
                         passenger_demand_elastic, waiting_time_weight,
                         area, avg_speed):
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


def passenger_demand_illustration():
    vehicle_hours = np.linspace(0, 30000, 20).tolist()
    print(vehicle_hours)
    vehicle_demands = []
    unit_revenues = []
    for veh_hr in vehicle_hours:
        travel_demand = get_passenger_demand(80000, 20, veh_hr, 0.03, 33, 10000, 40)
        print("Vehicle hours", veh_hr, "demand", travel_demand)
        vehicle_demands.append(travel_demand)
        unit_revenues.append(travel_demand * 0.8 * 20 / veh_hr)

    plt.figure(dpi=200)
    plt.plot(vehicle_hours, vehicle_demands, "b.-")
    plt.ylabel("Total demand ($veh\cdot hr$)")
    plt.xlabel("Total vehicle hours ($veh\cdot hr$)")
    plt.savefig("data/passenger_demand.png")

    plt.figure(dpi=200)
    plt.plot(vehicle_hours, unit_revenues, "b.-")
    plt.ylabel("Average Revenue of Drivers ($\$/hr$)")
    plt.xlabel("Total vehicle hours ($veh\cdot hr$)")
    plt.savefig("data/unit_revenue.png")


if __name__ == '__main__':
    # passenger_demand_illustration()
    a = get_passenger_demand(10000.0, 20.0, 526.3157894736842, 0.04, 20.0, 10000.0, 50.0)
    print(a)
