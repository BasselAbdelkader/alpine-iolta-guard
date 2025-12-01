FROM nginx:alpine

# Copy all frontend files to nginx html directory
COPY frontend/ /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Nginx runs automatically from base image
