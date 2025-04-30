FROM python:3.9-slim

# Create working directory
WORKDIR /app

# Install dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create and switch to non-root user
RUN useradd -m myuser && \
    chown -R myuser:myuser /app
USER myuser

# Run the application
CMD ["python", "bot.py"]
