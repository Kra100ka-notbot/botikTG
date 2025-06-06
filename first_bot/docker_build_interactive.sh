echo "Starting container interactively..."

# Читаем имя образа из файла
IMAGE_NAME=$(cat image_name.txt)

# Убедимся, что директория для логов существует
mkdir -p ./log

# Запускаем контейнер
docker run -it --rm \
    -v "$(pwd)/log:/usr/log/app/log" \
    "$IMAGE_NAME"
