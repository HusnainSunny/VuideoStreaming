# Use an official lightweight Python image.
FROM python:3.10-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt .

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container.
COPY . .

# Expose the port your app will run on (informational).
EXPOSE 8765

# Run your application.
CMD ["python", "signaling_server.py"]
