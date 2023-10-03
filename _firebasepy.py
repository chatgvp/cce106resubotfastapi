import firebase_admin
from firebase_admin import credentials, initialize_app, storage, db
from datetime import datetime, timedelta
cred = credentials.Certificate("firebase.json")
initialize_app(cred, {"databaseURL": "https://resubot-ad708-default-rtdb.asia-southeast1.firebasedatabase.app", 'storageBucket': 'resubot-ad708.appspot.com'})
import uuid

# Reference to the root of the database
ref = db.reference('/')

def add(add_data, candidate1):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(candidate1.filename)
        candidate1.file.seek(0)
        blob.upload_from_file(candidate1.file)
        expiration_time = datetime.utcnow() + timedelta(hours=24)
        pdf_url = blob.generate_signed_url(expiration=expiration_time)
        
        data_to_store = {
            'pdf_url': pdf_url,
            **add_data,
        }
        new_ref = ref.push(data_to_store)
        return data_to_store
    except Exception as e:
        return str(e)



def delete(child_key):
    try:
        child_ref = ref.child(child_key)
        child_ref.delete()
        return f"Child with key {child_key} deleted successfully"
    except Exception as e:
        return str(e)

def fetch_all_data():
    try:
        snapshot = ref.get()
        if snapshot is not None:
            all_data = {}
            for key, value in snapshot.items():
                all_data[key] = value
            return all_data
        else:
            return None
    except Exception as e:
        return str(e)
