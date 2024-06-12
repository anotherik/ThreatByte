# Use an official Python runtime as a parent image
FROM python:3.9-slim
# Set the working directory in the container
WORKDIR /app
# Copy the dependencies file to the working directory
COPY requirements.txt .
# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code to the working directory
COPY . .
# Expose the port number the Flask app runs on
EXPOSE 5000
# Define environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
# Run the Flask application
CMD ["flask", "run"]
