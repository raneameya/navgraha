import sqlite3

connection = sqlite3.connect('./core/data/birth_data.db')

cursor = connection.cursor()

# Create birth data database
cursor.execute('''
CREATE TABLE IF NOT EXISTS births (
    id INTEGER PRIMARY KEY,
    name TEXT,
    birth TEXT,
    latitude REAL,
    longitude REAL,
    timezone TEXT,
    place TEXT
)
''')

# Define seed data
seed_data = [
    (1, 'Anandmayi Maa', '1896-05-01 03:45:00', 22.780757, 91.083451, 'Asia/Dhaka', 'Kheore'),
    (2, 'Jiddu Krishnamurti', '1895-05-12 00:30:00', 13.5668, 78.47611, 'Asia/Kolkata', 'Madanapalle'),
    (3, 'Ramana Maharishi', '1879-12-30 01:00:00', 9.61228, 78.32321, 'Asia/Kolkata', 'Tiruchuli'),
    (4, 'Osho', '1931-12-11 17:13:00', 23.144975740327727, 78.34920336707333, 'Asia/Kolkata', 'Kuchwada'),
    (5, 'PVR Narasimha Rao', '1970-04-04 17:50:40', 16.14196, 81.13644, 'Asia/Kolkata', 'Machilipatnam'),
    (6, 'Prash Trivedi', '1975-05-21 00:30:04', 17.90802, 77.51524, 'Asia/Kolkata', 'Bidar')
]

# Insert rows and commit
cursor.executemany("""
INSERT OR REPLACE INTO births (id, name, birth, latitude, longitude, timezone, place)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", seed_data)
connection.commit()

# Test print
cursor.execute("SELECT * FROM births")
rows = cursor.fetchall()
print(rows)

connection.close()
