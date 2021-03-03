from collections import Counter

from .db_connector import DatabaseConnector as dbConnector


# Finds top 7 items rated highly by users who rated target_item
def find_similar_items_to_target_item(target_item):
    cursor = dbConnector.setup_db_connection()

    # Get users who have rated specified item
    users = _find_users_who_rated_target_item(cursor, target_item)

    # Get list of all items rated by all relevant users
    all_items_rated_by_users = list()
    for user in users:
        all_items_rated_by_users.extend(_find_items_liked_by_user(cursor, user, target_item))

    # Count number of users (occurrences) for common items in item_list
    counter = Counter(all_items_rated_by_users)

    # Create unique item_id set with default rank 0
    unique_items = set(all_items_rated_by_users)

    # Create list of items with associated recommendation rank
    items_with_rank = list()
    for item in unique_items:
        rank = _calculate_item_rank(cursor, item, counter.get(item), users)
        items_with_rank.append({'item_id': item, 'rank': rank})

    sorted_items_with_rank = sorted(items_with_rank, key=lambda x: x['rank'], reverse=True)

    recommendations = list()
    for scored_item in sorted_items_with_rank[:7]:
        recommendations.append(scored_item['item_id'])

    return recommendations


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


# Check which other items the user has rated
def _find_items_liked_by_user(cursor, user, target_item):
    get_items_for_user_query = """
        SELECT [item_id]
        FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings_Subset]
        WHERE [user_id] = '{user_id}' AND [item_id] != '{item_id}'
    """.format(user_id=user, item_id=target_item)
    cursor.execute(get_items_for_user_query)

    item_ids = list()
    for item in cursor.fetchall():
        item_ids.append(item.item_id)

    return item_ids


# Calculate rank of item based on occurrences and average rating from selected users
def _calculate_item_rank(cursor, item, occurrences, users):
    total_rating = 0

    ratings_for_item_by_selected_users_query = """
        SELECT [user_id], [rating]
        FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings_Subset]
        WHERE [item_id] = '{item_id}'
    """.format(item_id=item)
    cursor.execute(ratings_for_item_by_selected_users_query)
    rows = cursor.fetchall()

    for user in users:
        item_rating = rows['user_id' == user].rating
        if not item_rating:
            total_rating += 0
        else:
            total_rating += float(item_rating)

    return total_rating / len(users) * occurrences
