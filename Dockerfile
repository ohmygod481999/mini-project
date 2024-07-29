FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# create client_file_folder if it doesnt exist
RUN mkdir -p /app/src/client_file_storage

ENV PYTHONPATH /app/src

EXPOSE 8765

# Set the command to run when the container starts
# CMD [ "python", "app.py" ]