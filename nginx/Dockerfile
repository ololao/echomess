FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY frontend /usr/share/nginx/html/

CMD ["nginx", "-g", "daemon off;"]
