import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import json
from datetime import datetime, timedelta
import os

class LearningAgent:
    """
    Learning Agent: Monitors system performance, compares predictions vs actual outcomes,
    and continuously improves ML models through retraining and feedback loops
    """

    def __init__(self):
        self.model_versions = []
        self.performance_history = []
        self.feedback_data = []
        self.model_path = 'models/reasoning_model.pkl'
        self.load_performance_history()

    def load_performance_history(self):
        """Load historical performance data"""
        try:
            with open('data/learning_history.json', 'r') as f:
                self.performance_history = json.load(f)
        except FileNotFoundError:
            self.performance_history = []

    def save_performance_history(self):
        """Save performance history"""
        with open('data/learning_history.json', 'w') as f:
            json.dump(self.performance_history, f, indent=2)

    def collect_feedback(self, prediction_data, actual_data):
        """Collect prediction vs actual feedback data"""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'predictions': prediction_data,
            'actuals': actual_data,
            'date_range': f"{prediction_data[0]['date']} to {prediction_data[-1]['date']}"
        }

        self.feedback_data.append(feedback_entry)

        # Keep only last 100 entries
        if len(self.feedback_data) > 100:
            self.feedback_data = self.feedback_data[-100:]

        # Save feedback data
        with open('data/feedback_data.json', 'w') as f:
            json.dump(self.feedback_data, f, indent=2)

    def evaluate_predictions(self, predictions, actuals):
        """Evaluate prediction accuracy"""
        if len(predictions) != len(actuals):
            return {'error': 'Mismatched prediction and actual data lengths'}

        pred_values = [p['predicted_patients'] for p in predictions]
        actual_values = actuals

        mae = mean_absolute_error(actual_values, pred_values)
        mse = mean_squared_error(actual_values, pred_values)
        rmse = np.sqrt(mse)

        # Calculate accuracy percentage (lower MAE is better)
        avg_actual = np.mean(actual_values)
        accuracy = max(0, 100 - (mae / avg_actual * 100))

        evaluation = {
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'rmse': round(rmse, 2),
            'accuracy_percentage': round(accuracy, 2),
            'sample_size': len(predictions),
            'evaluation_date': datetime.now().isoformat()
        }

        return evaluation

    def analyze_performance_trends(self):
        """Analyze performance trends over time"""
        if len(self.performance_history) < 2:
            return {'trend': 'insufficient_data'}

        recent_evaluations = self.performance_history[-10:]  # Last 10 evaluations
        accuracies = [eval['accuracy_percentage'] for eval in recent_evaluations]

        # Calculate trend
        if len(accuracies) >= 2:
            slope = np.polyfit(range(len(accuracies)), accuracies, 1)[0]
            if slope > 0.5:
                trend = 'improving'
            elif slope < -0.5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'average_accuracy': round(np.mean(accuracies), 2),
            'best_accuracy': round(max(accuracies), 2),
            'worst_accuracy': round(min(accuracies), 2),
            'consistency': round(np.std(accuracies), 2)
        }

    def retrain_model(self, new_data=None):
        """Retrain ML model with new feedback data"""
        try:
            # Load existing training data
            data = pd.read_csv('data/hospital_data.csv')

            # Add feedback data if available
            if new_data and len(self.feedback_data) > 0:
                feedback_df = self.prepare_feedback_for_training()
                if feedback_df is not None:
                    data = pd.concat([data, feedback_df], ignore_index=True)

            # Prepare features and target
            X = data[['AQI', 'festival_flag', 'epidemic_flag']]
            y = data['patient_count']

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Train new model
            new_model = RandomForestRegressor(n_estimators=100, random_state=42)
            new_model.fit(X_train, y_train)

            # Evaluate new model
            train_score = new_model.score(X_train, y_train)
            test_score = new_model.score(X_test, y_test)

            # Save model with version info
            version = len(self.model_versions) + 1
            model_filename = f'models/reasoning_model_v{version}.pkl'
            joblib.dump(new_model, model_filename)

            # Update current model
            joblib.dump(new_model, self.model_path)

            model_info = {
                'version': version,
                'filename': model_filename,
                'training_date': datetime.now().isoformat(),
                'train_score': round(train_score, 4),
                'test_score': round(test_score, 4),
                'data_size': len(data),
                'feedback_incorporated': len(self.feedback_data) > 0
            }

            self.model_versions.append(model_info)

            return {
                'status': 'success',
                'model_info': model_info,
                'improvement': self.calculate_model_improvement(model_info)
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def prepare_feedback_for_training(self):
        """Prepare feedback data for model retraining"""
        if not self.feedback_data:
            return None

        feedback_rows = []

        for feedback in self.feedback_data[-20:]:  # Use last 20 feedback entries
            predictions = feedback['predictions']
            actuals = feedback['actuals']

            for pred, actual in zip(predictions, actuals):
                # Create synthetic features based on prediction date
                # This is simplified - in reality, you'd have actual environmental data
                feedback_rows.append({
                    'AQI': np.random.randint(50, 300),  # Mock AQI
                    'festival_flag': 1 if 'festival' in pred.get('context', '') else 0,
                    'epidemic_flag': 1 if 'epidemic' in pred.get('context', '') else 0,
                    'patient_count': actual
                })

        return pd.DataFrame(feedback_rows)

    def calculate_model_improvement(self, new_model_info):
        """Calculate improvement over previous model"""
        if len(self.model_versions) < 2:
            return 'first_model'

        previous_model = self.model_versions[-2]
        improvement = new_model_info['test_score'] - previous_model['test_score']

        return round(improvement, 4)

    def identify_model_weaknesses(self):
        """Identify areas where model performance can be improved"""
        weaknesses = []

        # Analyze recent performance
        recent_perf = self.performance_history[-5:] if len(self.performance_history) >= 5 else self.performance_history

        if recent_perf:
            avg_mae = np.mean([p['mae'] for p in recent_perf])

            if avg_mae > 20:
                weaknesses.append('high_prediction_error')
            if len([p for p in recent_perf if p['accuracy_percentage'] < 70]) > 2:
                weaknesses.append('inconsistent_accuracy')
            if self.analyze_performance_trends()['trend'] == 'declining':
                weaknesses.append('performance_declining')

        # Check data quality issues
        if len(self.feedback_data) < 10:
            weaknesses.append('insufficient_feedback_data')

        return weaknesses

    def generate_improvement_recommendations(self):
        """Generate recommendations for model improvement"""
        weaknesses = self.identify_model_weaknesses()
        recommendations = []

        if 'high_prediction_error' in weaknesses:
            recommendations.extend([
                'Increase model complexity (try Gradient Boosting)',
                'Add more environmental features (weather, traffic data)',
                'Implement ensemble methods'
            ])

        if 'inconsistent_accuracy' in weaknesses:
            recommendations.extend([
                'Improve data preprocessing and feature engineering',
                'Add cross-validation during training',
                'Implement model calibration techniques'
            ])

        if 'performance_declining' in weaknesses:
            recommendations.extend([
                'Retrain model with recent data',
                'Check for concept drift in data patterns',
                'Update feature importance analysis'
            ])

        if 'insufficient_feedback_data' in weaknesses:
            recommendations.extend([
                'Collect more prediction-actual pairs',
                'Improve feedback collection system',
                'Implement active learning strategies'
            ])

        return recommendations

    def schedule_retraining(self):
        """Determine if model retraining is needed"""
        if len(self.feedback_data) < 5:
            return {'retrain_needed': False, 'reason': 'insufficient_feedback_data'}

        # Check performance degradation
        recent_perf = self.performance_history[-3:] if len(self.performance_history) >= 3 else []
        if recent_perf and all(p['accuracy_percentage'] < 75 for p in recent_perf):
            return {'retrain_needed': True, 'reason': 'poor_recent_performance'}

        # Check if enough new data available
        if len(self.feedback_data) >= 20:
            return {'retrain_needed': True, 'reason': 'sufficient_new_data'}

        # Check time since last retraining
        if self.model_versions:
            last_training = datetime.fromisoformat(self.model_versions[-1]['training_date'])
            days_since_training = (datetime.now() - last_training).days
            if days_since_training > 30:
                return {'retrain_needed': True, 'reason': 'time_based_retraining'}

        return {'retrain_needed': False, 'reason': 'no_retraining_needed'}

    def get_learning_insights(self):
        """Get comprehensive learning insights"""
        insights = {
            'performance_summary': self.analyze_performance_trends(),
            'model_versions': self.model_versions[-5:],  # Last 5 versions
            'weaknesses': self.identify_model_weaknesses(),
            'recommendations': self.generate_improvement_recommendations(),
            'retraining_status': self.schedule_retraining(),
            'feedback_stats': {
                'total_feedback_entries': len(self.feedback_data),
                'date_range': f"{self.feedback_data[0]['timestamp'] if self.feedback_data else 'N/A'} to {self.feedback_data[-1]['timestamp'] if self.feedback_data else 'N/A'}"
            }
        }

        return insights

    def update_performance_history(self, evaluation):
        """Update performance history with new evaluation"""
        self.performance_history.append(evaluation)

        # Keep only last 50 evaluations
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]

        self.save_performance_history()

    def adaptive_learning_trigger(self, current_accuracy):
        """Trigger adaptive learning based on current performance"""
        if current_accuracy < 70:
            # Immediate retraining needed
            return {'action': 'immediate_retraining', 'priority': 'high'}
        elif current_accuracy < 80:
            # Schedule retraining
            return {'action': 'schedule_retraining', 'priority': 'medium'}
        else:
            # Continue monitoring
            return {'action': 'monitor_only', 'priority': 'low'}
