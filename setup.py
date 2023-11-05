import subprocess
import sqlite3



def SeedDB():
    dbName = "BankAppDb.sqlite3"
    con = sqlite3.connect(dbName)
    cur = con.cursor()

    pass1 = "squarepants"
    pass2 = "redqueen"

    f1 = "Bob"
    l1 = "Sponge"
    s1 = 100000000001
    
    f2 = "Alice"
    l2 = "Queen"
    s2 = "100000000002"

    sql1 = f"INSERT INTO BankApp_Customer (Id, firstname, lastname, SocSecNumber, password, FailedLoginCount, IsBlocked, is_authenticated, is_anonymous) VALUES (1, '{f1}', '{l1}', '{s1}', '{pass1}', 0, False, True, False);"
    sql2 = f"INSERT INTO BankApp_Customer (Id, firstname, lastname, SocSecNumber, password, FailedLoginCount, IsBlocked, is_authenticated, is_anonymous) VALUES (2, '{f2}', '{l2}', '{s2}', '{pass2}', 0, False, True, False);"

    cur.execute(sql1)
    cur.execute(sql2)

    con.commit()
    con.close()



if __name__ == "__main__":
    SeedDB()