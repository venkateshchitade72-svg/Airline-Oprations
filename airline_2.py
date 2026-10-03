import os
import platform
import mysql.connector
import datetime
import joblib
import streamlit

mydb=mysql.connector.connect(host="localhost",user="root",passwd=os.getenv("AIR_DB_PASSWORD", ""),database="air")
mycursor=mydb.cursor()
print("PROJECT BY -")
print("              VENKATESH CHITADE                    ")

print("\\\\\ WELCOME TO VENKATESH AIRLINES /////")

print("--------------------------------------------------------------------")
print("successfully connected to mysql")
print("====================================================================")

def registercust():
    L=[]
    custno=int(input('Enter customer no='))
    L.append(custno)
    name=input('Enter name:')
    L.append(name)
    address=input('Enter address:')
    L.append(address)
    journey_date=input('Enter date of journey[dd/mm/yy]:')
    L.append(journey_date)
    source=input('Enter source:')
    L.append(source)
    destination=input('Enter destination:')
    L.append(destination)
    cust=(L)
    sql='insert into pdata(custno,name,address,journey_date,source, destination)  values(%s,%s,%s,%s,%s,%s)'
    mycursor.execute(sql,cust)
    print("Successfully inserted ")
    mydb.commit()

def add_classtype():
    c1=mydb.cursor()
    L=[]
    sno=int(input("enter serial number:"))
    L.append(sno)
    itemname=input("enter name of class type")
    L.append(itemname)
    rate=int(input("enter price per ticket"))
    L.append(rate)
    ct=(L)
    sql="insert into classtype(sno,itemname,rate)values(%s,%s,%s)"
    c1.execute(sql,ct)
    mydb.commit()
    print("Record inserted in class")

    print("Do you want to see class type available : Enter 1 for yes :")
    ch=int(input("Enter your choice:"))
    if ch==1:
        sql="select * from classtype"
        mycursor.execute(sql)
        rows=mycursor.fetchall()
        for x in rows:
            print(x)

def delete():
    print("Select delete criteria")
    print("1 for Customer data")
    print("2 for Classtype")
    print("3 for Food")
    ch=int(input("Please Enter choice 1-3: "))
    if ch==1:
        s=int(input("Enter Customer id: "))
        sql=("delete from pdata where custno=%s;")
        wal=(s,)
        mycursor.execute(sql,wal)
        mydb.commit()
        print("Customer details successfully deleted")
    elif ch==2:
        s=int(input("Enter class type serial number: "))
        sql=("delete from classtype where sno=%s;")
        wal=(s,)
        mycursor.execute(sql,wal)
        mydb.commit()
        print("Classtype details successfully deleted")
    elif ch==3:
        s=int(input("Enter food serial number: "))
        sql=("delete from foodinfo where sno=%s;")
        wal=(s,)
        mycursor.execute(sql,wal)
        mydb.commit()
        print("Food details successfully deleted")

def update():
    print("Select update criteria")
    print("1 for Customer data")
    print("2 for Classtype")
    print("3 for Food")
    ch=int(input("Please Enter choice 1-3: "))
    if ch==1:
        s=int(input("Enter Customer number: "))
        name=input("Enter new customer name: ")
        address=input("Enter new address: ")
        journey_date=input("Enter new date of journey: ")
        source=input("Enter new souce: " )
        destination=input("Enter new destination: ")
        sql="update pdata set name='{}',address='{}',journey_date='{}',source='{}',destination='{}' where custno={}".format(name,address,journey_date,source,destination,s)
        mycursor.execute(sql)
        mydb.commit()
        print("Customer details successfully updated")
    elif ch==2:
        s=int(input("Enter class type serial number: "))
        itemname=input("Enter new classtype: ")
        rate=int(input("Enter new price per ticket"))
        sql="update classtype set itemname='{}',rate={} where sno={}".format(itemname,rate,s)
        mycursor.execute(sql)
        mydb.commit()
        print("Classtype details successfully updated")
    elif ch==3:
        s=int(input("Enter food serial number: "))
        itemname=input("Enter new fooditem name: ")
        price=int(input("Enter new price per packet(Inr): "))
        sql="update foodinfo set itemname='{}',price={} where sno={}".format(itemname,price,s)
        mycursor.execute(sql)
        mydb.commit()
        print("Food details successfully updated")

def ticketprice():
    L=[]
    cno=int(input('Enter custoner no='))
    L.append(cno)
    print('We have the following rooms for you:-')
    print('1. type First class--->rs 6000 PN\-')
    print('2. type Business class--->rs 4000 PN\-')
    print('3. type Economy class--->rs 2000 PN\-')
    x=int(input('Enter your choice:'))
    n=1
    if x==1:
        print('you have opted First class.')
        s=6000*n
        L.append(s)
    elif x==2:
        print('you have opted Business class.')
        s=4000*n
        L.append(s)
    elif x==3:
        print('you have opted Economy class.')
        s=2000*n
        L.append(s)
    else:
        print('Please select a class type.')
        print('Ticket charge is =',s,'\n')
        print('Extra luggage charge 100 rs per kg')

    y=int(input('Enter  weight of extra luggage:'))
    z=y*100
    L.append(z)
    tkt=(L)
    print('Totalbill:',s+z,'\n')
    g_tot=s+z
    L.append(g_tot)
    sql="insert into ticket (custno,tkt,luggage,total) values (%s,%s,%s,%s)"
    mycursor.execute(sql,tkt)
    print("Successfully inserted ")
    mydb.commit()

def dis():
    custno=int(input("Enter the customer number whose bill to be viewed : "))
    sql="Select pdata.custno, pdata.name, pdata.address, pdata.source, pdata.destination, ticket.tkt, ticket.luggage, total from pdata INNER JOIN ticket ON pdata.custno=ticket.custno and ticket.custno = %s"
    rl=[custno]
    mycursor.execute(sql,rl)
    res=mycursor.fetchall()
    for x in res:
        print(x)

def dispall():
    sql="Select pdata.custno, pdata.name, pdata.address, pdata.source, pdata.destination, ticket.tkt, ticket.luggage, total from pdata INNER JOIN ticket ON pdata.custno=ticket.custno"
    mycursor.execute(sql)
    res=mycursor.fetchall()
    print("The Customer details are as follows : ")

    for x in res:
        print(x)
def foodinfo():
    L=[]
    sno =int(input("Enter the serial number:"))
    L.append(sno)
    itemname= input('Enter food item: ')
    L.append(itemname)
    price=int(input("Enter Rate per pack(Inr):"))
    L.append(price)

    food=(L)
    sql='insert into foodinfo(sno,itemname,price) values(%s,%s,%s)'
    mycursor.execute(sql,food)
    print("Successfully inserted ")
    mydb.commit()

def Menuset():
    print('Enter 1: To enter customer data.')
    print('Enter 2: For ticketamount.')
    print('Enter 3: To add and view classtype')
    print('Enter 4: Display customerwise Details.')
    print('Enter 5: Display All Details.')
    print('Enter 6: Add Fooditem detail')
    print('Enter 7: Update details')
    print('Enter 8: Delete details')
    print('Enter 9: Exit')
    print("-------------------------------------------------------------")
    userinput=int(input('Enter your choice:'))
    if userinput==1:
        registercust()
    elif userinput==2:
        ticketprice()
    elif userinput==3:
        add_classtype()
    elif userinput==4:
        dis()
    elif userinput==5:
        dispall()
    elif userinput==6:
        foodinfo()
    elif userinput==7:
        update()
    elif userinput==8:
        delete()
    elif userinput==9:
        quit()
    else:
        print('Enter correct choice.')
Menuset()
def runagain():
    runagn=input('\nWant to run again? y/n:')
    while runagn=='y':
        if platform.system=='windows':
            print(os.system('cls'))
        else:
            print(os.system('clear'))
        Menuset()
        runagn=input('\nWant to run again? y/n:')
runagain()
