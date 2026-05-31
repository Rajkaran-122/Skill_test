FROM node:22-alpine AS base
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .

FROM base AS development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

FROM base AS production
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
