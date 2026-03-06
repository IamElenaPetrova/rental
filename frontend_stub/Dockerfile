FROM alpine:3.19

WORKDIR /app

COPY index.html build/

CMD ["sh", "-c", "cp -r /app/build/. /static/"]
