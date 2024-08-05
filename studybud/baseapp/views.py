from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Let learn Python!'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'}
# ]


def loginView(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page, 'fieldValue': request.POST}
    return render(request, 'baseapp/login_register.html', context)


def logoutView(request):
    logout(request)
    return redirect('home')


def registerView(request):
    context = {
        'fieldValues': request.POST
    }
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password2')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        elif len(password) < 6:
            messages.error(request, 'Password too short')          
        elif password != confirm_password:
            messages.error(request, 'Password did not match')
        else:
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.save()
                
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'An error occurred during registration')
                         
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
        #     user = form.save(commit=False)
        #     user.username = user.username.lower()
        #     user.save()
        #     login(request, user)
        #     return redirect('home')
        # else:
        #     messages.error(request, 'An error occurred during registration')

    return render(request, 'baseapp/login_register.html',  context)


def home(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.all()

    rooms = Room.objects.filter(
        Q(topic__name__icontains=query) |
         Q(name__icontains=query) |
        Q(description__icontains=query)
    )

    topics = Topic.objects.all()[0:4]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=query)
    )

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages':  room_messages
    }
    return render(request, 'baseapp/home.html', context)


@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    print(participants)

    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'baseapp/room.html',  context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.message_set.all()

    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_messages': room_messages,
    }

    return render(request, 'baseapp/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        try:
            Room.objects.create(
                host=request.user,
                topic=topic,
                name=request.POST.get('name'),
                description=request.POST.get('description')
            )
            return redirect('home')
        except Exception as e:
            messages.error(request, 'An unexpected error occurred while creating the room. Please try again later.')
        
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     try:
        #         room = form.save(commit=False)
        #         room.host = request.user
        #         room.save()
        #         return redirect('home')
        #     except Exception as e:
        #         print(f"Error saving form: {str(e)}")

    context = {'form': form, 'topics': topics }
    return render(request, 'baseapp/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        try:
            room.name = request.POST.get('name')
            room.topic = topic
            room.description = request.POST.get('description')
            room.save()
            return redirect('home')
        except Exception as e:
            messages.error(request, 'An unexpected error occurred while updating the room. Please try again later.')
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     try:
        #         form.save()
        #         return redirect('home')
        #     except Exception as e:
        #         print(f"Error updating form: {str(e)}")

    context = {'form': form, 'topics': topics, "room": room}
    return render(request, 'baseapp/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'baseapp/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("you are not allowed to delete this message!")
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'baseapp/delete.html', {'obj': message})


def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    return render(request, 'baseapp/update-user.html', {'form': form})


def topicsView(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=query)
    return render(request, 'baseapp/topics.html', {'topics': topics})


def activitiesView(request):
    # query = request.GET.get('q') if request.GET.get('q') != None else ''
    room_messages = Message.objects.filter()
    return render(request, 'baseapp/activities.html', {'room_messages': room_messages})
