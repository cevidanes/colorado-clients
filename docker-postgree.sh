#!/bin/bash

# Define your database name, user, password, and volume name
DB_NAME=colorado_clients
DB_USER=colorado
DB_PASSWORD=colorado123
VOLUME_NAME=postgres_data_boletos

# Check if the Docker volume exists, if not, create it
if [ $(docker volume ls -q -f name=$VOLUME_NAME | wc -l) -eq 0 ]; then
  echo "Creating Docker volume named $VOLUME_NAME for PostgreSQL data..."
  docker volume create $VOLUME_NAME
fi

# Pull the latest PostgreSQL image
docker pull postgres:latest

# Run the PostgreSQL container with the volume attached
docker run --name postgres-boletos \
  -e POSTGRES_DB=$DB_NAME \
  -e POSTGRES_USER=$DB_USER \
  -e POSTGRES_PASSWORD=$DB_PASSWORD \
  -p 5432:5432 \
  -v $VOLUME_NAME:/var/lib/postgresql/data \
  -d postgres

echo "PostgreSQL container is up and running on port 5432"
echo "Database: $DB_NAME, User: $DB_USER"
echo "Data volume: $VOLUME_NAME is attached for data persistence"
