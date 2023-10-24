from django.shortcuts import render
from django.views.generic import TemplateView
import requests

# Create your views here.


def access_token(id):
    # Weavy API endpoint for getting an access token
    weavy_api_url = f"https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/users/{id}/tokens"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'

    # Your Weavy API authentication token or credentials
    headers = {
      "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Send a POST request to get the access token
        response = requests.post(weavy_api_url, headers=headers)

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            print(access_token)
            return access_token
        else:
            print(f"Failed to get access token. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    

def initialise_chat(id):
    weavy_api_url = "https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/apps/init"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'

    # Your Weavy API authentication token or credentials
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Data for initializing the app
    app_data = {
        "app": {
            "uid": id,
          
            "type": "Chat",
        },
        'user': {
            'uid':id,
            # 'uid': 'c89943e8-3a0b-4426-a488-063955102e1b',
        }
        
    }

    try:
        # Send a POST request to initialize the app
        response = requests.post(weavy_api_url, json=app_data, headers=headers)
        print(response.json(),'\n\n\n\n\n')

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 200:
            print("App initialized successfully.")
        else:
            print(f"Failed to initialize app. Status code: {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
  

def support_initialise_chat(id, member):
    weavy_api_url = "https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/apps/init"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'


    # Your Weavy API authentication token or credentials
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Data for initializing the app
    app_data = {
        "app": {
            "uid": id,
          
            "type": "Chat"
        },
        'user':{
            # 'uid': member,
            'uid':id,

        }
        
    }

    try:
        # Send a POST request to initialize the app
        response = requests.post(weavy_api_url, json=app_data, headers=headers)
        print(response.json(),'\n\n\n\n\n', 'APp iniYia')

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 200:
            print("App initialized successfully.")
        else:
            print(f"Failed to initialize app. Status code: {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
  
def add_chat_member(chat_id,member):



    weavy_api_url = "https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/apps/init"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'

    # Your Weavy API authentication token or credentials
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Data for initializing the app
    app_data = {
        "app": {
            "uid": chat_id,
          
            "type": "Chat",
        },
        'user': {
            'uid':chat_id,
            'uid': member,
        }
        
    }

    try:
        # Send a POST request to initialize the app
        response = requests.post(weavy_api_url, json=app_data, headers=headers)
        print(response.json(),'\n\n\n\n\n')

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 200:
            print("App initialized successfully.")
        else:
            print(f"Failed to initialize app. Status code: {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def index(request):
    return render(request, "Support/index.html")


def create_user(uuid):

    weavy_api_url = f"https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/users/{uuid}"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'

    # Your Weavy API authentication token or credentials
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # User data to be updated (name field)
    user_data = {
        "name": uuid,
    }
   

    try:
        # Send a PUT request to update the user
        response = requests.put(weavy_api_url, json=user_data, headers=headers)

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 201 :
            print("User updated successfully.")

        elif response.status_code ==200:
            print('User found and updated')
            
         
        else:
            print(f"Failed to update user. Status code: {response.status_code}")
            print(response.text)

           

    except requests.exceptions.RequestException as e:
        print(str(e))


def room(request):
    weavy_api_url = f"https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/users/{request.user.uuid}"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'


    # Your Weavy API authentication token or credentials
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # User data to be updated (name field)
    user_data = {
        "name": request.user.email
    }
    

    try:
        # Send a PUT request to update the user
        response = requests.put(weavy_api_url, json=user_data, headers=headers)

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 201 :
            print("User creaated successfully.")
            initialise_chat(request.user.uuid)
            acces = access_token(request.user.uuid)
            request.session['access_token'] = acces
        elif response.status_code == 200:
            print(f"User updated successfully: {response.status_code}")
            initialise_chat(request.user.uuid)
            acces = access_token(request.user.uuid)
            request.session['access_token'] = acces

    except requests.exceptions.RequestException as e:
        print(str(e))
    return render(request, "Support/room.html")


def chats(request):
    

    # Weavy API endpoint for user creation
    weavy_api_url = "https://ced0667cb8b14d76ba02bf7764860ddc.weavy.io/api/apps"
    token = 'wys_MEQ4Z1gWe6QUXK30fm7L6FL72R84ZS406oSm'

    


        # Your Weavy API authentication token or credentials
      
    # Your Weavy API authentication token or credentials
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Send a GET request to list conversations
        response = requests.get(weavy_api_url, headers=headers)

        # Check if the request was successful (status code 200 for OK)
        if response.status_code == 200:
            conversations = response.json()
            
            if conversations['data']:
                conversations = conversations['data']
                print(conversations, '\n\n\n\n\n')
            else:
                conversations = ['There are no available conversations']
        else:
            print(f"Failed to list conversations. Status code: {response.status_code}")
            print(response.text)
            conversations = ['None',]

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return render(request, "Support/chats.html", {'chats':conversations})


def room_support(request, chat_id):
    print('\n\n\n\n\n')
    create_user(request.user.uuid)
    initialise_chat(request.user.uuid)
    add_chat_member(chat_id, request.user.uuid)
    # support_initialise_chat(request.user.uuid, chat_id)
    a_token = access_token(request.user.uuid)
    
    request.session['access_token'] = a_token
    print(request.session.get('access_token'))

    return render(request, "Support/room_support.html", {'chat_id':chat_id})
