# Dockerfile for Muni MCP MySQL Server
# This creates a containerized version of the MCP server

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies for MySQL client
RUN apk add --no-cache \
    mysql-client \
    curl \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S mcp && \
    adduser -S mcp -u 1001 -G mcp

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application files
COPY --chown=mcp:mcp . .

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R mcp:mcp logs

# Create health check script
RUN echo '#!/usr/bin/env node\n\
const mysql = require("mysql2/promise");\n\
require("dotenv").config();\n\
\n\
async function healthCheck() {\n\
  try {\n\
    // Check if server process is responsive\n\
    const response = await fetch("http://localhost:3333/health", {\n\
      timeout: 5000\n\
    }).catch(() => null);\n\
    \n\
    if (response && response.ok) {\n\
      process.exit(0);\n\
    }\n\
    \n\
    // Fallback: test database connection\n\
    const config = {\n\
      host: process.env.MYSQL_DEV_HOST || "bdb-dev",\n\
      port: parseInt(process.env.MYSQL_DEV_PORT) || 3307,\n\
      user: process.env.MYSQL_DEV_USER,\n\
      password: process.env.MYSQL_DEV_PASSWORD,\n\
      connectTimeout: 5000\n\
    };\n\
    \n\
    if (!config.user || !config.password) {\n\
      console.error("Health check failed: Missing credentials");\n\
      process.exit(1);\n\
    }\n\
    \n\
    const connection = await mysql.createConnection(config);\n\
    await connection.execute("SELECT 1");\n\
    await connection.end();\n\
    \n\
    console.log("Health check passed");\n\
    process.exit(0);\n\
  } catch (error) {\n\
    console.error("Health check failed:", error.message);\n\
    process.exit(1);\n\
  }\n\
}\n\
\n\
healthCheck();\n' > health-check.js && \
    chmod +x health-check.js && \
    chown mcp:mcp health-check.js

# Switch to non-root user
USER mcp

# Set environment variables
ENV NODE_ENV=production
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=3333

# Expose MCP server port
EXPOSE 3333

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node health-check.js

# Start the MCP server
CMD ["node", "server.js", "--dev"]

# Build-time metadata
LABEL maintainer="Muni Development Team"
LABEL description="MCP MySQL server for AI database access"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/your-org/muni"
LABEL org.opencontainers.image.title="Muni MCP MySQL Server"
LABEL org.opencontainers.image.description="Read-only MySQL database access via Model Context Protocol"