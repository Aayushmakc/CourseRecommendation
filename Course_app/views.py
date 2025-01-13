# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import authenticate
# from .serializers import SignupSerializer

# class SignupView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = SignupSerializer(data=request.data)

     
#         if serializer.is_valid():
#             serializer.save()  
#             return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username=username, password=password)
#         if user:
#             return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
#         return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate
# from .serializers import SignupSerializer, LoginSerializer

# class SignupView(APIView):
#     def post(self, request):
#         serializer = SignupSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             token, _ = Token.objects.get_or_create(user=user)
#             return Response({
#                 'token': token.key,
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(
#                 username=serializer.validated_data['email'],
#                 password=serializer.validated_data['password']
#             )
#             if user:
#                 token, _ = Token.objects.get_or_create(user=user)
#                 return Response({
#                     'token': token.key,
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
# from django.contrib.auth import authenticate, login
# from .serializers import SignupSerializer, LoginSerializer

# class SignupView(APIView):
#     def post(self, request):
#         serializer = SignupSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             login(request, user)  # Log the user in after signup
#             return Response({
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(
#                 username=serializer.validated_data['email'],
#                 password=serializer.validated_data['password']
#             )
#             if user:
#                 login(request, user)  
#                 return Response({
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





from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

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