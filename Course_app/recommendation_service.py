import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from nltk.stem import WordNetLemmatizer
import nltk

class CourseRecommender:
    def __init__(self):
        # Load and prepare data
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Coursera.csv')
        self.df = pd.read_csv(csv_path)
        self.prepare_data()
        self.vectorizer = CountVectorizer(max_features=10000, stop_words='english')
        self.vectors = None
        self.lemmatizer = WordNetLemmatizer()

    def prepare_data(self):
        features_selected = ["Course_Name", "Course_Description", "Skills", 
                           "Difficulty_Level", "Course_Rating"]
        self.new_df = self.df[features_selected]
        
        # Create description keywords
        self.new_df["description_key_words"] = self.new_df[features_selected].apply(
            lambda x: ' '.join(str(x)), axis=1
        )
        
        # Preprocess text
        self.new_df["description_key_words"] = self.new_df["description_key_words"].apply(
            self.preprocess_text
        )
        
        # Create vectors
        self.vectors = self.vectorizer.fit_transform(
            self.new_df["description_key_words"]
        ).toarray()

    def preprocess_text(self, text):
        # Your existing PreprocessTexte function
        cleaned_text = re.sub(r'-',' ',text)
        cleaned_text = re.sub(r'https?://\S+|www\.\S+|http?://\S+',' ',cleaned_text)
        # ... rest of your preprocessing steps
        return cleaned_text

    def get_recommendations(self, query, difficulty_level=None, min_rating=None):
        # Preprocess query
        processed_query = self.preprocess_text(query)
        
        # Filter courses
        filtered_df = self.filter_courses(difficulty_level, min_rating)
        
        # Get recommendations
        recommendations = self.get_similar_courses(
            processed_query, 
            filtered_df, 
            num_recommendations=10
        )
        
        return recommendations

    def filter_courses(self, difficulty_level=None, min_rating=None):
        filtered_df = self.new_df.copy()
        
        if difficulty_level:
            filtered_df = filtered_df[
                filtered_df['Difficulty_Level'].str.lower() == difficulty_level.lower()
            ]
            
        if min_rating:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df['Course_Rating']) >= float(min_rating)
            ]
            
        return filtered_df

    def get_similar_courses(self, query, filtered_df, num_recommendations=10):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        similar_indices = similarities.argsort()[::-1][:num_recommendations]
        
        recommendations = []
        for idx in similar_indices:
            course = filtered_df.iloc[idx]
            recommendations.append({
                'name': course['Course_Name'],
                'rating': course['Course_Rating'],
                'difficulty': course['Difficulty_Level']
            })
            
        return recommendations