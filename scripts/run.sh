#!/bin/bash
# TODO make user specific xhost rule
xhost +local:root
docker-compose up -d dev
docker exec -it $(docker ps -qf "name=rb-dev") bash
