import mysql.connector

mydb = mysql.connector.connect(
    host="34.126.95.175",
    port="3306",
    user="root",
    passwd="lengmaynut123",
    database="Project"
)

# print(mydb)    # Check Connection

mycursor = mydb.cursor()
#mycursor.execute("CREATE DATABASE hiewKaoDB") # Create Database
#chef_name, menu_name, ingredient, step, link_vdo="", picture=""
#sql = "CREATE TABLE MenuList (food_id TEXT NOT NULL, chef_name TEXT NOT NULL, menu_name TEXT NOT NULL, usage_ingredient TEXT NOT NULL, step TEXT NOT NULL, price INT NOT NULL, vdo TEXT, picture TEXT, rate TEXT)"
sql = "ALTER TABLE Refrigerator DROP Owner_ID"

"""
sqlFormula = "INSERT INTO Refrigerator (Refrigerator_ID, Remaining_Ingredient, Remaining_Number, Unit) VALUES (%s, %s, %s, %s)" 

sql = [("RE0001", "Egg", 10, "units"),
    ("RE0001", "Rice", 300, "grams"),
    ("RE0001", "Pork Chop", 500, "grams"),
    ("RE0001", "Chicken Breast", 500, "grams"), 
    ("RE0001", "Milk", 400, "litre"),]


sql = [("RE0002", "Tomato", 3, "units"),
    ("RE0002", "Salmon", 2, "units"),
    ("RE0002", "Rice", 500, "grams"),]

sql = [(""RE0003", "Lobster", 3, "units"),
    ("RE0003", "Catfish", 5, "units"),
    ("RE0003", "Chocolate", 100, "grams"),
    ("RE0003", "Rice", 300, "grams"),]
"""

# egg porkchop badycorn
mycursor.execute(sql)

mydb.commit()