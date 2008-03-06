import MySQLdb

conn = MySQLdb.connect (host = "localhost",
                        user = "smoon",
                        passwd = "smoon",
                        db = "smoon")
cursor = conn.cursor ()
cursor.execute ("select id,f_bsize,f_blocks from file_systems")
rows = cursor.fetchall ()

for row in rows:
    print row
    fs_size=(row[1]*row[2])/1024
    cursor.execute("update file_systems set f_fssize=%s where id=%s",(fs_size,row[0]))
cursor.close ()
conn.close