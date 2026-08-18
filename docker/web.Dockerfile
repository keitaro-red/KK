FROM node:24-alpine
WORKDIR /app

COPY web/package.json ./
RUN npm config set registry https://registry.npmmirror.com && npm install

COPY web/index.html web/vite.config.js ./
COPY web/public ./public
COPY web/src ./src

EXPOSE 5173

CMD ["npx","vite","--host"]