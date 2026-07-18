import random
from datetime import datetime, timedelta
from database import SessionLocal
import models
from machine_learning.preprocessing import preprocess_telemetry
from machine_learning.feature_engineering import generate_features
from machine_learning.train_models import PasteurizationModelTrainer

def run_training_pipeline():
    db = SessionLocal()
    
    # 1. Database Check & Synthetic Data Injection
    record_count = db.query(models.SensorData).count()
    if record_count < 100:
        print(f"\n[Warning] Only {record_count} rows found. Injecting 500 simulated historical records...")
        base_time = datetime.utcnow() - timedelta(days=7)
        for i in range(500):
            # Simulating a realistic thermal heating curve
            temp = 25.0 + (i % 100) * 0.5 
            new_record = models.SensorData(
                machine_id="MP001",
                timestamp=base_time + timedelta(minutes=i),
                mode="AUTO",
                process="HEATING" if temp < 72 else "HOLDING",
                temperature=temp + random.uniform(-1.0, 1.0), # Add thermal noise
                target_temperature=75.0,
                voltage=230.0 + random.uniform(-5.0, 5.0),
                power=2.5 + random.uniform(-0.2, 0.2),
                heater_status=True if temp < 75 else False,
                wifi_connected=True
            )
            db.add(new_record)
        db.commit()
        print("[Success] Simulated historical data injected into PostgreSQL.")

    # 2. Extract Data for ML
    print("\n[Extraction] Extracting historical SensorData from PostgreSQL...")
    records = db.query(models.SensorData).all()
    
    # Convert SQLAlchemy ORM objects to a list of standard dictionaries
    raw_data = []
    for r in records:
        row_dict = {column.name: getattr(r, column.name) for column in r.__table__.columns}
        raw_data.append(row_dict)
        
    db.close()

    # 3. Run the Preprocessing & Engineering Pipeline
    print("\n[Pipeline] Pushing data through ML Pipeline...")
    df_clean = preprocess_telemetry(raw_data)
    df_features = generate_features(df_clean)

    # 4. Train the Models
    print("\n[Training] Initializing Random Forest & Isolation Forest Training...")
    trainer = PasteurizationModelTrainer(df_features)
    
    # We will train a Regressor to predict Power Consumption (Energy Optimization)
    if 'power' in df_features.columns:
        trainer.train_numerical('power', 'energy_model.pkl')
        
    # We will train a Classifier to predict Heater Status (Control Systems)
    # Using 'heater_status' which was converted to 1/0 during preprocessing
    if 'heater_status' in df_features.columns:
        trainer.train_categorical('heater_status', 'heating_model.pkl')
        
    # We will train an Isolation Forest to detect sensor anomalies (Fault Detection)
    trainer.train_anomaly_detection('fault_model.pkl')
    
    print("\n[Complete] Pipeline Execution Complete!")

if __name__ == "__main__":
    run_training_pipeline()
