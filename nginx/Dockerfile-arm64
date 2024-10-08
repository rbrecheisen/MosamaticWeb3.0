FROM alpine:3.14

ENV NGINX_VERSION 1.25.2

COPY install.sh /usr/src/
COPY nginx.key /usr/src/

RUN apk add dos2unix && dos2unix /usr/src/install.sh && sh -x /usr/src/install.sh

COPY nginx.conf /etc/nginx/nginx.conf
RUN dos2unix /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
