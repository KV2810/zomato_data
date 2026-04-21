import mysql.connector as cn

conn=cn.connect(username="root",port="3306",password="actowiz",database="billboard_db")
con=conn.cursor()

query="""select * from billboards """
con.execute(query)
raws=con.fetchall()
for f in raws:
    print(f)



