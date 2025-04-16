## OPENAI
You first need to create an account on openAI and get your openAI key

## How to Use (Docker)

```sh
cd DrugPredictor
docker build -t predictor-docker-d:latest .
#if you want to make sure Docker is build fresh new no cache
docker build --no-cache  -t predictor-docker-d:latest .
docker run -it -p 9999:9999 predictor-docker-d
##this should start the web app



## Deploying on Heroku
 docker buildx build --provenance=false --platform linux/amd64 -t predictor-docker-linux:latest .
 docker tag predictor-docker-linux registry.heroku.com/drug-predictor1/web
 docker push registry.heroku.com/drug-predictor1/web 
 heroku container:release web -a drug-predictor1


 #to delete all docker containers and clear cache
 docker system prune --all
 