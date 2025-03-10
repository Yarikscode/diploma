FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Копируем фронтенд файлы (HTML, CSS, JS)
COPY html/ .  

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
