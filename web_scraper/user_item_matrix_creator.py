import pandas as pd
from .db_connector import DatabaseConnector


# Create dataframe containing all users who rated target_item, and each item rated by said users
# (much smaller pivot table)
def build_user_item_matrix(target_item):
    cursor = DatabaseConnector.setup_db_connection()
    user_ids = _find_users_who_rated_target_item(cursor, target_item)

    # If item is not rated by any user then return empty matrix
    if len(user_ids) == 0:
        return pd.DataFrame()

    database_results = list()
    for user in user_ids:
        database_results.extend(_find_items_rated_by_user(cursor, user))

    results_dataframe = pd.DataFrame(data=database_results, columns=['user_id', 'item_id', 'rating'])

    user_item_matrix = results_dataframe.pivot_table(index='item_id', columns='user_id', values='rating', fill_value=0)
    return user_item_matrix


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

# endregion
