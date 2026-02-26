#!/bin/bash

# Image Generation Suite Launcher
echo "🎨 Starting Image Generation Suite..."
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the app
echo "🚀 Launching Streamlit app..."
streamlit run app.py
