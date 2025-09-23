# 1. Use an official lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependencies file first to leverage Docker cache
COPY ./requirements.txt .

# 4. Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your application code into the container
COPY ./app ./app
COPY ./main.py .

# 6. Expose the port App Runner will listen on
EXPOSE 8080

# 7. Command to run the application using uvicorn
#    --host 0.0.0.0 is CRITICAL for App Runner to access the app inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]