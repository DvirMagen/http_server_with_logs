# Use the python 3.9 image as the Base Image
FROM python:3.9

# install packages
RUN pip install flask

# Create a new app directory for application files
RUN mkdir /app

# Copy the main.py from the host machine to image filesystem
COPY ./main.py /app

# set the directory for executing future commands
WORKDIR /app

# expose application port to docker
EXPOSE 9285

# run the main class
CMD python3 main.py

