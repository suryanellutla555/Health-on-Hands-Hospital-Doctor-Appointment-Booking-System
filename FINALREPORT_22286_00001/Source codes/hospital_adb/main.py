import datetime
import os.path
import re
from bson import ObjectId
from flask import Flask, request, render_template, redirect, session, app
import pymongo

app = Flask(__name__)
doctor = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = doctor["Doctor"]
admin_collection = my_database["admin"]
officers_collection = my_database["officers"]
doctor_collection = my_database["doctor"]
doctor_timings_collection = my_database["doctor_timings"]
slots_collection = my_database["slots"]
patient_collection = my_database["patient"]
vaccines_collection = my_database["vaccines"]
appointments_collection = my_database["appointment"]
prescription_collection = my_database["prescription"]
payments_collection = my_database["payments"]
app.secret_key = "doctor"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT_DOCTORS = APP_ROOT + "/static/doctors"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT_VACCINES = APP_ROOT + "/static/vaccines"
query = {}
count = admin_collection.count_documents({})
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)

WEEK_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session["admin_id"] = str(admin['_id'])
        session["role"] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="invalid login details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/add_view_officer")
def add_view_officer():
    officer_id = request.args.get("officer_id")
    officer = {}
    if officer_id!=None:
        officer = officers_collection.find_one({"_id": ObjectId(officer_id)})
    query = {}
    officers = officers_collection.find(query)
    officers = list(officers)
    message = request.args.get("message")
    if message == None:
        message = ""
    return render_template("add_view_officer.html", officers=officers,officer=officer, message=message)


@app.route("/add_view_officer_action", methods=['post'])
def add_view_officer_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    gender = request.form.get("gender")
    phone = request.form.get("phone")
    dob = request.form.get("dob")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    address = request.form.get("address")
    ssn = request.form.get("ssn")
    officer_id = request.form.get("officer_id")
    if officer_id != "":
        query1 = {"_id": ObjectId(officer_id)}
        query2 = {"$set": {"first_name": first_name,"last_name":last_name,"email":email,"gender":gender,"phone":phone,"dob":dob,"city":city,
                 "state":state,"zipcode":zipcode,"address":address,"ssn":ssn}}
        officers_collection.update_one(query1, query2)
        return redirect("add_view_officer?message= Officer Update Successfully")
    query = {"last_name": last_name}
    count = officers_collection.count_documents(query)
    if count == 0:
        query = {"first_name": first_name,"last_name":last_name,"email":email,"gender":gender,"phone":phone,"dob":dob,"city":city,
                 "state":state,"zipcode":zipcode,"address":address,"ssn":ssn}
        officers_collection.insert_one(query)
        return redirect("add_view_officer?message= Officer Added Successfully")
    else:
        return redirect("add_view_officer?message= Duplicate Exist")


def adupile(param, IGNORECASE):
    pass


@app.route("/add_view_vaccines")
def add_view_vaccines():
    vaccine_id = request.args.get("vaccine_id")
    vaccine = {}
    if vaccine_id != None:
        vaccine = vaccines_collection.find_one({"_id": ObjectId(vaccine_id)})
    message = request.args.get("message")
    keyword = request.args.get("keyword")
    if keyword == None:
        keyword = ""
    keyword2 = re.compile(".*" + str(keyword) + ".*", re.IGNORECASE)
    query = {"name": keyword2}
    vaccines = vaccines_collection.find(query)
    vaccines = list(vaccines)
    if message == None:
        message = ""
    return render_template("add_view_vaccines.html", vaccines=vaccines, vaccine=vaccine, message=message, keyword=keyword,is_consulted_the_doctor=is_consulted_the_doctor)


@app.route("/add_view_vaccine_action", methods=['post'])
def add_view_vaccine_action():
    vaccine_id = request.form.get("vaccine_id")
    name = request.form.get("name")
    about = request.form.get("about")
    is_prescription_needed = request.form.get("prescription")
    start_time = request.form.get("start_time")
    start_time = datetime.datetime.strptime(start_time, "%H:%M")
    end_time = request.form.get("end_time")
    end_time = datetime.datetime.strptime(end_time, "%H:%M")
    price = request.form.get("price")
    vaccine_image = request.files.get("vaccine_image")
    message = "Vaccine Added Successfully"
    if vaccine_image.filename != "":
        path = APP_ROOT_VACCINES + "/" + vaccine_image.filename
        vaccine_image.save(path)
        query = {"name": name, "about": about, "is_prescription_needed": is_prescription_needed,
                 "vaccine_image": vaccine_image.filename, "start_time": start_time,
                 "end_time": end_time, "price": price}
    else:
        query = {"name": name, "about": about, "is_prescription_needed": is_prescription_needed,"start_time": start_time,
                 "end_time": end_time, "price": price}
    if vaccine_id != "":
        query1 = {"_id": ObjectId(vaccine_id)}
        query2 = {"$set": query}
        vaccines_collection.update_one(query1, query2)
        vaccine_id = ObjectId(vaccine_id)
        query3 = {"vaccine_id": vaccine_id}
        slots_collection.delete_many(query3)
        message = "Vaccine Updated Successfully"
    else:
        query4 = {"name": name}
        count = vaccines_collection.count_documents(query4)
        if count == 0:
            result = vaccines_collection.insert_one(query)
            vaccine_id = result.inserted_id
        else:
            return redirect("add_view_vaccines?message= Duplicate exist")
    slot_number = 1
    while start_time < end_time:
        slot_start_time = start_time
        slot_start_time = slot_start_time.strftime("%H:%M %p")
        start_time = start_time + datetime.timedelta(minutes=15)
        slot_end_time = start_time
        slot_end_time = slot_end_time.strftime("%H:%M %p")
        query = {"slot_number": slot_number, "slot_start_time": slot_start_time, "slot_end_time": slot_end_time,
                 "vaccine_id": vaccine_id}
        slots_collection.insert_one(query)
        slot_number = slot_number + 1
        if start_time > end_time:
            break
    return redirect("add_view_vaccines?message="+message)


@app.route("/add_view_doctor")
def add_view_doctor():
    query = {}
    doctors = doctor_collection.find(query)
    doctors = list(doctors)
    message = request.args.get("message")
    keyword = request.args.get("keyword")
    vaccine_id = request.args.get("vaccine_id")
    if vaccine_id == None:
        vaccine_id = ""
    if keyword == None:
        keyword = ""
    if keyword == "":
        query = {}
    else:
        keyword2 = re.compile(".*" + str(keyword) + ".*", re.IGNORECASE)
        query = {"$or": [{"name": keyword2}, {"specialization": keyword2}]}
    doctors = doctor_collection.find(query)
    doctors = list(doctors)
    if message == None:
        message = ""
    return render_template("add_view_doctor.html", doctors=doctors, message=message, keyword=keyword,
                           vaccine_id=vaccine_id)


@app.route("/add_view_doctor_action", methods=['post'])
def add_view_doctor_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    gender = request.form.get("gender")
    dob = request.form.get("dob")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    address = request.form.get("address")
    ssn = request.form.get("ssn")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password != password2:
        return redirect("add_view_doctor?message=Password and confirm password did not match")
    specialization = request.form.get("specialization")
    designation = request.form.get("designation")
    experience = request.form.get("experience")
    about_doctor = request.form.get("about_doctor")
    picture = request.form.get("vaccine_image")
    consulting_fee = request.form.get("consulting_fee")
    # start_time = request.form.get("start_time")
    # start_time = datetime.datetime.strptime(start_time, "%H:%M")
    # end_time = request.form.get("end_time")
    # end_time = datetime.datetime.strptime(end_time, "%H:%M")
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = doctor_collection.count_documents(query)
    if count == 0:
        picture = request.files.get("picture")
        path = APP_ROOT_DOCTORS + "/" + picture.filename
        picture.save(path)
        query = {"first_name": first_name, "email": email, "phone": phone, "password": password, "specialization": specialization,
                 "designation": designation,"first_name":first_name,"last_name":last_name,"gender":gender,"dob":dob,
                 "experience": experience, "about_doctor": about_doctor, "picture": picture.filename,"city":city,
                 "consulting_fee": consulting_fee,"state":state,"zipcode":zipcode,"address":address,"ssn":ssn, "is_logged": False}
        result = doctor_collection.insert_one(query)
        # doctor_id = result.inserted_id
        # slot_number = 1
        # while start_time < end_time:
        #     slot_start_time = start_time
        #     slot_start_time = slot_start_time.strftime("%H:%M %p")
        #     start_time = start_time + datetime.timedelta(minutes=15)
        #     slot_end_time = start_time
        #     slot_end_time = slot_end_time.strftime("%H:%M %p")
        #     query = {"slot_number": slot_number, "slot_start_time": slot_start_time, "slot_end_time": slot_end_time,
        #              "doctor_id": doctor_id}
        #     slots_collection.insert_one(query)
        #     slot_number = slot_number + 1
        #     if start_time > end_time:
        #         break
        return redirect("add_view_doctor?message=Doctor added successfully")
    else:
        return redirect("add_view_doctor?message= Duplicate exist")


@app.route("/doctor_login")
def doctor_login():
    return render_template("doctor_login.html")


@app.route("/doctor_login_action", methods=['post'])
def doctor_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = doctor_collection.count_documents(query)
    if count > 0:
        doctor = doctor_collection.find_one(query)
        if doctor['is_logged'] == True:
            session['doctor_id'] = str(doctor['_id'])
            session['role'] = 'doctor'
            return redirect("/doctor_home")
        else:
            return render_template("change_password.html", doctor_id=doctor['_id'])
    else:
        return render_template("message.html", message="invalid login details")

@app.route("/change_password_action", methods = ['post'])
def change_password_action():
    doctor_id = request.form.get("doctor_id")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password != password2:
        return render_template("message.html", message="New Password and Confirm New Password did not match")
    query = {"_id": ObjectId(doctor_id)}
    query2 = {"$set": {"password": password, "is_logged": True}}
    doctor_collection.update_one(query, query2)
    doctor = doctor_collection.find_one(query)
    session['doctor_id'] = str(doctor['_id'])
    session['role'] = 'doctor'
    return redirect("/doctor_home")
@app.route("/doctor_home")
def doctor_home():
    return render_template("doctor_home.html")


@app.route("/patient_login")
def patient_login():
    return render_template("patient_login.html")


@app.route("/patient_login_action", methods=['post'])
def patient_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = patient_collection.count_documents(query)
    if count > 0:
        patient = patient_collection.find_one(query)
        session['patient_id'] = str(patient['_id'])
        session['role'] = 'patient'
        return redirect("/patient_home")
    else:
        return render_template("message.html", message="invalid login details")


@app.route("/patient_register")
def patient_register():
    return render_template("patient_register.html")


@app.route("/Patient_register_action", methods=['post'])
def Patient_register_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone_number = request.form.get("phone_number")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    query = {"email": email, "phone_number": phone_number}
    if password != password2:
        return render_template("message.html", message="password and confirm password must be same")
    query = {"$or":[{"email": email}, {"phone_number": phone_number}]}
    count = patient_collection.count_documents(query)
    if count == 0:
        query = {"name": name, "email": email, "phone_number": phone_number, "password": password}
        patient_collection.insert_one(query)
        return render_template("message.html", message="Register Successfully")
    else:
        return render_template("message.html", message="Duplicate Entry")

@app.route("/doctor_timings")
def doctor_timings():
    doctor_id = session["doctor_id"]
    print(doctor_id)
    query = {"doctor_id": ObjectId(doctor_id)}
    doctor_timings = doctor_timings_collection.find(query)
    doctor_timings = list(doctor_timings)
    print(doctor_timings)
    return render_template("doctor_timings.html", doctor_timings=doctor_timings)
@app.route("/doctor_timings_action")
def doctor_timings_action():
    doctor_id = session["doctor_id"]
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    day = request.args.get("day")
    start_date = datetime.datetime.strptime(start_date, "%H:%M")
    end_date = datetime.datetime.strptime(end_date, "%H:%M")

    query = {"$or": [
        {"start_date": {"$gte": start_date, "$lte": end_date}, "end_date": {"$gte": [start_date,end_date]}, "doctor_id": ObjectId(doctor_id), "day": day},
        {"start_date": {"$lte": [start_date,end_date]}, "end_date": {"$lte": start_date, "$gte": end_date}, "doctor_id": ObjectId(doctor_id), "day": day},
        {"start_date": {"$lte": [start_date,end_date]}, "end_date": {"$gte": [start_date,end_date]}, "doctor_id": ObjectId(doctor_id), "day": day},
        {"start_date": {"$gte": start_date, "$lte": end_date}, "end_date": {"$gte": start_date, "$lte": end_date}, "doctor_id": ObjectId(doctor_id), "day": day}
    ]}


    count = doctor_timings_collection.count_documents(query)
    if count > 0:
        return render_template("doctor_message.html", message="There is a time conflict on these days")
    else:
        query = {"day": day, "start_date": start_date, "end_date": end_date, "doctor_id": ObjectId(doctor_id)}
        result = doctor_timings_collection.insert_one(query)
        doctor_timing_id = result.inserted_id
        doctor_timings = doctor_timings_collection.find({"day": day, "doctor_id": ObjectId(doctor_id)})
        doctor_timing_ids = []
        for doctor_timing in doctor_timings:
            doctor_timing_ids.append(doctor_timing['_id'])
        slots = slots_collection.find({"doctor_timing_id": {"$in":doctor_timing_ids }})
        slots = list(slots)
        slot_number = len(slots)+1
        start_date2 = start_date
        while start_date2 < end_date:
            slot_start_time = start_date2
            slot_start_time = slot_start_time.strftime("%H:%M %p")
            start_date2 = start_date2 + datetime.timedelta(minutes=15)
            slot_end_time = start_date2
            slot_end_time = slot_end_time.strftime("%H:%M %p")
            query = {"slot_number": slot_number, "slot_start_time": slot_start_time, "slot_end_time": slot_end_time,
                     "doctor_timing_id": doctor_timing_id}
            slots_collection.insert_one(query)
            slot_number = slot_number + 1
            if start_date2 > end_date:
                break
    return redirect("/doctor_timings")
@app.route("/patient_home")
def patient_home():
    return render_template("patient_home.html")


@app.route("/slots")
def slots():
    appointment_type = request.args.get("appointment_type")
    vaccine_id = request.args.get("vaccine_id")
    doctor_id = request.args.get("doctor_id")
    appointment_date = request.args.get("appointment_date")
    if appointment_date == None:
        appointment_date = datetime.datetime.now()
        appointment_date = appointment_date.strftime("%Y-%m-%d")
    if doctor_id == None:
        doctor_id = ""
    if vaccine_id == None:
        vaccine_id = ""
    if session['role'] == 'doctor':
        doctor_id = session['doctor_id']
    if appointment_type == "vaccine":
        query = {"vaccine_id": ObjectId(vaccine_id)}
    elif appointment_type == "doctor":
        appointment_date3 = datetime.datetime.strptime(appointment_date,"%Y-%m-%d")
        day = WEEK_DAYS[appointment_date3.weekday()]
        query = {"doctor_id": ObjectId(doctor_id), "day":day}
        doctor_timings = doctor_timings_collection.find(query)
        doctor_timing_ids =[]
        for doctor_timing in doctor_timings:
            doctor_timing_ids.append(doctor_timing['_id'])
        query = {"doctor_timing_id": {"$in": doctor_timing_ids}}
    slots = slots_collection.find(query)
    slots = list(slots)
    # if len(slots) == 0:
    #     if session['role'] == 'patient':
    #         return render_template("")
    #     elif session['role'] == 'doctor':
    #         return render_template("doctor_message.html", message="Slots Not Available On "+appointment_date)

    doctor = None
    vaccine = None
    if appointment_type == "vaccine":
        query = {"_id": ObjectId(vaccine_id)}
        vaccine = vaccines_collection.find_one(query)
    elif appointment_type == "doctor":
        query = {"_id": ObjectId(doctor_id)}
        doctor = doctor_collection.find_one(query)
        if vaccine_id != "":
            query = {"_id": ObjectId(vaccine_id)}
            vaccine = vaccines_collection.find_one(query)

    return render_template("slots.html", slots=slots, vaccine_id=vaccine_id, doctor_id=doctor_id,
                           appointment_date=appointment_date, appointment_type=appointment_type, doctor=doctor,
                           vaccine=vaccine, is_slot_booked_on_date=is_slot_booked_on_date, len=len)


@app.route("/book_slot", methods=['post'])
def book_slot():
    slot_id = request.form.get("slot_id")
    vaccine_id = request.form.get("vaccine_id")
    doctor_id = request.form.get("doctor_id")
    appointment_type = request.form.get("appointment_type")
    appointment_date = request.form.get("appointment_date")
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
    booked_date = datetime.datetime.now()
    if doctor_id == "":
        query = {"_id": ObjectId(vaccine_id)}
        vaccine = vaccines_collection.find_one(query)
        price = int(vaccine['price'])
        patient_id = session['patient_id']
        query = {"slot_id": ObjectId(slot_id), "status": "Payment Pending", "vaccine_id": ObjectId(vaccine_id),
                 "appointment_type": appointment_type, "appointment_date": appointment_date, "booked_date": booked_date,
                 "price": price, "patient_id": ObjectId(patient_id)}
    else:
        query = {"_id": ObjectId(doctor_id)}
        doctor = doctor_collection.find_one(query)
        price = int(doctor['consulting_fee'])
        patient_id = session['patient_id']
        query = {"slot_id": ObjectId(slot_id), "status": "Payment Pending", "vaccine_id": ObjectId(vaccine_id),
                 "doctor_id": ObjectId(doctor_id),
                 "appointment_type": appointment_type, "appointment_date": appointment_date, "booked_date": booked_date,
                 "price": price, "patient_id": ObjectId(patient_id)}
    result = appointments_collection.insert_one(query)
    appointment_id = result.inserted_id
    query = {"_id": appointment_id}
    appointment = appointments_collection.find_one(query)
    query = {"_id": appointment['slot_id']}
    slot = slots_collection.find_one(query)
    query = {"_id": appointment['vaccine_id']}
    vaccine = vaccines_collection.find_one(query)
    doctor = None
    if doctor_id != "":
        query = {"_id": appointment["doctor_id"]}
        doctor = doctor_collection.find_one(query)
    return render_template("book_slot.html", appointment=appointment, slot=slot, vaccine=vaccine, doctor=doctor,
                           is_slot_booked_on_date=is_slot_booked_on_date)


def is_slot_booked_on_date(slot_id, appointment_date):
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
    statuses = ["Cancelled", "Rejected"]
    query = {"slot_id": slot_id, "appointment_date": appointment_date,
             "status": {"$nin": statuses}}
    print(query)
    count = appointments_collection.count_documents(query)
    if count > 0:
        return True
    else:
        return False


@app.route("/book_slot2", methods=['post'])
def book_slot2():
    appointment_id = request.form.get("appointment_id")
    price = request.form.get("price")
    card_type = request.form.get("card_type")
    card_number = request.form.get("card_number")
    name_on_card = request.form.get("name_on_card")
    cvv = request.form.get("cvv")
    expiry_date = request.form.get("expiry_date")
    patient_id = session['patient_id']
    query = {"appointment_id": ObjectId(appointment_id), "price": price, "card_type": card_type,
             "card_number": card_number, "name_on_card": name_on_card, "cvv": cvv, "expiry_date": expiry_date,
             "patient_id": ObjectId(patient_id)}
    payments_collection.insert_one(query)
    query = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Appointment Booked"}}
    appointments_collection.update_one(query, query2)
    return render_template("patient_message.html", message="Appointment Booked Successfully")


@app.route("/view_appointment")
def view_appointment():
    if session['role'] == 'patient':
        patient_id = session['patient_id']
        query = {"patient_id": ObjectId(patient_id)}
    else:
        slot_id = request.args.get("slot_id")
        appointment_date = request.args.get("appointment_date")
        appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
        query = {"slot_id": ObjectId(slot_id), "appointment_date": appointment_date}
    appointments = appointments_collection.find(query)
    appointments = list(appointments)
    appointments.reverse()
    print(appointments)
    officers = officers_collection.find({})
    officers = list(officers)
    return render_template("view_appointment.html", appointments=appointments, officers=officers, get_vaccine_by_vaccine_id=get_vaccine_by_vaccine_id,
                           get_patient_by_patient_id=get_patient_by_patient_id, get_slot_by_slot_id=get_slot_by_slot_id,get_doctor_by_doctor_id=get_doctor_by_doctor_id,
                           get_appointment_by_vaccine=get_appointment_by_vaccine, get_officer_by_officer_id=get_officer_by_officer_id)



@app.route("/cancel_appointment")
def cancel_appointment():
    appointment_id=request.args.get("appointment_id")
    query = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Cancelled"}}
    appointments_collection.update_one(query,query2)
    query = {"appointment_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Payment Refunded"}}
    payments_collection.update_one(query, query2)
    return render_template("patient_message.html", message="Appointment cancelled")

def get_vaccine_by_vaccine_id(vaccine_id):
    query = {"_id": vaccine_id}
    vaccine = vaccines_collection.find_one(query)
    return vaccine

def get_patient_by_patient_id(patient_id):
    query = {"_id": patient_id}
    patient = patient_collection.find_one(query)
    return patient

def get_slot_by_slot_id(slot_id):
    query = {"_id": slot_id}
    slot = slots_collection.find_one(query)
    return slot

def get_doctor_by_doctor_id(doctor_id):
    query = {"_id": doctor_id}
    doctor = doctor_collection.find_one(query)
    return doctor

@app.route("/assign_office")
def assign_office():
    appointment_id = request.args.get("appointment_id")
    officer_id = request.args.get("officer_id")
    query = {"_id": ObjectId(appointment_id)}
    query2 = {"$set":{"officer_id": ObjectId(officer_id), "status": "Officer Assigned"}}
    appointments_collection.update_one(query,query2)
    return render_template("admin_message.html", message="Officer Assigned")

@app.route("/mark_as_vaccinated")
def mark_as_vaccinated():
    appointment_id = request.args.get("appointment_id")
    query = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Vaccinated"}}
    appointments_collection.update_one(query, query2)
    return render_template("admin_message.html", message="Marked as vaccinated")


@app.route("/reject_appointment")
def reject_appointment():
    appointment_id = request.args.get("appointment_id")
    query = {"_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Rejected"}}
    appointments_collection.update_one(query, query2)
    query = {"appointment_id": ObjectId(appointment_id)}
    query2 = {"$set": {"status": "Payment Refunded"}}
    payments_collection.update_one(query, query2)
    if session['role'] == 'admin':
        return render_template("admin_message.html", message="Appointment cancelled")
    else:
        return render_template("doctor_message.html", message="Appointment cancelled")


@app.route("/write_prescription")
def write_prescription():
    appointment_id=request.args.get("appointment_id")
    return render_template("write_prescription.html",appointment_id=appointment_id)

@app.route("/write_prescription_action")
def write_prescription_action():
    appointment_id = request.args.get("appointment_id")
    prescription = request.args.get("prescription")
    date=datetime.datetime.now()
    query={"appointment_id":ObjectId(appointment_id),"prescription":prescription,"date":date}
    prescription_collection.insert_one(query)
    query1={"_id":ObjectId(appointment_id)}
    query2={"$set":{"status":"Prescribed"}}
    appointments_collection.update_one(query1,query2)
    return render_template("doctor_message.html", message="Prescription sent successfully")

def is_consulted_the_doctor(vaccine_id):
    patient_id = session['patient_id']
    query = {"vaccine_id": ObjectId(vaccine_id), "patient_id": ObjectId(patient_id), "status": "Prescribed"}
    count = appointments_collection.count_documents(query)
    if count > 0:
        return True
    else:
        return False
def get_appointment_by_vaccine(vaccine_id, patient_id):
    query = {"vaccine_id": ObjectId(vaccine_id), "patient_id": ObjectId(patient_id), "status": "Prescribed"}
    appointment = appointments_collection.find_one(query)
    return appointment

@app.route("/view_prescription")
def view_prescription():
    appointment_id = request.args.get("appointment_id")
    query = {"appointment_id": ObjectId(appointment_id)}
    prescription = prescription_collection.find_one(query)
    return render_template("view_prescription.html", prescription=prescription)


@app.route("/view_payments")
def view_payments():
    appointment_id = request.args.get("appointment_id")
    query = {"appointment_id": ObjectId(appointment_id)}
    payment = payments_collection.find_one(query)
    return render_template("view_payments.html", payment=payment)

def get_officer_by_officer_id(officer_id):
    query = {"_id": officer_id}
    officer = officers_collection.find_one(query)
    return officer
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/edit_details")
def edit_details():
     vaccine_id = request.args.get("vaccine_id")
     vaccines = vaccines_collection.find_one({"_id": ObjectId(vaccine_id)})
     return render_template("edit_details.html", vaccines=vaccines, vaccine_id=vaccine_id)

@app.route("/edit_vaccine_details_action")
def edit_vaccine_details_action():
    vaccine_id = request.args.get("specialization_id")
    name = request.args.get("name")
    about = request.args.get("about")
    is_prescription_needed = request.args.get("is_prescription_needed")
    price = request.args.get("price")
    query1 = {"_id": ObjectId(vaccine_id)}
    query2 = {"$set": {"name":name,"about":about,"is_prescription_needed":is_prescription_needed,"price":price}}
    vaccines_collection.update_many(query1, query2)
    return render_template("admin_message.html", message="Details are Updated")

app.run(debug=True)
