from ubuntu:18.04

# Install prerequisites
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
    software-properties-common \
    python3 \
    python3-pip

# Copy all data
copy . /srv/openalpr

# Setup the build directory
run mkdir /srv/openalpr/src/build
workdir /srv/openalpr/src/build

# Setup the compile environment
run cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc .. && \
    make -j2 && \
    make install

run mkdir /opt/app
workdir /opt/app
copy ./code/main.py /opt/app/main.py
#run python -m venv /venv
#env PATH="/venv/bin:$PATH"
run pip3 install --upgrade pip
run pip3 install openalpr
run pip3 install tornado
run pip3 install numpy

expose 7878

cmd ["python3", "/opt/app/main.py"]

#entrypoint ["alpr"]
