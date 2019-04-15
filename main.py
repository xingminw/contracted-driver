from initiate import initiate_network
from user_equilibrium import get_lower_level_solution
import matplotlib.pyplot as plt
import numpy as np


def main():
    # load the network
    network = initiate_network(reload=False)

    contracted_path = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
    base_solution = get_lower_level_solution(network, contracted_path, 0, [0.0, 0.0, 0.0])
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
    plt.xticks(np.linspace(0, 23, 24), [str(int(val)) for val in np.linspace(0, 23, 24)])
    plt.show()


if __name__ == '__main__':
    main()
