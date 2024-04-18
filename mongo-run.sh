docker pull mongodb/mongodb-community-server:latest
docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest
docker cp dump mongodb:/dump
docker container exec -it mongodb mongorestore dump/