# order_flow.py

import numpy as np

def generate_orders(lambda_rate):
    n_orders = np.random.poisson(lambda_rate)
    return np.random.choice(['buy', 'sell'], size=n_orders)
