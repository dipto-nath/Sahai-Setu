# Frontend Dockerfile for SIH26093
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Build application
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]
