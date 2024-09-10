# Deploying HTTPS APP on DigitalOcean (Ubuntu 24.04) using Docker, Nginx, and Let's Encrypt
## Step 1: Update and Install Docker
- Update the package manager and upgrade the system:
```
sudo apt update
```
- Install Docker on the server:
```
sudo apt install -y docker.io
```
- Start the Docker service:
```
sudo systemctl start docker
```
- Enable Docker to start automatically on system reboot:
```
sudo systemctl enable docker
```
## Step 2: Install Docker Compose
- Download and install the latest version of Docker Compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '(?<="tag_name": ")[^"]*')/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
- Make the Docker Compose binary executable:
sudo chmod +x /usr/local/bin/docker-compose
## Step 3: Install Git
- Install Git to clone the repository:
```
sudo apt install -y git
```
## Step 4: Run the Application with Docker Compose
- Use Docker Compose to start your application in detached mode:
```
sudo docker-compose up -d
```
## Step 5: Set Up Firewall Rules
- Allow traffic on ports 80 (HTTP) and 443 (HTTPS):
```
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
Ensure OpenSSH is allowed for remote access:
sudo ufw allow OpenSSH
Enable the firewall:
sudo ufw enable
```
## Step 6: Install and Configure Nginx
- Install Nginx on the server:
```
sudo apt install nginx -y
```
- Allow full Nginx access through the firewall:
```
sudo ufw allow 'Nginx Full'
```
- Create a new Nginx configuration file under /etc/nginx/sites-available/ to proxy requests to the Docker container on port 5000:
```
sudo vim /etc/nginx/sites-available/yourapp
```
- Add the server block to listen on port 80 and proxy requests to localhost:$PORT.
```
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    location / {
        proxy_pass http://localhost:$PORT;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
## Step 7: Enable the New Nginx Configuration
- Link the new configuration file to /etc/nginx/sites-enabled/:
```
sudo ln -s /etc/nginx/sites-available/yourapp /etc/nginx/sites-enabled/
```
- Unlink the default Nginx site to disable it:
```
sudo unlink /etc/nginx/sites-enabled/default
```
- Test the Nginx configuration for any syntax errors:
```
sudo nginx -t
```
- Start the Nginx service:
```
sudo systemctl start nginx
```
- Reload Nginx to apply the changes:
```
sudo systemctl reload nginx
```
- Enable Nginx to start on system reboot:
```
sudo systemctl enable nginx
```
## Step 8: Install Certbot for Let's Encrypt SSL Certificates
- Install Certbot and the Certbot Nginx plugin:
```
sudo apt install certbot python3-certbot-nginx -y
```
- Use Certbot to obtain an SSL certificate for your domain:
```
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```
- Certbot will automatically update the Nginx configuration with the SSL certificate and reload Nginx.

## Step 9: Review the Certificate and Key Locations And HTTPS Redirect In Your Nginx Configuration
- The SSL certificate and key are saved at:
```
server {
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    if ($host = your-domain.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name your-domain.com;
    return 404; # managed by Certbot


}
```
Certbot will automatically renew the certificate before it expires and update the certificate files.

## Step 10: Test Certificate Renewal
- Run a dry-run test to ensure Certbot is correctly set up for automatic certificate renewal:
```
sudo certbot renew --dry-run
```
