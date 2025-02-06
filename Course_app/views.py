from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer
from .utils import send_welcome_email
from .utils import filter_dataframe_function
from .utils import recommend_courses
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models import Course, UserProfile
import pandas as pd
import numpy as np
from .utils import PreprocessTexte, CustomTFIDFVectorizer, clean_and_process_data, books_id_recommended


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


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import pandas as pd
from .models import Course, UserProfile
from .serializers import CourseSerializer, UserProfileSerializer
from .utils import (
    CustomTFIDFVectorizer, PreprocessTexte, 
    filter_dataframe_function, books_id_recommended,
    process_user_profile, recommend_courses,
    cosine_similarity, clean_and_process_data
)

class SearchCourseView(APIView):
    def post(self, request):
        # Get parameters from request
        name = request.data.get('name', '')
        description = request.data.get('description', '')
        difficulty_level = request.data.get('difficulty_level')
        min_rating = request.data.get('min_rating')

        try:
            # Convert queryset to DataFrame
            queryset = Course.objects.all()
            df = pd.DataFrame.from_records(
                queryset.values('course_id', 'name', 'university', 'difficulty', 'rating', 'url', 'description')
            )
            
            # Clean data
            df = clean_and_process_data(df)
            recommended_df = df.copy()
            
            # Search by text (name or description) if provided
            if name or description:
                search_text = []
                if name:
                    search_text.append(name)
                if description:
                    search_text.append(description)
                    
                # Create search_text_field with more weight on course name
                df["search_text_field"] = df.apply(
                    lambda x: ' '.join([
                        # Add name multiple times to give it more weight
                        str(x['name']) * 3,
                        str(x['description']),
                        str(x['university'])
                    ]), 
                    axis=1
                )
                df["search_text_field"] = df["search_text_field"].apply(PreprocessTexte)
                
                # Get recommendations based on text search
                vectorizer = CustomTFIDFVectorizer(max_features=10000, stop_words='english')
                vectors = vectorizer.fit_transform(df["search_text_field"])
                search_query = ' '.join(search_text)
                recommended_indices = books_id_recommended(
                    search_query, 
                    vectorizer, 
                    vectors, 
                    number_of_recommendation=50
                )
                recommended_df = df.iloc[recommended_indices]
            
            # Filter by difficulty level if provided
            if difficulty_level:
                valid_difficulties = ["beginner", "intermediate", "advanced"]
                if difficulty_level.lower() in valid_difficulties:
                    recommended_df = recommended_df[
                        recommended_df['difficulty'].str.lower() == difficulty_level.lower()
                    ]
            
            # Filter by minimum rating if provided
            if min_rating is not None:
                try:
                    min_rating = float(min_rating)
                    recommended_df = recommended_df[recommended_df['rating'] >= min_rating]
                except (ValueError, TypeError):
                    pass
            
            if recommended_df.empty:
                return Response(
                    {"message": "No courses found matching your criteria"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Format response
            recommendations = []
            for _, course in recommended_df.iterrows():
                try:
                    recommendations.append({
                        'course_id': int(course.get('course_id', 0)),
                        'name': str(course.get('name', '')),
                        'university': str(course.get('university', '')),
                        'difficulty': str(course.get('difficulty', '')),
                        'rating': float(course.get('rating', 0.0)) if pd.notnull(course.get('rating')) else 0.0,
                        'url': str(course.get('url', '')),
                        'description': str(course.get('description', ''))
                    })
                except Exception as e:
                    print(f"Error formatting course: {e}")
                    print("Course data:", course)
            
            return Response({
                'recommendations': recommendations
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContentBasedRecommenderView(APIView):
    """
    API endpoint for getting personalized course recommendations based on user profile.
    
    post:
    Get personalized recommendations for a specific user.
    
    Parameters:
        - user_id: ID of the user to get recommendations for
    """
    
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get user profile from database
            user_profiles = UserProfile.objects.filter(user_id=user_id)
            if not user_profiles.exists():
                return Response(
                    {"error": f"No profile found for user {user_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Convert to DataFrame for processing
            user_df = pd.DataFrame.from_records(user_profiles.values())
            
            # Get all courses
            queryset = Course.objects.all()
            df = pd.DataFrame.from_records(
                queryset.values('course_id', 'name', 'university', 'difficulty', 'rating', 'url', 'description')
            )
            
            # Clean data
            df = clean_and_process_data(df)
            
            # Create text field for similarity comparison
            df["search_text_field"] = df.apply(
                lambda x: ' '.join([
                    str(x['name']) * 3,  # Give more weight to name
                    str(x['description']),
                    str(x['university'])
                ]), 
                axis=1
            )
            df["search_text_field"] = df["search_text_field"].apply(PreprocessTexte)
            
            # Create user profile text
            user_interests = ' '.join([
                str(user_df['course_name'].iloc[0]),
                str(user_df['course_description'].iloc[0]),
                str(user_df['skills'].iloc[0])
            ])
            
            # Get recommendations based on user profile
            vectorizer = CustomTFIDFVectorizer(max_features=10000, stop_words='english')
            vectors = vectorizer.fit_transform(df["search_text_field"])
            recommended_indices = books_id_recommended(
                user_interests,
                vectorizer,
                vectors,
                number_of_recommendation=10
            )
            
            # Get recommended courses
            recommended_df = df.iloc[recommended_indices]
            
            # Format response
            recommendations = []
            for _, course in recommended_df.iterrows():
                try:
                    recommendations.append({
                        'course_id': int(course.get('course_id', 0)),
                        'name': str(course.get('name', '')),
                        'university': str(course.get('university', '')),
                        'difficulty': str(course.get('difficulty', '')),
                        'rating': float(course.get('rating', 0.0)) if pd.notnull(course.get('rating')) else 0.0,
                        'url': str(course.get('url', '')),
                        'description': str(course.get('description', ''))
                    })
                except Exception as e:
                    print(f"Error formatting course: {e}")
                    print("Course data:", course)
            
            return Response({
                'recommendations': recommendations
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in recommendations: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """
    API endpoint for managing user profiles.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create a new user profile"""
        try:
            # Get data from request
            user_id = request.data.get('user_id')
            course_id = request.data.get('course_id')
            
            if not user_id or not course_id:
                return Response(
                    {"error": "Both user_id and course_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the course
            try:
                course = Course.objects.get(course_id=course_id)
            except Course.DoesNotExist:
                return Response(
                    {"error": f"Course with id {course_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create user profile
            profile_data = {
                'user_id': user_id,
                'course': course,
                'course_name': request.data.get('course_name', course.name),
                'course_description': request.data.get('course_description', course.description),
                'skills': request.data.get('skills', course.skills),
                'difficulty_level': request.data.get('difficulty_level', course.difficulty),
                'course_rating': request.data.get('course_rating', course.rating)
            }
            
            # Create the profile
            profile = UserProfile.objects.create(**profile_data)
            
            return Response({
                'message': 'Profile created successfully',
                'profile': {
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'course_name': profile.course_name,
                    'course_description': profile.course_description,
                    'skills': profile.skills,
                    'difficulty_level': profile.difficulty_level,
                    'course_rating': profile.course_rating
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error creating profile: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get user profiles"""
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            profiles = UserProfile.objects.filter(user_id=user_id)
            if not profiles.exists():
                return Response(
                    {"error": f"No profiles found for user {user_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            profiles_data = []
            for profile in profiles:
                profiles_data.append({
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'course_name': profile.course_name,
                    'course_description': profile.course_description,
                    'skills': profile.skills,
                    'difficulty_level': profile.difficulty_level,
                    'course_rating': profile.course_rating
                })
            
            return Response({
                'profiles': profiles_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error getting profiles: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseInteractionView(APIView):
    """
    API endpoint for tracking user interactions with courses.
    This automatically creates/updates user profiles based on their interactions.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            course_id = request.data.get('course_id')
            interaction_type = request.data.get('interaction_type')  # 'view', 'rate'
            rating = request.data.get('rating')  # only for 'rate' interaction
            
            if not all([user_id, course_id, interaction_type]):
                return Response(
                    {"error": "user_id, course_id, and interaction_type are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the course
            try:
                course = Course.objects.get(course_id=course_id)
            except Course.DoesNotExist:
                return Response(
                    {"error": f"Course with id {course_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create or get user profile
            profile = UserProfile.objects.filter(
                user_id=user_id,
                course=course
            ).first()
            
            if not profile:
                # Create new profile
                profile = UserProfile.objects.create(
                    user_id=user_id,
                    course=course,
                    course_name=course.name,
                    course_description=course.description,
                    skills=course.skills,
                    difficulty_level=course.difficulty,
                    course_rating=rating if rating is not None else course.rating
                )
            elif interaction_type == 'rate' and rating is not None:
                # Update rating for existing profile
                profile.course_rating = rating
                profile.save()
            
            return Response({
                'message': 'Interaction recorded successfully',
                'profile': {
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'course_name': profile.course_name,
                    'skills': profile.skills,
                    'difficulty_level': profile.difficulty_level,
                    'course_rating': profile.course_rating
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error recording interaction: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )