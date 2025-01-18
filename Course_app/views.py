


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer
from .utils import send_welcome_email
from rest_framework.permissions import AllowAny
from .recommendation_service import CourseRecommender

class SignupView(APIView):
    """
    API endpoint for user registration.
    """
    permission_classes = [AllowAny]
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

                print('Login Response:', {  
                    'user': user.email,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                })

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
    






class CourseSearchView(APIView):
    def __init__(self):
        super().__init__()
        self.recommender = CourseRecommender()

    def get(self, request):
        query = request.query_params.get('query', '')
        difficulty = request.query_params.get('difficulty')
        min_rating = request.query_params.get('min_rating')

        if not query:
            return Response({
                'error': 'Please provide a search query'
            }, status=400)

        try:
            recommendations = self.recommender.get_recommendations(
                query,
                difficulty_level=difficulty,
                min_rating=min_rating
            )
            
            return Response({
                'results': recommendations
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=500)