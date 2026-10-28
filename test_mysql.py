import pymysql

conn = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = '12345678901313zk',
    database = 'fastapi_lab'
)

cursor = conn.cursor()
cursor.execute("select * from todos;")
print(cursor.fetchall())
conn.close()