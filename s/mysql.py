import MySQLdb

db = MySQLdb.connect("localhost","share","share","share")

cursor = db.cursor()

data = cursor.execute("insert into a (a) values ('1')")
db.commit()


print(data)



