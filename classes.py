import model
import numpy as np


class Link(object):
    def __init__(self, link_id, demand=None,
                 travel_fare=None, waiting_time_weight=None,
                 passenger_elastic=None, sharing_area=None,
                 avg_speed=None, link_revenue_integral=None):
        self.link_id = link_id
        self.demand = demand
        self.travel_fare = travel_fare
        self.waiting_time_weight = waiting_time_weight
        self.passenger_elastic_val = passenger_elastic
        self.sharing_area = sharing_area
        self.avg_speed = avg_speed
        self.link_revenue_integral = link_revenue_integral

    def get_link_passenger_demand_and_unit_revenue(self, vehicle_hours):
        link_passenger_demand, unit_revenue = model.get_passenger_demand(self.demand,
                                                                         self.travel_fare, vehicle_hours,
                                                                         self.passenger_elastic_val,
                                                                         self.waiting_time_weight,
                                                                         self.sharing_area, self.avg_speed)
        return link_passenger_demand, unit_revenue

    def get_link_revenue_integral(self, link_vehicles):
        if link_vehicles > len(self.link_revenue_integral) - 2:
            print("link revenue not enough!")
            exit()
        link_veh_int = int(link_vehicles)
        link_veh_frac = link_vehicles - int(link_vehicles)
        integral = self.link_revenue_integral[link_veh_int] * (1 - link_veh_frac) + self.link_revenue_integral[
            link_veh_int] * link_veh_frac
        return integral

    def prepare_link_revenue_integral(self, max_vehicle_hours=6000):
        vehicle_hours = np.linspace(0, max_vehicle_hours, int(max_vehicle_hours) + 1).tolist()[1:]
        unit_revenues = []
        for vehicle_hour in vehicle_hours:
            passenger_demand, unit_revenue = self.get_link_passenger_demand_and_unit_revenue(vehicle_hour)
            unit_revenues.append(unit_revenue)

        length = len(vehicle_hours)
        integral_list = []
        for idx in range(length + 1):
            local_unit_revenue = unit_revenues[0: idx]
            local_integral = np.sum(local_unit_revenue)
            integral_list.append(local_integral)
        self.link_revenue_integral = integral_list


class Drivers(object):
    def __init__(self, drivers_id, number, links_preference=None,
                 unit_time_cost=None, unit_runs_cost=None):
        self.drivers_id = drivers_id
        self.drivers_amount = number
        self.links_preference = links_preference
        self.unit_time_cost = unit_time_cost
        self.unit_runs_cost = unit_runs_cost

    def get_path_cost(self, path):
        link_based = np.sum(np.array(path) * np.array(self.links_preference))
        cumulative_time = pow(float(np.sum(path)), 1.2) * self.unit_time_cost

        # count runs
        runs = 0
        for idx in range(len(path)):
            if idx == len(path) - 1:
                if (path[idx] == 0) and (path[0] == 1):
                    runs += 1
            else:
                if (path[idx] == 0) and (path[idx + 1] == 1):
                    runs += 1
        run_cost = runs * self.unit_runs_cost

        total_cost = run_cost + cumulative_time + link_based
        return total_cost


class Network(object):
    def __init__(self, links=None, drivers=None):
        self.links = links
        self.drivers = drivers

    def add_link(self, link):
        if self.links is None:
            self.links = {}
        self.links[link.link_id] = link

    def add_driver(self, driver):
        if self.drivers is None:
            self.drivers = {}
        self.drivers[driver.drivers_id] = driver

    def get_driver_amount(self):
        total_number = 0
        for driver_id in self.drivers.keys():
            drivers = self.drivers[driver_id]
            amount = drivers.drivers_amount
            total_number += amount
        return total_number

    def get_link_revenue_integral_list(self, link_flow_list):
        if len(link_flow_list) != 24:
            print("The length of the link flow is not 24!")
            exit()

        revenue_integral_list = []
        for idx in range(len(link_flow_list)):
            link = self.links[idx]
            link_revenue_integral = link.get_link_revenue_integral(link_flow_list[idx])
            revenue_integral_list.append(link_revenue_integral)
        return revenue_integral_list

    def get_path_distribution_objective_value(self, path_set_dict, path_distribution_list):
        link_flow = model.get_link_vehicle_hours(path_set_dict, path_distribution_list)
        link_integral_list = self.get_link_revenue_integral_list(link_flow)
        link_revenue_total = - np.sum(link_integral_list)

        total_objective_value = link_revenue_total

        path_flow_index = 0
        for driver_id in path_set_dict.keys():
            for path in path_set_dict[driver_id]:
                drivers = self.drivers[driver_id]
                driver_path_cost = drivers.get_path_cost(path)
                path_flow = path_distribution_list[path_flow_index]
                path_flow_index += 1
                total_objective_value += driver_path_cost * path_flow
        return total_objective_value



