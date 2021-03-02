import numpy as np
import pandas as pd
import pyodbc

_conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-U3ATH6F;Database=Final Year Project;Trusted_Connection=yes;")


class DatabaseConnector:

    # Setup DB connection
    @staticmethod
    def setup_db_connection():
        cursor = _conn.cursor()
        return cursor

# Adapted from tutorial at:
# https://towardsdatascience.com/user-user-collaborative-filtering-for-jokes-recommendation-b6b1e4ec8642


# Create dataframe containing all users, and each item rated by said users (much smaller pivot table)
def build_user_item_matrix(target_item):
    cursor = DatabaseConnector.setup_db_connection()
    user_ids = _find_users_who_rated_target_item(cursor, target_item)

    database_results = list()
    for user in user_ids:
        database_results.extend(_find_items_rated_by_user(cursor, user))

    results_dataframe = pd.DataFrame(data=database_results, columns=['user_id', 'item_id', 'rating'])

    user_item_matrix = results_dataframe.pivot_table(index='item_id', columns='user_id', values='rating', fill_value=0)
    return user_item_matrix


# Collate items from each of k users which target_user has not yet selected and determine (up to) highest 7 to recommend
def recommend_items_for_target_item(target_item):
    # Create user_item pivot table, getting first user as target_user
    user_item_matrix = build_user_item_matrix(target_item)
    target_user_name = user_item_matrix.iloc[:, 0].name

    # Calculate similarity for each user
    similarity_matrix = _calculate_pearson_similarity_for_matrix(user_item_matrix)

    # Normalise user_item pivot_table
    normalised_user_item_matrix = _normalisation(user_item_matrix)

    # If more than 5 similar users, take most similar 5
    if len(similarity_matrix.columns) > 5:
        most_similar_users = _find_5_most_similar_users_to_target_user(similarity_matrix, target_user_name)
    else:
        most_similar_users = user_item_matrix

    # Find items which target_user has not rated yet
    possible_recommendations = user_item_matrix[user_item_matrix[target_user_name] == 0].index.values

    # Get normalised ratings for each similar user, as well as each user's similarity to target_user
    neighbour_rating = normalised_user_item_matrix.loc[possible_recommendations][most_similar_users]
    neighbour_similarity = similarity_matrix.loc[target_user_name].loc[most_similar_users]

    # Score items
    item_scores = _score_items(neighbour_rating, neighbour_similarity, user_item_matrix, target_user_name)

    # Get up to top 7 items by score
    recommended_items = _get_top_7_items_by_score(item_scores)
    return recommended_items


# region Private Functions

# Get users who have rated target item
def _find_users_who_rated_target_item(cursor, target_item):
    get_users_for_item_query = """
        SELECT [user_id]
        FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings_Subset]
        WHERE [item_id] = '{target_item}'
    """.format(target_item=target_item)
    print(get_users_for_item_query)
    cursor.execute(get_users_for_item_query)

    user_ids = list()
    for user in cursor.fetchall():
        user_ids.append(user.user_id)

    return user_ids


def _find_items_rated_by_user(cursor, user):
    get_items_for_user_query = """
        SELECT [user_id], [item_id], [rating]
        FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings_Subset]
        WHERE [user_id] = '{user}' 
    """.format(user=user)
    print(get_items_for_user_query)
    cursor.execute(get_items_for_user_query)

    results = list()
    for row in cursor.fetchall():
        results.append({"user_id": row.user_id, "item_id": row.item_id, "rating": float(row.rating)})

    return results


def _normalisation(matrix):
    matrix_mean = matrix.mean(axis=0)
    return matrix.subtract(matrix_mean, axis='columns')


def _calculate_pearson_similarity_for_matrix(matrix):
    return matrix.corr(method="pearson")


def _find_5_most_similar_users_to_target_user(similarity_matrix, target_user_name):
    all_similar_users = similarity_matrix.drop([target_user_name], axis=0)
    five_most_similar_users = all_similar_users.nlargest(5, [target_user_name])
    return five_most_similar_users.index.values


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
