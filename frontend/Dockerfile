FROM node:20-alpine AS build

WORKDIR /app

ENV ELECTRON_SKIP_BINARY_DOWNLOAD=1

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build


FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
