# Chattypaws backend — API + detector (same image; run API by default).
# For HA add-on we'll reuse this image with add-on metadata.
FROM python:3.12-slim

WORKDIR /app

# OpenCV headless may need libgl (uncomment if runtime fails).
# RUN apt-get update && apt-get install -y --no-install-recommends libgl1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run API. Override CMD to run detector: python -m detector
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
