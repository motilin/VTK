# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and debugging tools
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libgl1-mesa-glx \
    libxt6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-dri \
    libglu1-mesa \
    libxrandr2 \
    libxcursor1 \
    libxinerama1 \
    libxi6 \
    gdb \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME=World
ENV PYTHONPATH=/app

# Run cylinder_example.py when the container launches
CMD ["python", "applications/cylinder_example.py"]