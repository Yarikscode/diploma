FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY html/ /usr/share/nginx/html/

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
