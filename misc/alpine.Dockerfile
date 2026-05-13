FROM alpine:latest

RUN apk add --no-cache \
    gcc make autoconf automake libtool pkgconf musl-dev bash git \
    gmp-dev pcre2-dev gettext-dev \
    python3
