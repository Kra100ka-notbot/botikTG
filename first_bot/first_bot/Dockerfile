# Указываем версию python
FROM python:3.13 
# Устанавливаем часовой пояс
ENV TZ="Europe/Moscow"
RUN apt update -y
RUN apt install -y tzdata
# Рабочая директория внутри контейнера
WORKDIR /usr/src/app
RUN cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime
# Копируем зависимоти
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 
# Выделяем папку под логи
RUN mkdir -p /usr/src/app/log

# Копируем директорию основного кода
COPY ./src/* .
# Копируем токен бота указаный в файле
COPY ./*.bot_token .
# Указываем команду запуска
CMD ["python", "./main.py"]