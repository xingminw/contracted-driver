from initiate import initiate_network
from user_equilibrium import get_lower_level_solution
import time
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def main():
    # load the network
    network = initiate_network(reload=False)
    #
    # for link_id in network.links.keys():
    #     link = network.links[link_id]
    #     vehicle_hours = np.linspace(0, 10000, 10000)
    #     passenger_demand_list = []
    #     unit_revenue_list = []
    #     for veh_hr in tqdm(vehicle_hours):
    #         link_demand, unit_revenue = link.get_link_passenger_demand_and_unit_revenue(veh_hr)
    #         passenger_demand_list.append(link_demand)
    #         unit_revenue_list.append(unit_revenue)
    #     plt.figure()
    #     plt.plot([0, 10000], [link.demand, link.demand], "k--")
    #     plt.plot(vehicle_hours, passenger_demand_list, ".-")
    #     plt.title("Link" + str(link_id))
    #     plt.show()
    #     plt.close()
    #
    #     plt.figure()
    #     plt.plot(vehicle_hours, unit_revenue_list, ".-")
    #     plt.title("Link" + str(link_id))
    #     plt.show()
    #     plt.close()
    #
    # exit()

    # contracted_path = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
    # contracted_fracs = [0.3, 0.0, 0.0]
    # solution1 = column_generation_user_equilibrium(network, contracted_path, contracted_fracs)

    contracted_path = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0]
    # contracted_path = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
    contracted_fracs = [0.3, 0.3, 0.3]
    bonus_list = [0, 5, 10, 12, 15, 18, 20]
    platform_benefit_list = []

    for bonus in bonus_list:
        solution = get_lower_level_solution(network, contracted_path, bonus, contracted_fracs)
        platform_benefit_list.append(solution["platform_profits"])

    plt.figure()
    plt.plot(bonus_list, platform_benefit_list, ".-")
    plt.xlabel("Additional bonus for the contraction ($)")
    plt.ylabel("Platform benefit ($)")
    plt.show()


if __name__ == '__main__':
    main()
