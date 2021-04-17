from .db_connector import DatabaseConnector as dbConnector


def get_similar_items(target_item):
    cursor = dbConnector.setup_db_connection()
    get_recommendations_query = """
        SELECT [first_similar], [second_similar], [third_similar], [fourth_similar], [fifth_similar],
            [sixth_similar], [seventh_similar] 
        FROM [Final Year Project].[dbo].[Item_Id_To_Similar_Item_Ids] 
        WHERE [target_item] = '{target_item}'
    """.format(target_item=target_item)

    cursor.execute(get_recommendations_query)

    similar_item_ids = list(cursor.fetchone())
    return similar_item_ids
