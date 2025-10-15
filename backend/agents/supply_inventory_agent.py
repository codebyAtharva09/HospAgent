import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

class SupplyInventoryAgent:
    def __init__(self):
        self.inventory_data = self._load_inventory_data()
        self.consumption_history = self._load_consumption_history()
        self.consumption_model = self._train_consumption_model()

    def _load_inventory_data(self):
        """Load current inventory levels."""
        # Mock inventory data - in real implementation, this would come from inventory DB
        return {
            'oxygen_masks': {'current_stock': 500, 'min_threshold': 100, 'max_capacity': 1000},
            'ventilator_filters': {'current_stock': 50, 'min_threshold': 10, 'max_capacity': 100},
            'gloves': {'current_stock': 2000, 'min_threshold': 200, 'max_capacity': 5000},
            'syringes': {'current_stock': 1000, 'min_threshold': 100, 'max_capacity': 2000},
            'antibiotics': {'current_stock': 300, 'min_threshold': 50, 'max_capacity': 500},
            'painkillers': {'current_stock': 400, 'min_threshold': 40, 'max_capacity': 600},
            'bandages': {'current_stock': 800, 'min_threshold': 80, 'max_capacity': 1500}
        }

    def _load_consumption_history(self):
        """Load historical consumption data."""
        # Mock consumption data for the last 30 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        data = []
        for date in dates:
            data.append({
                'date': date,
                'oxygen_masks': np.random.randint(20, 50),
                'ventilator_filters': np.random.randint(2, 8),
                'gloves': np.random.randint(100, 300),
                'syringes': np.random.randint(50, 150),
                'antibiotics': np.random.randint(10, 30),
                'painkillers': np.random.randint(15, 40),
                'bandages': np.random.randint(40, 100),
                'patient_count': np.random.randint(150, 300)
            })
        return pd.DataFrame(data)

    def _train_consumption_model(self):
        """Train model to predict consumption based on patient count."""
        models = {}
        for supply in ['oxygen_masks', 'ventilator_filters', 'gloves', 'syringes', 'antibiotics', 'painkillers', 'bandages']:
            X = self.consumption_history[['patient_count']]
            y = self.consumption_history[supply]
            model = LinearRegression()
            model.fit(X, y)
            models[supply] = model
        return models

    def predict_consumption(self, predicted_patients, days_ahead=7):
        """Predict supply consumption for the next few days."""
        predictions = {}
        for supply, model in self.consumption_model.items():
            predicted_usage = model.predict([[predicted_patients]])[0]
            daily_usage = max(1, int(predicted_usage))
            predictions[supply] = {
                'daily_usage': daily_usage,
                'weekly_usage': daily_usage * days_ahead,
                'current_stock': self.inventory_data[supply]['current_stock'],
                'days_until_depletion': int(self.inventory_data[supply]['current_stock'] / daily_usage),
                'reorder_needed': self.inventory_data[supply]['current_stock'] < self.inventory_data[supply]['min_threshold'] * 2
            }
        return predictions

    def generate_reorder_alerts(self, predictions):
        """Generate alerts for supplies that need reordering."""
        alerts = []
        for supply, data in predictions.items():
            if data['reorder_needed'] or data['days_until_depletion'] < 7:
                alerts.append({
                    'supply': supply,
                    'current_stock': data['current_stock'],
                    'predicted_daily_usage': data['daily_usage'],
                    'days_until_depletion': data['days_until_depletion'],
                    'recommended_order': max(100, data['weekly_usage'] * 2),  # Order for 2 weeks
                    'urgency': 'critical' if data['days_until_depletion'] < 3 else 'high' if data['days_until_depletion'] < 7 else 'medium',
                    'reason': f"Predicted surge will deplete {supply} in {data['days_until_depletion']} days"
                })
        return alerts

    def update_inventory(self, supply, quantity_change):
        """Update inventory levels after consumption or restocking."""
        if supply in self.inventory_data:
            self.inventory_data[supply]['current_stock'] += quantity_change
            self.inventory_data[supply]['current_stock'] = max(0, min(
                self.inventory_data[supply]['current_stock'],
                self.inventory_data[supply]['max_capacity']
            ))
            return True
        return False

    def get_inventory_status(self):
        """Get current inventory status for all supplies."""
        status = {}
        for supply, data in self.inventory_data.items():
            status[supply] = {
                'current_stock': data['current_stock'],
                'min_threshold': data['min_threshold'],
                'max_capacity': data['max_capacity'],
                'stock_level': 'low' if data['current_stock'] < data['min_threshold'] else 'normal',
                'utilization_percent': (data['current_stock'] / data['max_capacity']) * 100
            }
        return status

    def optimize_inventory_levels(self, predictions):
        """Optimize inventory levels based on predictions and historical data."""
        optimizations = []
        for supply, pred_data in predictions.items():
            current = self.inventory_data[supply]['current_stock']
            min_thresh = self.inventory_data[supply]['min_threshold']
            max_cap = self.inventory_data[supply]['max_capacity']

            # Calculate optimal stock level (2 weeks buffer)
            optimal_stock = pred_data['weekly_usage'] * 2

            if optimal_stock > current:
                optimizations.append({
                    'supply': supply,
                    'action': 'increase',
                    'current_stock': current,
                    'recommended_stock': min(max_cap, optimal_stock),
                    'quantity_to_add': min(max_cap - current, optimal_stock - current),
                    'reason': f"Predicted usage requires {optimal_stock} units for safety buffer"
                })
            elif current > max_cap * 0.8 and pred_data['days_until_depletion'] > 14:
                optimizations.append({
                    'supply': supply,
                    'action': 'reduce',
                    'current_stock': current,
                    'recommended_stock': optimal_stock,
                    'quantity_to_remove': current - optimal_stock,
                    'reason': f"Overstock detected, can reduce to {optimal_stock} units"
                })

        return optimizations
