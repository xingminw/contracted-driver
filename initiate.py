import os
import pickle
import classes as cls
import matplotlib.pyplot as plt
from tqdm import tqdm
from time import sleep

input_folder = "data/input"
driver_file_name = os.path.join(input_folder, "drivers.txt")
links_file_name = os.path.join(input_folder, "links.txt")

network_file = os.path.join("data/network.pickle")


def initiate_network(reload=False):
    if (not os.path.exists(network_file)) or reload:
        print("Reload the network information!")
        network = cls.Network()
        network = load_links(network)
        network = load_drivers(network)

        print("Start to prepare the integral of the demand function")
        sleep(0.1)
        for link_id in tqdm(network.links.keys()):
            link = network.links[link_id]
            link.prepare_link_revenue_integral(network.get_driver_amount() * 2)
        sleep(0.1)
        print("Prepare integral done!")

        with open(network_file, "wb") as temp_file:
            pickle.dump(network, temp_file)

        print("Save the network buffer done!")
        return network
    else:
        print("Load the network from buffer directly...")
        with open(network_file, "rb") as temp_file:
            network = pickle.load(temp_file)
        print("Load the network success!")
        return network


def load_links(network):
    with open(links_file_name, "r") as links_file:
        links_lines = links_file.readlines()[1:]

    for link_info in links_lines:
        if link_info[0] == "\n":
            continue
        link_info_list = link_info.split(",")

        link_id = int(link_info_list[0])
        demand = float(link_info_list[1])
        travel_fare = float(link_info_list[2])
        wait_time_cost = float(link_info_list[3])
        elastic = float(link_info_list[4])
        area = float(link_info_list[5])
        velocity = float(link_info_list[6])
        link = cls.Link(link_id, demand, travel_fare,
                        wait_time_cost, elastic, area, velocity)
        network.add_link(link)
    return network


def load_drivers(network):
    with open(driver_file_name, "r") as driver_file:
        driver_lines = driver_file.readlines()[1:]

    for driver_line in driver_lines:
        driver_info_list = driver_line.split(",")
        driver_id = int(driver_info_list[0])
        driver_num = float(driver_info_list[1])
        driver_unit_cost = float(driver_info_list[2])
        driver_run_cost = float(driver_info_list[3])
        driver_link_preference = [float(val) for val in driver_info_list[4:28]]
        driver = cls.Drivers(driver_id, driver_num,
                             driver_link_preference, driver_unit_cost, driver_run_cost)
        network.add_driver(driver)

    return network


def display_input(network):
    # display traffic demand
    link_id_list = []
    traffic_demand_list = []
    for link_id in network.links.keys():
        link = network.links[link_id]
        link_id_list.append(link_id)
        traffic_demand_list.append(link.demand)

    plt.figure(dpi=200)
    plt.plot(link_id_list, traffic_demand_list, ".-")
    plt.xlabel("Hour")
    plt.ylabel("Base Demand (hr)")
    plt.savefig("data/figure/input_demand.png")
    plt.close()


if __name__ == '__main__':
    temp_network = initiate_network()
    display_input(temp_network)
