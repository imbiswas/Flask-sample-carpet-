import mysql.connector
class databse(object):
    def __init__(self):
        self.material()
    def material(self):
        materials=[]
        db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                            user="root",         # your username
                            passwd="1234",  # your password
                            db="carpet",
                            )        # name of the data base


        cur = db.cursor()
        cur.execute("SELECT * FROM carpet.materials;")

        for row in cur.fetchall():
            materials.append(row[1])

        db.close()
        return (materials)

