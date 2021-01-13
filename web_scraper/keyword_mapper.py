from .db_connector import DatabaseConnector as dbConnector


def map_id_to_keyword(item_id):
    cursor = dbConnector.setup_db_connection()
    find_keyword_query = """
        SELECT [keywords]
        FROM [Final Year Project].[dbo].[Item_Id_To_Keywords]
        WHERE [item_id] = '{item_id}'
    """.format(item_id=item_id)

    print(find_keyword_query)
    cursor.execute(find_keyword_query)

    rows = cursor.fetchall()
    return rows[0].keywords


def map_keyword_to_id(keyword):
    cursor = dbConnector.setup_db_connection()

    space_separated_keywords = keyword.split()
    find_item_id_query = """
        SELECT [item_id]
        FROM [Final Year Project].[dbo].[Item_Id_To_Keywords]
        WHERE [keywords] LIKE '%{keyword}%'
    """.format(keyword=space_separated_keywords[0])

    for i in range(1, len(space_separated_keywords)):
        find_item_id_query += " AND [keywords] LIKE '%" + space_separated_keywords[i] + "%'"

    cursor.execute(find_item_id_query)
    rows = cursor.fetchall()

    row_count = len(rows)
    if row_count > 1:
        raise Exception("Too many matching items")
    elif row_count < 1:
        raise Exception("No matching items")
    else:
        return rows[0].item_id
