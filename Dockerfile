# Get the base Ubuntu image from Docker Hub
FROM ubuntu:latest

# Update apps on the base image
RUN apt-get -y update && apt-get install -y

# Install the Clang compiler
RUN apt-get -y install clang cmake aptitude 
RUN apt-get -y install python3.6 python3-pip python3-setuptools
RUN apt-get -y install curl libcurl4-openssl-dev

COPY . /usr/src/baloo
WORKDIR /usr/src/baloo

RUN pip3 install setuptools pytest

RUN python3 setup.py install

CMD ["pytest", "/usr/src/baloo/test/pytest/OrderBookSnapshot.py"]