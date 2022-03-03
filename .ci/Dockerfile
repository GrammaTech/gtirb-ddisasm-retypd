FROM ubuntu:20.04 as souffle
RUN export DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN apt-get -y update && apt-get -y install bison build-essential cmake \
    doxygen flex git libffi-dev libtool lsb-release make mcpp pkg-config \
    zlib1g-dev

# souffle
RUN git clone -b 2.1 https://github.com/souffle-lang/souffle && \
    cd souffle && \
    cmake . -Bbuild -DCMAKE_BUILD_TYPE=Release -DSOUFFLE_USE_CURSES=0 -DSOUFFLE_USE_SQLITE=0 -DSOUFFLE_DOMAIN_64BIT=1 && \
    cd build && \
    make install -j4

FROM docker.grammatech.com/rewriting/ddisasm/ubuntu20 AS ubuntu20

COPY --from=souffle /usr/local/bin/souffle-compile /usr/bin/souffle-compile
COPY --from=souffle /usr/local/bin/souffle /usr/bin/souffle
COPY --from=souffle /usr/local/bin/souffleprof /usr/bin/souffleprof
COPY --from=souffle /usr/local/include/souffle/ /usr/include/souffle

RUN apt update
RUN apt install -y gcc python3 python3-pip
