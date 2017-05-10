FROM python:3.5

# We want proper container logging
ENV PYTHONUNBUFFERED 1

# Upgrade ubuntu
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y pkg-config
RUN apt-get install -y software-properties-common python-software-properties
RUN apt-get install -y apt-utils

# Upgrade pip
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip

# Install requirements
ADD requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Set working directory to project
WORKDIR /github_issues_report
ADD . /github_issues_report
