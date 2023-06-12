FROM golang:alpine

ADD entrypoint.sh /bin/entrypoint
RUN go install github.com/NYTimes/openapi2proto/cmd/openapi2proto@latest && \
    chmod +x /bin/entrypoint


ENTRYPOINT [ "entrypoint" ]
