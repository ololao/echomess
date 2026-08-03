FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY frontend/index.html frontend/style.css frontend/app.js /usr/share/nginx/html/

CMD ["nginx", "-g", "daemon off;"]
