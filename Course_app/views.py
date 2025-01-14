# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from django.contrib.auth import authenticate, login
# from .serializers import SignupSerializer, LoginSerializer
# from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
# from .utils import send_welcome_email

# class SignupView(APIView):
#     """
#     API endpoint for user registration.
    
#     Accepts POST requests with the following fields:
#     * first_name
#     * last_name
#     * email
#     * phone_number (must start with +977)
#     * password (minimum 8 characters)
#     """
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     serializer_class = SignupSerializer  # Required for browseable API

#     def post(self, request):
#         """Create a new user account and log them in."""
#         serializer = SignupSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             login(request, user)
            
#             # Send welcome email
#             try:
#                 send_welcome_email(user.email, user.first_name)
#             except Exception as e:
#                 print(f"Failed to send welcome email: {str(e)}")
            
#             return Response({
#                 'message': 'User created successfully',
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     """
#     API endpoint for user login.
    
#     Accepts POST requests with:
#     * email
#     * password
#     """
#     parser_classes = (JSONParser, FormParser, MultiPartParser)
#     serializer_class = LoginSerializer  # Required for browseable API

#     def post(self, request):
#         """Authenticate user and create session."""
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(
#                 username=serializer.validated_data['email'],
#                 password=serializer.validated_data['password']
#             )
#             if user:
#                 login(request, user)
#                 return Response({
#                    'message': 'Login successful',
#                     'user': {
#                         'id': user.id,
#                         'email': user.email,
#                         'first_name': user.first_name,
#                         'last_name': user.last_name
#                     }
#                 })
#             return Response(
#                 {'error': 'Invalid credentials'}, 
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User  # Using default User model
# from rest_framework_simplejwt.tokens import RefreshToken
# from .serializers import SignupSerializer, LoginSerializer
# from .utils import send_welcome_email

# class SignupView(APIView):
#     """
#     API endpoint for user registration using default User model.
#     """
#     def post(self, request):
#         serializer = SignupSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             refresh = RefreshToken.for_user(user)
            
#             # Send welcome email
#             try:
#                 send_welcome_email(user.email, user.first_name)
#             except Exception as e:
#                 print(f"Failed to send email: {str(e)}")
            
#             return Response({
#                 'message': 'User created successfully',
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name,
#                     'is_staff': user.is_staff  # For admin access
#                 },
#                 'tokens': {
#                     'access': str(refresh.access_token),
#                     'refresh': str(refresh)
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     """
#     API endpoint for user login using default User model.
#     """
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(
#                 username=serializer.validated_data['email'],
#                 password=serializer.validated_data['password']
#             )
#             if user:
#                 refresh = RefreshToken.for_user(user)
#                 return Response({
#                     'message': 'Login successful',
#                     'user': {
#                         'id': user.id,
#                         'email': user.email,
#                         'first_name': user.first_name,
#                         'last_name': user.last_name,
#                         'is_staff': user.is_staff  # For admin access
#                     },
#                     'tokens': {
#                         'access': str(refresh.access_token),
#                         'refresh': str(refresh)
#                     }
#                 })
#             return Response(
#                 {'error': 'Invalid credentials'}, 
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserProfileView(APIView):
#     """
#     API endpoint for viewing user profile.
#     Requires JWT authentication.
#     """
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
#         return Response({
#             'user': {
#                 'id': user.id,
#                 'email': user.email,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'is_staff': user.is_staff,
#                 'date_joined': user.date_joined
#             }
#         })




from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer
from .utils import send_welcome_email

class SignupView(APIView):
    """
    API endpoint for user registration.
    """
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = SignupSerializer  

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)  
            refresh = RefreshToken.for_user(user)
            
            # Send welcome email
            try:
                send_welcome_email(user.email, user.first_name)
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
            
            return Response({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API endpoint for user login.
    """
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = LoginSerializer  

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                })
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)