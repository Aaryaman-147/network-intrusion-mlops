#!/bin/bash
# Start the API in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the Dashboard in the foreground
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0