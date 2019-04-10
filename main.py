from initiate import initiate_network
from user_equilibrium import column_generation_user_equilibrium


def main():
    # load the network
    network = initiate_network(reload=False)
    #
    # for link_id in network.links.keys():
    #     link = network.links[link_id]
    #
    #     vehicle_hours = np.linspace(6000, 6001, 10).tolist()
    #     cost_list = []
    #     for vehicle_hour in vehicle_hours:
    #         cost_list.append(link.get_link_revenue_integral(vehicle_hour))
    #
    #     cost_list = [- val for val in cost_list]
    #     plt.figure()
    #     plt.plot(vehicle_hours, cost_list, ".-")
    #     # plt.ylim([None, 0])
    #     plt.show()
    # get the user equilibrium using column generation
    # path_set_dict = {0: [[0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    #                      [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]]}
    #
    # objective_function_list = []
    # for idx in range(6000):
    #     cost1 = get_path_distribution_cost(np.array([6000 - idx, idx]), path_set_dict, network)
    #     objective_function_list.append(cost1)
    #
    # x1 = 6000 - np.argmin(objective_function_list)
    # x2 = np.argmin(objective_function_list)
    # print([x1, x2])
    # link_hours = model.get_link_vehicle_hours(path_set_dict, [x1, x2])
    # print(link_hours)
    # link_revenue = network.get_link_revenue_list(link_hours)
    #
    # for path in path_set_dict[0]:
    #     drivers = network.drivers[0]
    #     cost = drivers.get_path_cost(path)
    #     revenue = np.sum(np.array(path) * np.array(link_revenue))
    #     profit = revenue - cost
    #     print(cost, revenue, profit)
    contracted_path = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    contracted_fracs = [0.3, 0.2, 0.0]
    column_generation_user_equilibrium(network, contracted_path, contracted_fracs)


if __name__ == '__main__':
    main()
