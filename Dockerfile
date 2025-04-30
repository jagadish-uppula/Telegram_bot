FROM python:3.9-slim

WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create and switch to Choreo-compliant user (UID between 10000-20000)
RUN useradd -u 10014 -m choreouser && \
    chown -R choreouser:choreouser /app
USER 10014  # Explicitly set the UID

# Run the application
CMD ["python", "bot.py"]
