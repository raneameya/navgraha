import sqlite3

from pandas import DataFrame

birth_data_path = './core/data/birth_data.db'

def get_charts():
    connection = sqlite3.connect(birth_data_path)
    df = DataFrame(
        connection.execute(
            '''
            SELECT id, name, birth, place, latitude, longitude, timezone
            FROM births
            ORDER BY id
            '''
        ).fetchall(),
        columns = [
            'ID', 'Name', 'Birth', 'Place', 'Latitude',
            'Longitude', 'Timezone'
        ]
    )
    connection.close()
    df = df.round({'Latitude': 5, 'Longitude': 5})
    return df

def save_chart(name, birth, latitude, longitude, timezone, place):
    connection = sqlite3.connect(birth_data_path)
    cursor = connection.cursor()
    # Insert rows and commit. SQLite automatically inrements id as it is the primary key
    cursor.execute('''
    INSERT OR REPLACE INTO births (name, birth, latitude, longitude, timezone, place)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, birth, latitude, longitude, timezone, place))
    connection.commit()
    connection.close()
    return None   

def delete_chart(chart_id):
    connection = sqlite3.connect(birth_data_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM births WHERE id = ?", (chart_id,))
    connection.commit()
    connection.close()
    return None
