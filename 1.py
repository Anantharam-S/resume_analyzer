import mysql.connector

# Establish a connection to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="resume_analyzer"  # Replace with your actual database name
)

# Check if the connection is successful
if conn.is_connected():
    print("Connected to MySQL database")
print("hi")
# Close the connection
conn.close()
