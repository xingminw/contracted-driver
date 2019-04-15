from initiate import initiate_network
from user_equilibrium import get_lower_level_solution
import matplotlib.pyplot as plt
import numpy as np


def main():
    # load the network
    network = initiate_network(reload=True)

    # plt.figure()
    # for driver_id in network.drivers.keys():
    #     drivers = network.drivers[driver_id]
    #     driver_prefer_link = drivers.links_preference
    #
    #     plt.plot(driver_prefer_link, ".-", label="Driver Class " + str(driver_id))
    #
    # plt.legend()
    # plt.xticks(np.linspace(0, 23, 24), [str(int(val + 1)) for val in np.linspace(0, 23, 24)])
    # plt.xlim([-0.5, 23.5])
    # plt.ylabel("Link-based Cost of Drivers ($)")
    # plt.xlabel("Hour")
    # plt.show()
    # exit()

    contracted_path = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
    base_solution = get_lower_level_solution(network, contracted_path, 0, [0.0, 0.0, 0.0])

    # base_demand = base_solution["base_demand"]
    # plt.figure()
    # plt.plot([val / 1000 for val in base_demand], ".-")
    # plt.ylabel("Base demand (# of trips, $10^3$)")
    # plt.xlabel("Hour")
    # plt.xticks(np.linspace(0, 23, 24), [str(int(val + 1)) for val in np.linspace(0, 23, 24)])
    # plt.xlim([-0.5, 23.5])
    # plt.show()
    # exit()

    contracted_fracs = [0, 0, 0.3]
    bonus_list = [0, 15, 20, 30, 45, 50]
    # bonus_list = [0]
    platform_benefit_list = []

    for bonus in bonus_list:
        solution = get_lower_level_solution(network, contracted_path, bonus, contracted_fracs)
        platform_benefit_list.append(solution["platform_profits"])

    plt.figure()
    plt.plot([0], [base_solution["platform_profits"]], "b.")
    plt.plot(bonus_list, platform_benefit_list, ".-")
    plt.xlabel("Additional bonus for the contraction ($)")
    plt.ylabel("Platform benefit ($)")
    plt.show()


if __name__ == '__main__':
    main()
