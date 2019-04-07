# This file is to solve the lower level user equilibrium using column generation
# Use the nonlinear programming package in scipy.optimize
# given the constraints for the contracted driver and the bonus for the contracted driver
from initiate import initiate_network
from scipy.optimize import minimize


def get_user_equilibrium_path_flow():

    pass


def main():
    network = initiate_network()


if __name__ == '__main__':
    main()

