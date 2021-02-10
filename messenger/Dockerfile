FROM node:latest

WORKDIR /usr/src/app/messenger

COPY ["package.json", "package-lock.json*", "./"]

RUN npm install --production

COPY . .

CMD [ "node", "messenger.js" ]