from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import json

router = APIRouter(prefix="/analytics", tags=["Analytics"])

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mldataset", "data.csv")

@router.get("/correlation")
async def get_correlation_matrix():
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        # Drop non-numeric columns like 'date'
        numeric_df = df.select_dtypes(include=['number'])
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Convert to a format easy for the frontend to consume
        # We'll return labels and values
        labels = list(corr_matrix.columns)
        values = corr_matrix.values.tolist()
        
        # Also provide some "Insights" from the correlation
        strong_positive = []
        strong_negative = []
        
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                val = values[i][j]
                insight = {
                    "source": labels[i],
                    "target": labels[j],
                    "value": round(val, 2)
                }
                if val > 0.7:
                    strong_positive.append(insight)
                elif val < -0.7:
                    strong_negative.append(insight)
        
        return {
            "labels": labels,
            "values": values,
            "strong_positive": strong_positive,
            "strong_negative": strong_negative
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset")
async def get_raw_dataset():
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
