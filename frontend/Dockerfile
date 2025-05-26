FROM node:23-alpine AS builder

ARG NGINX_BACKEND_URL="http://arxivsearch:2137"
ARG NGINX_SERVER_NAME="localhost"
ARG FRONTEND_BACKEND_URL=""

ENV BACKEND_URL=${FRONTEND_BACKEND_URL} VITE_BACKEND_URL=${FRONTEND_BACKEND_URL} \
    NGINX_SERVER_NAME=${NGINX_SERVER_NAME} \
    NGINX_BACKEND_URL=${NGINX_BACKEND_URL}

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.28

WORKDIR /app
COPY --from=builder /app/build .
COPY nginx.conf /etc/nginx/templates/nginx.conf.template
