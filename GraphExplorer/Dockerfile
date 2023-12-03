FROM node:latest

WORKDIR /code

COPY ./.env /code/.env 
COPY ./package.json /code/package.json
COPY ./package-lock.json /code/package-lock.json

RUN npm install

COPY ./src /code/src
COPY ./public /code/public
COPY ./tsconfig.json /code/tsconfig.json

CMD ["npm", "start"]