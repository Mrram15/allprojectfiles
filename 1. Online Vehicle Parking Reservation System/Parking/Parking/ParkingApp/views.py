from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import pymysql
from datetime import datetime

global username

def ViewHistory(request):
    if request.method == 'GET':
        global username
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Parking ID</th><th><font size="3" color="black">Area ID</th>'
        output+='<th><font size="3" color="black">Slot No</th><th><font size="3" color="black">Entry Time</th>'
        output+='<th><font size="3" color="black">Exit Time</th><th><font size="3" color="black">Total Charges</th><th><font size="3" color="black">Vehicle No</th>'
        output+='<th><font size="3" color="black">Username</th><th><font size="3" color="black">Card No</th>'
        output+='<th><font size="3" color="black">CVV</th><th><font size="3" color="black">Status</th></tr>'
        output+='</tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from book_slot where username='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[2])+'</td><td><font size="3" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[4])+'</td><td><font size="3" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[6])+'</td><td><font size="3" color="black">'+str(row[7])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[8])+'</td><td><font size="3" color="black">'+str(row[9])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[10])+'</td></tr>' 
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'UserScreen.html', context)

def getCost(area, parking_id):
    cost = 0
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select parking_cost from parking_area where area_id='"+area+"'")
        rows = cur.fetchall()
        for row in rows:
            cost = row[0]
            break
    entry_time = ""
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select entry_date from book_slot where parking_id='"+parking_id+"'")
        rows = cur.fetchall()
        for row in rows:
            entry_time = row[0]
            entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
            break
    return cost, entry_time    

def ReleaseSlotAction(request):
    if request.method == 'POST':
        global username
        parking_id = request.POST.get('t1', False)
        area_id = request.POST.get('t2', False)
        hours = request.POST.get('t3', False)
        charges = request.POST.get('t4', False)
        exit_time = request.POST.get('t5', False)
        card = request.POST.get('t6', False)
        cvv = request.POST.get('t7', False)

        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        cursor = db_connect.cursor()
        query = "update book_slot set exit_date='"+exit_time+"', total_charges='"+charges+"', card_no='"+card+"', cvv_no='"+cvv+"', status='Released' where parking_id='"+parking_id+"'"
        cursor.execute(query)
        db_connect.commit()
        context= {'data': "Slot successfully released"}
        return render(request, 'UserScreen.html', context)

def SlotRelease(request):
    if request.method == 'GET':
        parking_id = request.GET.get('name', False)
        area = request.GET.get('area', False)
        exit_time = datetime.now()
        exit_time = exit_time.strftime('%Y-%m-%d %H:%M:%S')
        exit_time = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')

        cost, entry_time = getCost(area, parking_id)
        #entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
        difference = exit_time - entry_time
        print(str(difference))
        difference = difference.total_seconds() / 3600
        difference = round(difference, 4)
        print(str(difference)+" "+str(cost))    
        charges = difference * cost
        charges = round(charges, 3)
        output =  '<tr><td><font size="3" color="black"><b>Parking&nbsp;ID</b></td><td><input type="number" name="t1" size="15" value="'+parking_id+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black"><b>Area&nbsp;ID</b></td><td><input type="number" name="t2" size="15" value="'+area+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black"><b>Total&nbsp;Hours</b></td><td><input type="number" name="t3" size="15" value="'+str(difference)+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black"><b>Charges</b></td><td><input type="number" name="t4" size="15" value="'+str(charges)+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black"><b>Exit&nbsp;time</b></td><td><input type="text" name="t5" size="25" value="'+str(exit_time)+'" readonly/></td></tr>'
        
        context= {'data1': output}
        return render(request, 'ReleaseSlot.html', context)

def ReleaseSlot(request):
    if request.method == 'GET':
        global username
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Parking ID</th><th><font size="3" color="black">Area ID</th>'
        output+='<th><font size="3" color="black">Slot No</th><th><font size="3" color="black">Entry Time</th>'
        output+='<th><font size="3" color="black">Exit Time</th><th><font size="3" color="black">Total Charges</th><th><font size="3" color="black">Vehicle No</th>'
        output+='<th><font size="3" color="black">Release Booking</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from book_slot where username='"+username+"' and status='Booked'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[2])+'</td><td><font size="3" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[4])+'</td><td><font size="3" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[6])+'</td>'
                output+='<td><a href=\'SlotRelease?name='+str(row[0])+'&area='+str(row[1])+'\'><font size=3 color=black>Click Here to Release</font></a></td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'UserScreen.html', context) 

def ViewOccupancy(request):
    if request.method == 'GET':
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Parking ID</th><th><font size="3" color="black">Area ID</th>'
        output+='<th><font size="3" color="black">Slot No</th><th><font size="3" color="black">Entry Time</th>'
        output+='<th><font size="3" color="black">Exit Time</th><th><font size="3" color="black">Total Charges</th><th><font size="3" color="black">Vehicle No</th>'
        output+='<th><font size="3" color="black">Username</th><th><font size="3" color="black">Card No</th>'
        output+='<th><font size="3" color="black">CVV</th><th><font size="3" color="black">Status</th></tr>'
        output+='</tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from book_slot")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[2])+'</td><td><font size="3" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[4])+'</td><td><font size="3" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[6])+'</td><td><font size="3" color="black">'+str(row[7])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[8])+'</td><td><font size="3" color="black">'+str(row[9])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[10])+'</td></tr>' 
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'AdminScreen.html', context) 

def BookSlotAction(request):
    if request.method == 'POST':
        global username
        area = request.POST.get('t1', False)
        slot = request.POST.get('t2', False)
        vehicle_no = request.POST.get('t3', False)
        entry_time = datetime.now()
        entry_time = entry_time.strftime('%Y-%m-%d %H:%M:%S')        
        output = "Error in booking slot"
        parking_id = 0
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select max(parking_id) from book_slot")
            rows = cursor.fetchall()
            for row in rows:
                parking_id = row[0]
                break
        if parking_id is not None:
            parking_id += 1
        else:
            parking_id = 1
        total_charges = "0"
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        cursor = db_connect.cursor()
        query = "INSERT INTO book_slot VALUES('"+str(parking_id)+"','"+area+"','"+slot+"','"+entry_time+"','"+entry_time+"','"+total_charges+"','"+vehicle_no+"','"+username+"','"+total_charges+"','"+total_charges+"','Booked')"
        cursor.execute(query)
        db_connect.commit()
        if cursor.rowcount == 1:
            output = 'Your parking slot booked with id = '+str(parking_id)
        context= {'data': output}
        return render(request, 'UserScreen.html', context)

def ChooseSlot(request):
    if request.method == 'GET':
        slot_no = request.GET.get('name', False)
        area_id = request.GET.get('area', False)
        output =  '<tr><td><font size="3" color="black"><b>Area&nbsp;ID</b></td><td><input type="number" name="t1" size="15" value="'+area_id+'" readonly/></td></tr>'
        output +=  '<tr><td><font size="3" color="black"><b>Slot&nbsp;No</b></td><td><input type="number" name="t2" size="15" value="'+slot_no+'" readonly/></td></tr>'
        context= {'data1': output}
        return render(request, 'BookSlot.html', context)

def AreaChoose(request):
    if request.method == 'GET':
        area_id = request.GET.get('name', False)
        slots = request.GET.get('slots', False)
        slots = int(slots)
        counter = 0
        booked = []
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select slot_no from book_slot where area_id='"+area_id+"' and status='Booked'")
            rows = cursor.fetchall()
            for row in rows:
                booked.append(int(row[0]))
        output='<table border=0 align=center width=100%>'
        index = 0
        output += '<tr>'
        for i in range(0, slots):
            if i not in booked:
                output += '<td><a href=\'ChooseSlot?name='+str(i)+'&area='+str(area_id)+'\'><img src="static/images/free.jpg" width="50" height="50"/></a></td>'
            else:
                output += '<td><img src="static/images/parked.jpg" width="50" height="50"/></td>'
                counter += 1
            index += 1
            if index == 5:
                output += "</tr><tr>"
                index = 0
        output += "</table><br/><br/><br/><br/>"
        print(str(slots)+" "+str(counter))
        if counter >= slots:
            output = '<font size="3" color="red">All slots booked for selected Area. Please choose another area</font>'
        context= {'data': output}
        return render(request, 'UserScreen.html', context)

def BookSlot(request):
    if request.method == 'GET':
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Parking Area ID</th><th><font size="3" color="black">Area Name</th>'
        output+='<th><font size="3" color="black">Direction</th>'
        output+='<th><font size="3" color="black">Floor No</th>'
        output+='<th><font size="3" color="black">Total Slots</th>'
        output+='<th><font size="3" color="black">Parking&nbsp;Cost</th>'
        output+='<th><font size="3" color="black">Choose Desired Location</th></tr>'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select * from parking_area")
            rows = cursor.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[2])+'</td><td><font size="3" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[4])+'</td><td><font size="3" color="black">'+str(row[5])+'</td>'
                output+='<td><a href=\'AreaChoose?name='+str(row[0])+'&slots='+str(row[4])+'\'><font size=3 color=black>Click Here to Book</font></a></td></tr>'
        output += "</table><br/><br/><br/><br/>"        
        context= {'data': output}
        return render(request, 'UserScreen.html', context) 


def AddArea(request):
    if request.method == 'GET':
        return render(request, 'AddArea.html', {})    

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})
    
def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def ModifyAreaAction(request):
    if request.method == 'POST':
        area_id = request.POST.get('t1', False)
        slots = request.POST.get('t2', False)
        cost = request.POST.get('t3', False)
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        cursor = db_connect.cursor()
        query = "update parking_area set total_slots='"+slots+"', parking_cost='"+cost+"' where area_id='"+area_id+"'"
        cursor.execute(query)
        db_connect.commit()
        context= {'data': "Cost & Slot details successfully updated"}
        return render(request, 'AdminScreen.html', context)

def AreaModify(request):
    if request.method == 'GET':
        area_id = request.GET.get('name', False)
        output =  '<tr><td><font size="3" color="black"><b>Area&nbsp;ID</b></td><td><input type="number" name="t1" size="15" value="'+area_id+'" readonly/></td></tr>'
        context= {'data1': output}
        return render(request, 'ModifyArea.html', context)

def ModifyArea(request):
    if request.method == 'GET':
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Parking Area ID</th><th><font size="3" color="black">Area Name</th>'
        output+='<th><font size="3" color="black">Direction</th>'
        output+='<th><font size="3" color="black">Floor No</th>'
        output+='<th><font size="3" color="black">Total Slots</th>'
        output+='<th><font size="3" color="black">Parking&nbsp;Cost</th>'
        output+='<th><font size="3" color="black">Edit Cost or Slots</th></tr>'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select * from parking_area")
            rows = cursor.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[2])+'</td><td><font size="3" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[4])+'</td><td><font size="3" color="black">'+str(row[5])+'</td>'
                output+='<td><a href=\'AreaModify?name='+str(row[0])+'\'><font size=3 color=black>Click Here to Modify</font></a></td></tr>'
        output += "</table><br/><br/><br/><br/>"        
        context= {'data': output}
        return render(request, 'AdminScreen.html', context)       

def AddAreaAction(request):
    if request.method == 'POST':
        gate = request.POST.get('t1', False)
        direction = request.POST.get('t2', False)
        floor = request.POST.get('t3', False)
        slots = request.POST.get('t4', False)
        cost = request.POST.get('t5', False)
        output = "Error in adding parking details"
        area_id = 0
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select max(area_id) from parking_area")
            rows = cursor.fetchall()
            for row in rows:
                area_id = row[0]
                break
        if area_id is not None:
            area_id += 1
        else:
            area_id = 1
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        cursor = db_connect.cursor()
        query = "INSERT INTO parking_area VALUES('"+str(area_id)+"','"+gate+"','"+direction+"','"+floor+"','"+slots+"','"+cost+"')"
        cursor.execute(query)
        db_connect.commit()
        if cursor.rowcount == 1:
            output = 'Parking area added with id = '+str(area_id)
        context= {'data': output}
        return render(request, 'AddArea.html', context)

def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        command = 'not_found'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select username from signup where username = '"+username+"'")
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == username:
                    command = username+' Given Username already exists'
                    break
        if command == 'not_found':
            db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
            cursor = db_connect.cursor()
            query = "INSERT INTO signup VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            cursor.execute(query)
            db_connect.commit()
            if cursor.rowcount == 1:
                command = 'Signup process completed successfully'
        context= {'data': command}
        return render(request, 'Register.html', context)

def AdminLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList, usertype
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = "AdminLogin.html"
        output = 'Invalid login details'
        if username == "admin" and password == "admin":
            status = "AdminScreen.html"
            output = '<font size="3" color="blue">Welcome '+username+"</font>"                  
        context= {'data':output}
        return render(request, status, context)

def UserLoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = "UserLogin.html"
        output = 'Invalid login details'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select username, password from signup")
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    output = 'Welcome '+username
                    status = "UserScreen.html"                    
                    break    
        context= {'data':output}
        return render(request, status, context)    
    
def ViewUsers(request):
    if request.method == 'GET':
        global uname
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Username</th><th><font size="3" color="black">Password</th>'
        output+='<th><font size="3" color="black">Contact No</th><th><font size="3" color="black">Email ID</th>'
        output+='<th><font size="3" color="black">Address</th></tr>'
        output+='</tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'parking',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from signup")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="" color="black">'+str(row[0])+'</td><td><font size="" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="" color="black">'+str(row[2])+'</td><td><font size="" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="" color="black">'+str(row[4])+'</td></tr>'  
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'AdminScreen.html', context) 
