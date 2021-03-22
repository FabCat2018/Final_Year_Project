import numpy as np
import pandas as pd
from .user_item_matrix_creator import build_user_item_matrix


# MF class adapted from tutorial at:
# https://albertauyeung.github.io/2017/04/23/python-matrix-factorization.html

class MF:

    def __init__(self, user_item_matrix, latent_dimensions, learning_rate, regularisation_parameter, iterations):
        """
        Perform matrix factorization to predict empty
        entries in a matrix.
        """

        self.user_item_matrix = user_item_matrix
        self.num_users, self.num_items = user_item_matrix.shape
        self.latent_dimensions = latent_dimensions
        self.learning_rate = learning_rate
        self.regularisation_parameter = regularisation_parameter
        self.iterations = iterations

        self.user_latent_feature_matrix = np.random.normal()
        self.item_latent_feature_matrix = np.random.normal()
        self.user_bias = np.random.normal()
        self.item_bias = np.random.normal()
        self.global_bias = np.random.normal()
        self.samples = []

    def train(self, error_method):
        # Initialise user and item latent feature matrices
        self.user_latent_feature_matrix = np.random.normal(
            scale=1. / self.latent_dimensions,
            size=(self.num_users, self.latent_dimensions)
        )
        self.item_latent_feature_matrix = np.random.normal(
            scale=1. / self.latent_dimensions,
            size=(self.num_items, self.latent_dimensions)
        )

        # Initialise the biases
        self.user_bias = np.zeros(self.num_users)
        self.item_bias = np.zeros(self.num_items)
        self.global_bias = np.mean(self.user_item_matrix[np.where(self.user_item_matrix != 0)])

        # Create a list of training samples
        self.samples = [
            (i, j, self.user_item_matrix[i, j])
            for i in range(self.num_users)
            for j in range(self.num_items)
            if self.user_item_matrix[i, j] > 0
        ]

        # Perform stochastic gradient descent for number of iterations
        training_process = []
        for i in range(self.iterations):
            np.random.shuffle(self.samples)
            self.sgd()

            # Toggle mse and rmse for testing purposes
            if error_method == "rmse":
                error = self.rmse()
            else:
                error = self.mse()

            training_process.append((i, error))
            # if (i + 1) % 10 == 0:
            #     print("Iteration: %d ; error = %.4f" % (i + 1, mse))

        return training_process

    def mse(self):
        """
        A function to compute the total mean square error
        """
        xs, ys = self.user_item_matrix.nonzero()
        predicted = self.full_matrix()
        error = 0
        for x, y in zip(xs, ys):
            error += pow(self.user_item_matrix[x, y] - predicted[x, y], 2)
        return np.sqrt(error)

    # Method not from tutorial, my own work
    def rmse(self):
        """
        A function to compute the total root mean square error
        """
        xs, ys = self.user_item_matrix.nonzero()
        predicted = self.full_matrix()
        errors = list()
        for x, y in zip(xs, ys):
            errors.append(pow(self.user_item_matrix[x, y] - predicted[x, y], 2))
        return np.sqrt(np.mean(errors))

    def sgd(self):
        """
        Perform stochastic gradient descent
        """
        for i, j, r in self.samples:
            # Compute prediction and error
            prediction = self.get_rating(i, j)
            e = (r - prediction)

            # Update biases
            self.user_bias[i] += self.learning_rate * (e - self.regularisation_parameter * self.user_bias[i])
            self.item_bias[j] += self.learning_rate * (e - self.regularisation_parameter * self.item_bias[j])

            # Create copy of row of P since we need to update it but use older values for update on Q
            user_latent_feature_matrix_i = self.user_latent_feature_matrix[i, :][:]

            # Update user and item latent feature matrices
            self.user_latent_feature_matrix[i, :] += self.learning_rate * (e * self.item_latent_feature_matrix[j, :] -
                                                                           self.regularisation_parameter *
                                                                           self.user_latent_feature_matrix[i, :])
            self.item_latent_feature_matrix[j, :] += self.learning_rate * (e * user_latent_feature_matrix_i -
                                                                           self.regularisation_parameter *
                                                                           self.item_latent_feature_matrix[j, :])

    def get_rating(self, i, j):
        """
        Get the predicted rating of user i and item j
        """
        prediction = self.global_bias + self.user_bias[i] + self.item_bias[j] + self.user_latent_feature_matrix[i, :].\
            dot(self.item_latent_feature_matrix[j, :].T)
        return prediction

    def full_matrix(self):
        """
        Compute the full matrix using the resultant biases, P and Q
        """
        return self.global_bias + self.user_bias[:, np.newaxis] + self.item_bias[np.newaxis:, ] + self.\
            user_latent_feature_matrix.dot(self.item_latent_feature_matrix.T)


def recommend_items_for_target_item_mf(target_item):
    user_item_matrix = build_user_item_matrix(target_item)
    print(user_item_matrix)
    target_user = _get_target_user(user_item_matrix)
    print(target_user)
    predicted_user_item_matrix = _get_item_rating_predictions(user_item_matrix, "rmse")
    print(predicted_user_item_matrix)
    recommendations = _recommend_top_7_items_for_target_user(predicted_user_item_matrix, target_user, target_item)
    print(recommendations)
    return recommendations


# Locate target_user in user_item_matrix
def _get_target_user(user_item_matrix):
    unrated_items_for_users = user_item_matrix[user_item_matrix == 0].count(axis=0)
    return unrated_items_for_users.nlargest(1, 'first').index.values[0]


# Calculate predictions for ratings for every user-item pair and return matrix
def _get_item_rating_predictions(user_item_matrix, error_method):
    return _predict_item_ratings(user_item_matrix, latent_dimensions=2, learning_rate=0.1,
                                 regularisation_parameter=0.02, iterations=27, error_method=error_method)


def _predict_item_ratings(user_item_matrix, latent_dimensions, learning_rate, regularisation_parameter, iterations,
                          error_method):
    mf = MF(user_item_matrix.transpose().to_numpy(), latent_dimensions, learning_rate, regularisation_parameter,
            iterations)
    training_process = mf.train(error_method)
    predicted_user_item_matrix = pd.DataFrame(data=mf.full_matrix(), index=user_item_matrix.columns.values,
                                              columns=user_item_matrix.index.values).transpose()
    return predicted_user_item_matrix


# Find up to highest 7 scoring items for target_user
def _recommend_top_7_items_for_target_user(predicted_user_item_matrix, target_user, target_item):
    sorted_items_for_target_user = predicted_user_item_matrix.drop(labels=target_item).nlargest(7, target_user)
    return sorted_items_for_target_user.index.values
