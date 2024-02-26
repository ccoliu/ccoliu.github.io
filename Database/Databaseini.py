import mysql.connector

cnx = mysql.connector.connect(
    host="localhost",
)

cursor = cnx.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")

cnx.close()