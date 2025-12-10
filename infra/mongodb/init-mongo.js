// MongoDB initialization script
db = db.getSiblingDB('ecommerce_logs');

// Create collections
db.createCollection('log_files');
db.createCollection('fraud_detections');
db.createCollection('alert_history');
db.createCollection('user_sessions');

// Create indexes
db.log_files.createIndex({ "uploaded_at": -1 });
db.log_files.createIndex({ "filename": 1 });

db.fraud_detections.createIndex({ "detected_at": -1 });
db.fraud_detections.createIndex({ "user_id": 1 });
db.fraud_detections.createIndex({ "fraud_score": -1 });

db.alert_history.createIndex({ "created_at": -1 });
db.alert_history.createIndex({ "alert_type": 1 });

db.user_sessions.createIndex({ "user_id": 1 });
db.user_sessions.createIndex({ "created_at": -1 });

print('MongoDB initialization completed');
