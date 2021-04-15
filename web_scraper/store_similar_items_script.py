from .db_connector import DatabaseConnector

from .matrix_factorisation import recommend_items_for_target_item_mf


def store_similar_items():
    # Fetch the IDs
    cursor = DatabaseConnector.setup_db_connection()
    un_calculated_items_query = """
        SELECT DISTINCT T1.[item_id] FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings_Subset] T1
        LEFT JOIN [Final Year Project].[dbo].[Item_Id_To_Similar_Item_Ids] T2 ON T2.[target_item] = T1.[item_id]
        WHERE T2.[target_item] IS NULL
    """
    rows = cursor.execute(un_calculated_items_query)

    # Iterate through each of the IDs
    for target_item in list(rows):
        similar_items = recommend_items_for_target_item_mf(target_item.item_id).tolist()
        print("Length of similar items: ", len(similar_items))
        sql_text = "INSERT INTO [Final Year Project].[dbo].[Item_Id_To_Similar_Item_Ids](target_item, first_similar," \
                   "second_similar, third_similar, fourth_similar, fifth_similar, sixth_similar, seventh_similar)" \
                   "VALUES('" + str(target_item.item_id) + "'"

        for element in similar_items:
            sql_text += ", '" + str(element) + "'"

        while len(similar_items) < 7:
            sql_text += ", ''"
            similar_items.append("''")

        sql_text += ");"

        print(sql_text)
        cursor.execute(sql_text)
        cursor.commit()
