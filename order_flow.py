import numpy as np

def generate_orders(lam):
    num_orders = np.random.poisson(lam)
    return np.random.choice(['buy', 'sell'], size=num_orders)
