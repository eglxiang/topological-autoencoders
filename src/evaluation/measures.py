'''
Utility functions for calculating dimensionality reduction quality
measures for evaluating the latent space.
'''


import numpy as np


def pairwise_distances(X):
    '''
    Calculates pairwise distance matrix of a given data matrix and
    returns said matrix.
    '''

    D = np.sum((X[None, :] - X[:, None])**2, -1)**0.5
    return D


def stress(X, Z):
    '''
    Calculates the stress measure between the data space `X` and the
    latent space `Z`.
    '''

    X = pairwise_distances(X)
    Z = pairwise_distances(Z)

    sum_of_squared_differences = np.square(X - Z).sum()
    sum_of_squares = np.square(Z).sum()

    return np.sqrt(sum_of_squared_differences / sum_of_squares)


def RMSE(X, Z):
    '''
    Calculates the RMSE measure between the data space `X` and the
    latent space `Z`.
    '''

    X = pairwise_distances(X)
    Z = pairwise_distances(Z)

    n = X.shape[0]
    sum_of_squared_differences = np.square(X - Z).sum()
    return np.sqrt(sum_of_squared_differences / n**2)

def get_neighbours_and_ranks(X, k):
    '''
    Calculates the neighbourhoods and the ranks of a given space `X`,
    and returns the corresponding tuple. An additional parameter $k$,
    the size of the neighbourhood, is required.
    '''

    X = pairwise_distances(X)

    # Warning: this is only the ordering of neighbours that we need to
    # extract neighbourhoods below. The ranking comes later!
    X_ranks = np.argsort(X, axis=-1, kind='stable')

    # Extract neighbourhoods.
    X_neighbourhood = X_ranks[:, 1:k+1]

    # Convert this into ranks (finally)
    X_ranks = X_ranks.argsort(axis=-1, kind='stable')

    return X_neighbourhood, X_ranks


def trustworthiness(X, Z, k):
    '''
    Calculates the trustworthiness measure between the data space `X`
    and the latent space `Z`, given a neighbourhood parameter `k` for
    defining the extent of neighbourhoods.
    '''

    X_neighbourhood, X_ranks = get_neighbours_and_ranks(X, k)
    Z_neighbourhood, Z_ranks = get_neighbours_and_ranks(Z, k)

    result = 0.0

    # Calculate number of neighbours that are in the $k$-neighbourhood
    # of the latent space but not in the $k$-neighbourhood of the data
    # space.
    for row in range(X_ranks.shape[0]):
        missing_neighbours = np.setdiff1d(
            Z_neighbourhood[row],
            X_neighbourhood[row]
        )

        for neighbour in missing_neighbours:
            result += (X_ranks[row, neighbour] - k)

    n = X.shape[0]
    return 1 - 2 / (n * k * (2 * n - 3 * k - 1) ) * result


def continuity(X, Z, k):
    '''
    Calculates the continuity measure between the data space `X` and the
    latent space `Z`, given a neighbourhood parameter `k` for setting up
    the extent of neighbourhoods.

    This is just the 'flipped' variant of the 'trustworthiness' measure.
    '''

    # Notice that the parameters have to be flipped here.
    return trustworthiness(Z, X, k)

def neighbouhood_loss(X, Z, k):
    '''
    Calculates the neighbourhood loss quality measure between the data
    space `X` and the latent space `Z` for some neighbourhood size $k$
    that has to be pre-defined.
    '''

    X_neighbourhood, _ = get_neighbours_and_ranks(X, k)
    Z_neighbourhood, _ = get_neighbours_and_ranks(Z, k)

    result = 0.0
    n = X.shape[0]

    for row in range(n):
        shared_neighbours = np.intersect1d(
            X_neighbourhood[row],
            Z_neighbourhood[row]
        )

        result += len(shared_neighbours) / k

    return 1.0 - result / n


np.random.seed(42)
X = np.random.normal(size=(10, 2))
Z = np.random.normal(size=(10, 2))

print(stress(X, Z))
print(RMSE(X, Z))
print(trustworthiness(X, Z, 1))
print(continuity(X, Z, 1))
print(neighbouhood_loss(X, Z, 5))