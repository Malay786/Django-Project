from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Message
from django.contrib.auth.models import User
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib import messages     #flash messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# Create your views here.


def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
          user = User.objects.get(username=username)
        except:
            messages.error(request, "user does not exist.")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, "username or password does not exist.")

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
          user = form.save(commit=False)    # creates user object but doesn't save to DB yet
          user.username = user.username.lower()   #converts username to lowercase
          user.save()
          login(request, user)
          return redirect('home')
        
        else:
            messages.error(request, 'An error occurred during registration')


    return render(request, 'base/login_register.html', {'form':form})



def home(request):

    #search functionality 
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
        )
    topics = Topic.objects.all()[0:5]   #only give first five topics
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context= {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)



@login_required(login_url='login')   #redirect back to the login page
# @ - decorators
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic=topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
            
        )

        # form = RoomForm(request.POST)   #add the data to the form variable
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') 
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)   #this is how we get our form prefilled for update
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!")
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') 
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!")

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login') 
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Your are not allowed here!")

    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)  # instance=user creates a form pre-filled with the user's current data

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)    #with instance=user django updates the existing user
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)     # use return before redirect everytime

    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q) #filter() with no arguments returns everything (same as .all())
    
    context={'topics': topics}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages= Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})