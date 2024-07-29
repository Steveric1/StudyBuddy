from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
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
        
    context = {'page': page}
    return render(request, 'baseapp/login_register.html', context)


def logoutView(request):
    logout(request)
    return redirect('home')


def registerView(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
            
    return render(request, 'baseapp/login_register.html', context={'form': form})

def home(request):
    query = request.GET.get('q')
    rooms = Room.objects.all()
    
    if query is not None:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=query) |
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        rooms
        
    topics = Topic.objects.all()
    room_count = rooms.count()
    context = {
        'rooms': rooms, 
        'topics': topics,
        'room_count': room_count
    }
    return render(request, 'baseapp/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    print(participants)
    
    if request.method == 'POST':
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'baseapp/room.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('home')
            except Exception as e:
                print(f"Error saving form: {str(e)}")

    context = {'form': form}
    return render(request, 'baseapp/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            try:
                form.save()
                return redirect('home')
            except Exception as e:
                print(f"Error updating form: {str(e)}")

    context = {'form': form}
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
