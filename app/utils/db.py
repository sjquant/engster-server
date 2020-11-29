async def fetch_all(query):
    """
    Fetch data from database in formatted form
    """
    data = await query.gino.all()
    columns = [str(each.name) for each in query.columns]
    data = [dict(zip(columns, each)) for each in data]
    return data


async def fetch_one(query):
    """
    get data from database in formatted form
    """
    data = await query.gino.first()
    data = {str(col.name): value for col, value in zip(query.columns, data)}
    return data
