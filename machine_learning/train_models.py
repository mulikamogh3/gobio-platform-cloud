import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
import numpy as np

class PasteurizationModelTrainer:
    def __init__(self, data: pd.DataFrame, model_dir="machine_learning/models/"):
        df = data.copy()
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
            
        # Convert all columns to numeric, coercing strings/errors to NaN, then fill with 0
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        self.data = df
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)

    def split_data(self, target_col):
        X = self.data.drop(columns=[target_col])
        y = self.data[target_col]
        # 80/20 Split as requested
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_numerical(self, target_col, model_name):
        print(f"\nTraining Regressor for: {target_col}")
        X_train, X_test, y_train, y_test = self.split_data(target_col)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        
        # Evaluation
        print(f"MAE: {mean_absolute_error(y_test, predictions):.4f}")
        print(f"RMSE: {np.sqrt(mean_squared_error(y_test, predictions)):.4f}")
        print(f"R2 Score: {r2_score(y_test, predictions):.4f}")
        
        self.save_model(model, model_name)

    def train_categorical(self, target_col, model_name):
        print(f"\nTraining Classifier for: {target_col}")
        X_train, X_test, y_train, y_test = self.split_data(target_col)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        
        # Evaluation
        print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
        print("Classification Report:\n", classification_report(y_test, predictions))
        
        self.save_model(model, model_name)

    def train_anomaly_detection(self, model_name="fault_model.pkl"):
        print(f"\nTraining Isolation Forest for Anomaly Detection")
        # Isolation forest doesn't need a target column
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(self.data)
        
        print("Isolation Forest trained successfully on full dataset.")
        self.save_model(model, model_name)

    def save_model(self, model, filename):
        filepath = os.path.join(self.model_dir, filename)
        joblib.dump(model, filepath)
        print(f"[Success] Model saved to {filepath}")

# --- Example Usage (We will trigger this later from the API) ---
# if __name__ == "__main__":
#     trainer = PasteurizationModelTrainer(df)
#     trainer.train_numerical('time_to_target', 'heating_model.pkl')
#     trainer.train_anomaly_detection('fault_model.pkl')
