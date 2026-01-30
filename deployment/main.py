import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="CyberGuard AI - Cloud API")

# --- Global State ---
model = None

# --- Load Model on Startup ---
try:
    print("Loading model from file...")
    # We expect model.pkl to be in the same folder
    model = joblib.load("model.pkl")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    model = None

@app.get("/")
def home():
    return {"status": "Online", "model_loaded": model is not None}

@app.post("/predict")
async def predict(request: Request):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # 1. Parse Raw JSON
        body = await request.json()
        features_dict = body.get("features", {})
        
        if not features_dict:
             raise ValueError("No feature data found in request")

        # 2. Convert to DataFrame
        df_input = pd.DataFrame([features_dict])
        
        # 3. Numeric Conversion
        df_input = df_input.apply(pd.to_numeric, errors='coerce').fillna(0)

        # 4. Feature Alignment
        if hasattr(model, "feature_names_in_"):
            required_features = model.feature_names_in_
            df_input = df_input.reindex(columns=required_features, fill_value=0)
        
        # 5. Predict
        prediction = model.predict(df_input)[0]
        # Map 0 -> BENIGN, 1 -> DDoS (Adjust if your model uses different mapping)
        label = "DDoS" if prediction == 1 else "BENIGN"
        
        return {"prediction": label, "status": label, "confidence": "High"}

    except Exception as e:
        print(f"🔥 Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))