"""
Machine Learning Disease Classifier for FAI-Farm

Implements a lightweight ML model for crop disease detection using
environmental features and crop health indicators.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
from typing import Dict, Tuple, List
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kr.ontology import DiseaseType


class DiseaseClassifier:
    """
    Machine Learning classifier for crop disease detection.
    
    Uses environmental features (temperature, humidity, water level) and
    crop indicators (growth stage, health status) to predict disease type.
    """
    
    def __init__(self):
        """Initialize the disease classifier."""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.is_trained = False
        self.feature_names = [
            'temperature',
            'humidity',
            'water_level',
            'growth_progress',
            'soil_moisture',
            'days_since_watering',
            'leaf_color_r',
            'leaf_color_g',
            'leaf_color_b'
        ]
        self.disease_labels = {
            0: 'healthy',
            1: DiseaseType.LEAF_SPOT.value,
            2: DiseaseType.POWDERY_MILDEW.value,
            3: DiseaseType.ROOT_ROT.value,
            4: DiseaseType.BLIGHT.value,
            5: DiseaseType.RUST.value
        }
    
    def generate_synthetic_training_data(self, n_samples: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for disease classification.
        
        Args:
            n_samples: Number of samples to generate
        
        Returns:
            Tuple of (features, labels)
        """
        np.random.seed(42)
        
        features = []
        labels = []
        
        for _ in range(n_samples):
            # Generate base features
            temperature = np.random.uniform(10, 40)
            humidity = np.random.uniform(30, 100)
            water_level = np.random.uniform(0, 1)
            growth_progress = np.random.uniform(0, 100)
            soil_moisture = np.random.uniform(0, 1)
            days_since_watering = np.random.randint(0, 10)
            
            # Simulate leaf color (RGB)
            leaf_r = np.random.uniform(50, 200)
            leaf_g = np.random.uniform(100, 255)
            leaf_b = np.random.uniform(50, 150)
            
            # Determine disease based on conditions
            disease = 0  # healthy by default
            
            # Leaf Spot: High humidity + moderate temperature
            if humidity > 80 and 20 < temperature < 30 and np.random.random() > 0.3:
                disease = 1
                leaf_r += 30  # Brownish spots
                leaf_g -= 20
            
            # Powdery Mildew: Moderate humidity + cool temperature
            elif 60 < humidity < 80 and 15 < temperature < 25 and np.random.random() > 0.4:
                disease = 2
                leaf_r += 50  # White powder
                leaf_g += 50
                leaf_b += 50
            
            # Root Rot: Excessive water + poor drainage
            elif water_level > 0.9 and soil_moisture > 0.9 and np.random.random() > 0.3:
                disease = 3
                leaf_g -= 50  # Yellowing
                leaf_r += 20
            
            # Blight: High humidity + warm temperature
            elif humidity > 85 and temperature > 28 and np.random.random() > 0.4:
                disease = 4
                leaf_r -= 30  # Dark spots
                leaf_g -= 40
                leaf_b -= 20
            
            # Rust: Moderate conditions + stress
            elif days_since_watering > 5 and water_level < 0.3 and np.random.random() > 0.5:
                disease = 5
                leaf_r += 60  # Rust color
                leaf_g -= 10
                leaf_b -= 30
            
            features.append([
                temperature, humidity, water_level, growth_progress,
                soil_moisture, days_since_watering, leaf_r, leaf_g, leaf_b
            ])
            labels.append(disease)
        
        return np.array(features), np.array(labels)
    
    def train(self, X: np.ndarray = None, y: np.ndarray = None):
        """
        Train the disease classifier.
        
        Args:
            X: Feature matrix (if None, generates synthetic data)
            y: Label vector (if None, generates synthetic data)
        """
        if X is None or y is None:
            print("Generating synthetic training data...")
            X, y = self.generate_synthetic_training_data(n_samples=10000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training on {len(X_train)} samples...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Training accuracy: {train_score:.3f}")
        print(f"Testing accuracy: {test_score:.3f}")
        
        # Detailed evaluation
        y_pred = self.model.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=list(self.disease_labels.values())))
        
        return train_score, test_score
    
    def predict(self, features: Dict[str, float]) -> Tuple[str, float]:
        """
        Predict disease from environmental features.
        
        Args:
            features: Dictionary of feature values
        
        Returns:
            Tuple of (disease_name, confidence)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Extract features in correct order
        feature_vector = np.array([[
            features.get('temperature', 25),
            features.get('humidity', 60),
            features.get('water_level', 0.5),
            features.get('growth_progress', 50),
            features.get('soil_moisture', 0.5),
            features.get('days_since_watering', 2),
            features.get('leaf_color_r', 100),
            features.get('leaf_color_g', 180),
            features.get('leaf_color_b', 100)
        ]])
        
        # Predict
        prediction = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]
        confidence = probabilities[prediction]
        
        disease_name = self.disease_labels[prediction]
        
        return disease_name, confidence
    
    def predict_batch(self, features_list: List[Dict]) -> List[Tuple[str, float]]:
        """
        Predict diseases for multiple samples.
        
        Args:
            features_list: List of feature dictionaries
        
        Returns:
            List of (disease_name, confidence) tuples
        """
        results = []
        for features in features_list:
            disease, confidence = self.predict(features)
            results.append((disease, confidence))
        return results
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))
    
    def save_model(self, filepath: str):
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'disease_labels': self.disease_labels
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the saved model
        """
        data = joblib.load(filepath)
        self.model = data['model']
        self.feature_names = data['feature_names']
        self.disease_labels = data['disease_labels']
        self.is_trained = True
        print(f"Model loaded from {filepath}")
    
    def explain_prediction(self, features: Dict[str, float]) -> Dict:
        """
        Explain a prediction with feature contributions.
        
        Args:
            features: Feature dictionary
        
        Returns:
            Dictionary with prediction explanation
        """
        disease, confidence = self.predict(features)
        importance = self.get_feature_importance()
        
        # Get top contributing features
        feature_values = {name: features.get(name, 0) for name in self.feature_names}
        contributions = {
            name: importance[name] * abs(feature_values[name])
            for name in self.feature_names
        }
        
        # Sort by contribution
        sorted_contributions = sorted(
            contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'disease': disease,
            'confidence': confidence,
            'top_factors': sorted_contributions[:3],
            'all_probabilities': self.model.predict_proba(
                np.array([[feature_values[name] for name in self.feature_names]])
            )[0].tolist()
        }


def train_and_save_model(output_path: str = "ml/disease_model.pkl"):
    """
    Train a new disease classifier and save it.
    
    Args:
        output_path: Path to save the trained model
    """
    print("=" * 60)
    print("Training FAI-Farm Disease Classifier")
    print("=" * 60)
    
    classifier = DiseaseClassifier()
    train_acc, test_acc = classifier.train()
    
    print("\nFeature Importance:")
    importance = classifier.get_feature_importance()
    for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {score:.4f}")
    
    # Save model
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    classifier.save_model(output_path)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    
    return classifier


if __name__ == "__main__":
    # Train and save model
    classifier = train_and_save_model()
    
    # Test prediction
    print("\nTesting prediction...")
    test_features = {
        'temperature': 28,
        'humidity': 85,
        'water_level': 0.4,
        'growth_progress': 60,
        'soil_moisture': 0.6,
        'days_since_watering': 3,
        'leaf_color_r': 120,
        'leaf_color_g': 160,
        'leaf_color_b': 90
    }
    
    explanation = classifier.explain_prediction(test_features)
    print(f"\nPredicted Disease: {explanation['disease']}")
    print(f"Confidence: {explanation['confidence']:.2%}")
    print("\nTop Contributing Factors:")
    for factor, contribution in explanation['top_factors']:
        print(f"  {factor}: {contribution:.4f}")
