
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import status
from webserviceApp.models import ProviderService
from webserviceApp.serializers import ProviderServiceSerializer, UserSerializer
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from .models import BookingHistory, User
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now
import datetime
from datetime import datetime, timedelta
from django.utils.timezone import now

from django.db import models

#---------------------------------------------------------------------------
# For Provider Services - 


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def create_service(request):
    serializer = ProviderServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def get_service(request, _id):
    try:
        service = ProviderService.objects.get(_id=(ObjectId(_id)))
    except ProviderService.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProviderServiceSerializer(service)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def update_service(request, _id):
    try:
        service = ProviderService.objects.get(_id=(ObjectId(_id)))
    except ProviderService.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Fetch old image and video paths
    old_image_path = service.image.name if service.image else None
    old_video_path = service.video.name if service.video else None

    # Parse incoming data
    new_image = request.FILES.get('image')
    new_video = request.FILES.get('video')

    # Compare and delete old image if a new one is uploaded and different
    if new_image and old_image_path and old_image_path != new_image.name:
        default_storage.delete(old_image_path)

    # Compare and delete old video if a new one is uploaded and different
    if new_video and old_video_path and old_video_path != new_video.name:
        default_storage.delete(old_video_path)

    serializer = ProviderServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_service(request, _id):
    try:
        service = ProviderService.objects.get(_id=(ObjectId(_id)))
    except ProviderService.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Delete associated media files before deleting the service entry
    if service.image:
        default_storage.delete(service.image.name)
    if service.video:
        default_storage.delete(service.video.name)

    service.delete()
    return Response({'message': "Deleted Data Successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def list_services(request):
    services = ProviderService.objects.all()
    serializer = ProviderServiceSerializer(services, many=True)
    return Response(serializer.data)


# -----------------------------------------------------------------------------

# Register a user
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(): 
        serializer.save()
        return Response({'message': "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login a user (session-based)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    selected_role = request.data.get('role')

    try:
        # Find the user by username
        user = User.objects.get(username=username)
        
        if check_password(password, user.password):
            # Check if the selected role matches the user's actual role
            if selected_role == user.role:
                
                if user.role == 'admin':
                    panel = 'Admin Dashboard'
                elif user.role == 'provider':
                    panel = 'Provider Dashboard'
                elif user.role == 'client':
                    panel = 'Client Dashboard'
                else:
                    return Response({'error': 'Invalid role'}, status=status.HTTP_403_FORBIDDEN)
                
                return Response({
                    'message': 'Login successful',
                    'role': user.role,
                    'redirect_to': panel
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Selected role does not match'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# For logOut -
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        request.auth.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Something went wrong during logout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#---------------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def search_services(request):
    query = request.GET.get("query", "").strip().lower()  # Convert to lowercase for consistency
    if not query:
        return Response({"error": "Please provide a search term"}, status=400)

    services = ProviderService.objects.filter(service_type=query)  # Exact match on service_type
    service_list = list(services.values())

    if not service_list:
        return Response({"message": "No matching services found"}, status=404)

    serializer = ProviderServiceSerializer(services, many=True)  # Serialize the queryset
    return Response({"services": serializer.data})



@api_view(["POST"])
@permission_classes([AllowAny])
def book_service(request):
    service_id = request.data.get("service_id")
    user_name = request.data.get("user_name")

    if not service_id or not user_name:
        return Response({"error": "Service ID and User Name are required"}, status=400)

    try:
        service = ProviderService.objects.get(_id=ObjectId(service_id))
    except ProviderService.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)

    # Allow booking only within the service's defined time slot
    current_time = now().time()
    if service.time_slot:
        try:
            start_time_str, end_time_str = service.time_slot.split("-")
            start_time = datetime.strptime(start_time_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_time_str.strip(), "%H:%M").time()

            if not (start_time <= current_time <= end_time):
                return Response({
                    "error": f"Service is only available between {start_time_str} and {end_time_str}"},
                    status=400
                )
        except ValueError:
            return Response({"error": "Invalid time slot format. Use HH:MM-HH:MM"}, status=400)

    # Save the booking request in the BookingHistory model
    BookingHistory.objects.create(
        user_name=user_name,
        service_name=service.name,
        service_type=service.service_type
    )

    return Response({"message": "Booking request has been successfully submitted."}, status=201)


class ProviderService(models.Model):
    _id = models.ObjectIdField(default=ObjectId, primary_key=True)

    SERVICE_TYPES = [
        ('plumbing', 'plumbing'),
        ('electrical', 'electrical'), 
    ]    

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add image and video fields
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    video = models.FileField(upload_to='service_videos/', blank=True, null=True)
    time_slot = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.get_service_type_display()}"

    class Meta:
        db_table = 'Provider_services'
