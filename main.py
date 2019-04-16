from initiate import initiate_network
from user_equilibrium import get_lower_level_solution
import matplotlib.pyplot as plt
import numpy as np


def main():
    # load the network
    network = initiate_network(reload=False)

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

    contracted_path = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    # contracted_path = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    base_solution = get_lower_level_solution(network, contracted_path, 0, [0.0, 0.0, 0.0])
    # exit()
    # plt.figure()
    # plt.plot(base_solution["demand_elasticity"], ".-")
    # plt.xlim([-0.5, 23.5])
    # plt.ylabel("Ela ($)")
    # plt.xlabel("Hour")
    # plt.show()
    # exit()

    # base_demand = base_solution["base_demand"]
    # plt.figure()
    # plt.plot([val / 1000 for val in base_demand], ".-")
    # plt.ylabel("Base demand (# of trips, $10^3$)")
    # plt.xlabel("Hour")
    # plt.xticks(np.linspace(0, 23, 24), [str(int(val + 1)) for val in np.linspace(0, 23, 24)])
    # plt.xlim([-0.5, 23.5])
    # plt.show()
    # exit()

    contracted_fracs = [0.0, 0.0, 0.3]
    # bonus_list = [30]
    bonus_list = [36, 38, 40, 42]
    platform_benefit_list = []
    platform_revenue_list = []
    realized_demand_list = []
    contracted_driver_fracs = [[], [], []]

    for bonus in bonus_list:
        solution = get_lower_level_solution(network, contracted_path, bonus, contracted_fracs)
        platform_benefit_list.append(solution["platform_profits"])
        platform_revenue_list.append(solution["platform_revenue"])
        realized_demand_list.append(solution["realized_demand"])
        ratio_list = solution["contract_profit_ratio"]
        contracted_driver_fracs[0].append(ratio_list[0])
        contracted_driver_fracs[1].append(ratio_list[1])
        contracted_driver_fracs[2].append(ratio_list[2])

    plt.figure()
    for idx in range(len(contracted_driver_fracs)):
        plt.plot(bonus_list, contracted_driver_fracs[idx], ".-", label="Driver Class " + str(idx))

    plt.xlabel("Bonus ($)")
    plt.ylabel("Proportion of Contract Driver")
    plt.legend()
    plt.show()

    plt.figure()
    # plt.plot([0], [base_solution["platform_profits"]], "b.")
    plt.plot(bonus_list, [val / 1000 for val in platform_revenue_list], ".-", label="Platform Revenue")
    plt.plot(bonus_list, [val / 1000 for val in platform_benefit_list], ".-", label="Platform Profit")
    plt.xlabel("Additional bonus for the contraction ($)")
    plt.ylabel("Platform benefit (k$)")
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(base_solution["base_demand"], label="Base demand")
    for idx in range(len(bonus_list))[::2]:
        bonus_val = bonus_list[idx]
        plt.plot(realized_demand_list[idx], ".-", label="Bonus=" + str(bonus_val) + "$")
    plt.ylabel("Passenger demand (# of trips)")
    plt.xlabel("Hour")
    plt.xticks(np.linspace(0, 23, 24), [str(int(val + 1)) for val in np.linspace(0, 23, 24)])
    plt.xlim([-0.5, 23.5])
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
