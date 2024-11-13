## Provisioner image ##

# build
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/


# installing necssary dependencies #
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the app #
COPY . /app


# Port where will run flask app #
EXPOSE 5000


# Variable to production environment #
ENV FLASK_ENV=production


# Defining default command to run the app #
CMD ["python", "app.py"]