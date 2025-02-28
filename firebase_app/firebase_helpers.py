import firebase_admin
from firebase_admin import credentials, auth
from .models import UserDB
import os

# Initialize Firebase
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred = credentials.Certificate(os.path.join(BASE_DIR, 'firebase_app', 'firebase_config.json'))
firebase_admin.initialize_app(cred)

# Fetch users from Firebase
def fetch_firebase_users():
    users = []
    page = auth.list_users()
    while page:
        for user in page.users:
            users.append({
                'id': user.uid,
                'name': user.display_name or 'Anonymous',
                'imgurl': user.photo_url or '',
                'email': user.email,
            })
        page = page.get_next_page()
    return users

# Post users to the database
def post_to_users_db(firebase_users):
    for user_data in firebase_users:
        UserDB.objects.update_or_create(
            id=user_data['id'],
            defaults={
                'name': user_data['name'],
                'imgurl': user_data['imgurl'],
                'email': user_data['email'],
            }
        )

# Function to create a custom token with extended expiration (24 hours)
def create_custom_token(uid, expiration=86400):
  
    custom_token = auth.create_custom_token(uid)
    return custom_token
