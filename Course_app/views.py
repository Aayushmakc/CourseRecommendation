from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .utils import send_welcome_email

class SignupView(APIView):
    """
    API endpoint for user registration.
    
    Accepts POST requests with the following fields:
    * first_name
    * last_name
    * email
    * phone_number (must start with +977)
    * password (minimum 8 characters)
    """
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = SignupSerializer  # Required for browseable API

    def post(self, request):
        """Create a new user account and log them in."""
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            
            # Send welcome email
            try:
                send_welcome_email(user.email, user.first_name)
            except Exception as e:
                print(f"Failed to send welcome email: {str(e)}")
            
            return Response({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API endpoint for user login.
    
    Accepts POST requests with:
    * email
    * password
    """
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = LoginSerializer  # Required for browseable API

    def post(self, request):
        """Authenticate user and create session."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                return Response({
                   'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                })
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)