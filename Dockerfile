FROM python:3.9-slim-bullseye
LABEL authors="olive"

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container at /app
COPY ./src ./src
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 3000

# Run app.py when the container launches
CMD ["python", "src/app.py"]