from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from baseapp.models import Room
from .serilizers import RoomSerializer
from django.http import JsonResponse


@api_view(['GET'])
def getRoute(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/room/:id',
        'GET /api/room/search?query=example'
    ]

    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    print(RoomSerializer)
    return Response(serializer.data)


@api_view(['GET'])
def getRoomById(request, pk):
    try:
        room = Room.objects.get(id=pk)
        serializer = RoomSerializer(room, many=False)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist'})


@api_view(['GET'])
def searchRoom(request):
    query = request.GET.get('query', '')
    rooms = Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)
