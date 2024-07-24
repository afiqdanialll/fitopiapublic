# The first stage
# Build React static files
FROM node:current-alpine3.19 as build

WORKDIR /app/frontend
COPY ./frontend/ ./
RUN npm ci && npm run build

# The second stage
# Copy React static files and start nginx
FROM nginx:stable-alpine3.19
COPY --from=build /app/frontend/build /usr/share/nginx/html
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
