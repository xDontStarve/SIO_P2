import mysql.connector as db


if __name__ == "__main__":
    sql = db.connect(user="root", password="root", host="127.0.0.1", database="project01")
    cursor = sql.cursor()

    cursor.execute("SELECT ID FROM movies")
    rows = cursor.fetchall()

    print(rows)
