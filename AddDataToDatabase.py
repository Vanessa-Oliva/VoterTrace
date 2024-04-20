import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://biometricsattendance-ac92c-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ref = db.reference("Voters")

data = {
    "01001":
    {
        "name": "Vanessa Oliva",
        "address": "Sampaguita St., Sta. Mesa, Manila",
        "barangay": 1,
        "contact": "09123456789",
        "registration_status": "active",
        "last_attendance_time": "2024-04-16 17:13:55"
    },
    "01002":
    {
        "name": "Louis Partridge",
        "address": "Wandsworth, London, United Kingdom",
        "barangay": 1,
        "contact": "09123456789",
        "registration_status": "active",
        "last_attendance_time": "2024-04-16 17:13:55"
    },
    "01003":
    {
        "name": "Tom Holland",
        "address": "Kingston, Thames, United Kingdom",
        "barangay": 1,
        "contact": "09123456789",
        "registration_status": "active",
        "last_attendance_time": "2024-04-16 17:13:55"
    }


}

for key,value in data.items():
    ref.child(key).set(value)