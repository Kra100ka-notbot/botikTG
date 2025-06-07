echo "Starting container interactively..."

IMAGE_NAME=$(cat image_name.txt)

docker run \
    -v "$(pwd)/log:/usr/log/app/log" "$IMAGE_NAME"
