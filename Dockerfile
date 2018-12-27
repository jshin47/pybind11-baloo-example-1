# Get the base Ubuntu image from Docker Hub
FROM ubuntu:latest

# Update apps on the base image
RUN apt-get -y update && apt-get install -y

# Install the Clang compiler
RUN apt-get -y install clang cmake aptitude 
RUN apt-get -y install python3.6 python3-pip python3-setuptools

COPY . /usr/src/baloo
WORKDIR /usr/src/baloo

RUN pip3 install setuptools

RUN python3 setup.py install

CMD ["python3", "/usr/src/baloo/test/smoketest/baloo.smoketest.py"]