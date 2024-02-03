from django.shortcuts import render , redirect
from django.http import JsonResponse

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone

import google.generativeai as genai
# Create your views here.

GOOGLE_API_KEY = "AIzaSyBTLWHHb0wPqhqFEsASMJXFDPlSoxL27zk"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])


def ai(prompt):
    # response = model.generate_content(prompt, stream=True)
    response = chat.send_message(prompt, stream=True)

    response.resolve()
    return response.text


def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if (request.method == 'POST'):
        message = request.POST.get('message')
        response = ai(message)

        chat = Chat(user=request.user,message=message,response=response,created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html',{'chats':chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error = 'username or password is wrong'
            return render(request,'login.html',{'error_message':error})
    else:        
         return render(request, 'login.html')


def register(request):
    if (request.method=='POST'):
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            try:
                user = User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error = 'error creating account'
                return render(request,'register.html',{'error_message':error})
        else:
            error = 'passwords dont match'
            return render(request,'register.html',{'error_message':error})

    return render(request, 'register.html')
        

def logout(request):
    auth.logout(request)
    return redirect('login')