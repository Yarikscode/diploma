FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY html/ .  # Копируем фронтенд файлы
COPY nginx.conf /etc/nginx/nginx.conf  # Подключаем конфиг
CMD ["nginx", "-g", "daemon off;"]