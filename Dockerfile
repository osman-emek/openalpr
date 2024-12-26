from ubuntu:18.04

run apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    libcurl3-dev \
    libleptonica-dev \
    liblog4cplus-dev \
    libopencv-dev \
    libtesseract-dev \
    wget \
    software-properties-common

copy . /srv/openalpr

run mkdir /srv/openalpr/src/build
workdir /srv/openalpr/src/build

run cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc .. && \
    make -j2 && \
    make install

#///////

run add-apt-repository -y ppa:deadsnakes/ppa

run apt-get update && apt-get install -y python3.8
run apt-get install -y python3-pip

run python3.8 -m pip --no-cache-dir install pip

run apt-get install -y python3-distutils
run apt-get install -y python3-setuptools
run apt-get install -y python3.8-venv

run python3.8 -m venv /venv

env PATH="/venv/bin:$PATH"

run python3.8 -m pip install --no-cache-dir pip --upgrade pip

run mkdir /opt/app
workdir /opt/app
copy ./code/main.py /opt/app/main.py
copy ./code/requirements.txt /opt/app/requirements.txt

run pip3 install --no-cache-dir fastapi
run pip3 install --no-cache-dir fastapi-cli

expose 8181

cmd ["fastapi", "run", "/opt/app/main.py","--port","8181","--workers","4","--host","0.0.0.0"]