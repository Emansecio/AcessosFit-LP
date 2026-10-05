FROM nginx:stable-alpine@sha256:ef8676b33d681f272ba429b27658bdd7e640963279714c96bddf1dc76307f7b6
RUN apk add --no-cache logrotate \
    && mkdir -p /var/log/nginx/private \
    && chown nginx:nginx /var/log/nginx/private \
    && chmod 700 /var/log/nginx/private
COPY nginx-main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-logrotate.conf /etc/logrotate.d/nginx-private
COPY --chmod=755 nginx-start.sh /usr/local/bin/nginx-start
COPY site/ /usr/share/nginx/html/
USER 101:101
ENTRYPOINT ["/usr/local/bin/nginx-start"]
EXPOSE 80
