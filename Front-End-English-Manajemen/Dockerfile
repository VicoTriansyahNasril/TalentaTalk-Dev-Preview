# ---- TAHAP 1: BUILD APLIKASI REACT ----
FROM node:18-alpine AS builder

# Install dependencies yang mungkin diperlukan
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clear npm cache dan registry cache, set strict SSL false untuk debug
RUN npm cache clean --force
RUN npm config set registry https://registry.npmjs.org/
RUN npm config set strict-ssl false

# Install dependencies dengan retry mechanism dan fallback options
RUN npm install --no-audit --no-fund --verbose --fetch-retries 5 --fetch-retry-mintimeout 20000 --fetch-retry-maxtimeout 120000 || \
    (npm cache clean --force && npm install --no-audit --no-fund --legacy-peer-deps) || \
    (rm -rf node_modules package-lock.json && npm install --no-audit --no-fund)

# Copy source code
COPY . .

# Set build argument dan environment
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build aplikasi
RUN npm run build

# ---- TAHAP 2: SERVE HASIL BUILD DENGAN NGINX ----
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]