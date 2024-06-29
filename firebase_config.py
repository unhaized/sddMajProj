import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyBHJQfOOwEPMo3UQSR4CXuMECIiDSyIQNI",
    "authDomain": "sddmajproj.firebaseapp.com",
    "databaseURL": "https://sddmajproj-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "sddmajproj",
    "storageBucket": "sddmajproj.appspot.com",
    "messagingSenderId": "197676173625",
    "appId": "1:197676173625:web:796b10b2516828b06d80e8",
    "measurementId": "G-DC4LJSJH6F"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()