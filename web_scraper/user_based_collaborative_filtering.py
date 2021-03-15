import numpy as np
import pandas as pd
from .user_item_matrix_creator import build_user_item_matrix


# Adapted from tutorial at:
# https://towardsdatascience.com/user-user-collaborative-filtering-for-jokes-recommendation-b6b1e4ec8642


# Collate items from each of k users which target_user has not yet selected and determine (up to) highest 7 to recommend
def recommend_items_for_target_item_cf(target_item):
    # Create user_item pivot table, getting first user as target_user
    user_item_matrix = build_user_item_matrix(target_item)
    target_user_name = user_item_matrix.iloc[:, 0].name
    return _recommend_top_7_items_for_users(user_item_matrix, target_user_name)


# Recommend up to 7 items based on score
def _recommend_top_7_items_for_users(user_item_matrix, target_user_name):
    item_scores = _score_items_for_target_user_cf(user_item_matrix, target_user_name)
    recommended_items = _get_top_7_items_by_score(item_scores)
    return recommended_items


# Score items for a target_user
def _score_items_for_target_user_cf(user_item_matrix, target_user_name):
    # Calculate similarity for each user
    similarity_matrix = _calculate_pearson_similarity_for_matrix(user_item_matrix)

    # Normalise user_item pivot_table
    normalised_user_item_matrix = _normalisation(user_item_matrix)

    # If more than 5 similar users, take most similar 5
    if len(similarity_matrix.columns) > 20:
        most_similar_users = _find_20_most_similar_users_to_target_user(similarity_matrix, target_user_name)
    else:
        most_similar_users = user_item_matrix

    # Find items which target_user has not rated yet
    possible_recommendations = user_item_matrix[user_item_matrix[target_user_name] == 0].index.values

    # Get normalised ratings for each similar user, as well as each user's similarity to target_user
    neighbour_rating = normalised_user_item_matrix.loc[possible_recommendations][most_similar_users]
    neighbour_similarity = similarity_matrix.loc[target_user_name].loc[most_similar_users]

    # Score items
    item_scores = _score_items(neighbour_rating, neighbour_similarity, user_item_matrix, target_user_name)
    return item_scores


# region Private Helper Functions

# Adjust ratings by each user's average rating
def _normalisation(matrix):
    matrix_mean = matrix.mean(axis=0)
    return matrix.subtract(matrix_mean, axis='columns')


def _calculate_pearson_similarity_for_matrix(matrix):
    return matrix.corr(method="pearson")


def _find_20_most_similar_users_to_target_user(similarity_matrix, target_user_name):
    all_similar_users = similarity_matrix.drop([target_user_name], axis=0)
    twenty_most_similar_users = all_similar_users.nlargest(20, [target_user_name])
    return twenty_most_similar_users.index.values


def _score_items(neighbour_rating, neighbour_similarity, user_item_matrix, target_user_name):
    active_user_mean_rating = np.mean(user_item_matrix.loc[:, target_user_name])
    neighbour_rating_transpose = neighbour_rating.transpose()
    score = np.dot(neighbour_similarity, neighbour_rating_transpose) + active_user_mean_rating
    data = score.reshape(1, len(score))
    columns = neighbour_rating_transpose.columns
    return pd.DataFrame(data=data, columns=columns)


def _get_top_7_items_by_score(item_scores):
    if len(item_scores.columns) < 7:
        return item_scores.columns.values
    else:
        sorted_scores = item_scores.transpose().nlargest(7, [0])
        return sorted_scores.transpose().columns.values

# endregion
