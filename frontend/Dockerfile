# Etapa 1: construir el frontend con Node.js
FROM node:22-alpine AS build

WORKDIR /app

# Instalar las dependencias del frontend
COPY package*.json ./
RUN npm ci

# Copiar el código fuente
COPY . .

# La API será accesible mediante el proxy inverso
ENV VITE_API_URL=""

# Generar la versión de producción de React
RUN npm run build


# Etapa 2: servir el frontend compilado
FROM nginx:stable-alpine

# Copiar el resultado de la compilación
COPY --from=build /app/dist /usr/share/nginx/html

# Configuración para aplicaciones React
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]