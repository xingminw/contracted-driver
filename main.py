from initiate import initiate_network
from user_equilibrium import column_generation_user_equilibrium


def main():
    # load the network
    network = initiate_network(reload=False)

    # get the user equilibrium using column generation
    contracted_path = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    contracted_fracs = [0.8, 0.2, 0.1]

    column_generation_user_equilibrium(network, contracted_path, contracted_fracs)


if __name__ == '__main__':
    main()
