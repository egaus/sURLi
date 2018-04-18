FROM ubuntu:latest
MAINTAINER "Evan Gaustad"

# Update repos and get Python3
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev wget p7zip-full software-properties-common curl xvfb \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-add-repository ppa:mozillateam/firefox-next \
  &&  apt-get install -y firefox

# Dev packages for phantomjs and 7zip
#RUN apt-get install build-essential chrpath libssl-dev libxft-dev libfreetype6-dev libfreetype6 libfontconfig1-dev libfontconfig1  -y
#RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 \
#  && tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/ \
#  && ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/

RUN export BASE_URL=https://github.com/mozilla/geckodriver/releases/download \
  && export VERSION=$(curl -sL \
    https://api.github.com/repos/mozilla/geckodriver/releases/latest | \
    grep tag_name | cut -d '"' -f 4) \
  && curl -sL \
  $BASE_URL/$VERSION/geckodriver-$VERSION-linux64.tar.gz | tar -xz \
  && mv geckodriver /usr/local/bin/geckodriver

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

# RUN Xvfb :0 &
# USER surli
# ENV DISPLAY=:0.0

#ENTRYPOINT ["/bin/sh"]
ENTRYPOINT ["python3", "/surli/surli_cli.py"]
