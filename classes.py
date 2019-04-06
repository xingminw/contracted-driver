import model


class Link(object):
    def __init__(self, link_id, demand=None,
                 travel_fare=None, waiting_time_weight=None,
                 passenger_elastic=None, sharing_area=None,
                 avg_speed=None):
        self.link_id = link_id
        self.demand = demand
        self.travel_fare = travel_fare
        self.waiting_time_weight = waiting_time_weight
        self.passenger_elastic_val = passenger_elastic
        self.sharing_area = sharing_area
        self.avg_speed = avg_speed

    def get_link_passenger_demand(self, vehicle_hours):
        link_passenger_demand = model.get_passenger_demand(self.demand, self.travel_fare, vehicle_hours,
                                                           self.passenger_elastic_val, self.waiting_time_weight,
                                                           self.sharing_area, self.avg_speed)
        return link_passenger_demand


class Drivers(object):
    def __init__(self):
        pass


class Network(object):
    def __init__(self):
        pass



