# Use Python 3.11 slim image (no Chrome needed for no-selenium version)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the no-selenium production script (faster, no timeout issues)
CMD ["python", "run_production_powerbi_no_selenium.py"]
