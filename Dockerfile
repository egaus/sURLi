FROM ubuntu:latest
MAINTAINER "Evan Gaustad"

# Update repos and get Python3
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev wget p7zip-full software-properties-common curl xvfb unzip \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Adding sURLi library
RUN mkdir /surli
ADD setup.py /surli/setup.py
ADD sURLi /surli/sURLi
RUN pip3 install /surli && cd /surli

# Non-root user
# RUN groupadd -g 999 surli && \
#    useradd -r -u 999 -g surli surli
# RUN chown surli:surli /surli

ADD surli_cli.py /surli
WORKDIR /surli

RUN Xvfb :0 &
#USER surli
ENV DISPLAY=:0.0

# ENTRYPOINT ["/bin/sh"]
ENTRYPOINT ["python3", "/surli/surli_cli.py"]
