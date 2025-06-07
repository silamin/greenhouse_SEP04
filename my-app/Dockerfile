FROM node:18-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

# Install a static server to serve the build
RUN npm install -g serve

COPY . ./
RUN npm run build

EXPOSE 3000
CMD ["serve", "-s", "dist"]
