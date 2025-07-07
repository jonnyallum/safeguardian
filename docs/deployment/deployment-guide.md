# SafeGuardian Deployment Guide

## Overview

SafeGuardian is a comprehensive multi-platform child protection system designed to monitor social media interactions and detect potential grooming attempts in real-time. This deployment guide provides step-by-step instructions for setting up SafeGuardian in production environments.

## System Requirements

### Hardware Requirements

**Minimum Requirements:**
- CPU: 4 cores, 2.4 GHz
- RAM: 8 GB
- Storage: 100 GB SSD
- Network: 100 Mbps bandwidth

**Recommended Requirements:**
- CPU: 8 cores, 3.0 GHz
- RAM: 16 GB
- Storage: 500 GB SSD
- Network: 1 Gbps bandwidth

**Production Requirements:**
- CPU: 16 cores, 3.2 GHz
- RAM: 32 GB
- Storage: 1 TB SSD (with backup)
- Network: 10 Gbps bandwidth
- Load balancer support
- Database clustering capability

### Software Requirements

- **Operating System:** Ubuntu 22.04 LTS or later
- **Python:** 3.11 or later
- **Node.js:** 20.x or later
- **Database:** PostgreSQL 15+ or MySQL 8.0+
- **Redis:** 7.0+ (for caching and session management)
- **Nginx:** 1.20+ (reverse proxy and load balancing)
- **SSL Certificate:** Valid SSL certificate for HTTPS

## Pre-Deployment Checklist

### Security Preparation

1. **Generate Encryption Keys**
   ```bash
   # Generate master encryption key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Generate JWT secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Database Security**
   - Create dedicated database user with minimal privileges
   - Enable SSL connections
   - Configure firewall rules
   - Set up database backups

3. **Network Security**
   - Configure firewall (UFW recommended)
   - Set up VPN access for administrators
   - Enable fail2ban for SSH protection
   - Configure SSL/TLS certificates

### Environment Configuration

1. **Create Environment Files**
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   
   # Frontend environment
   cp mobile/.env.example mobile/.env
   cp dashboard/.env.example dashboard/.env
   ```

2. **Configure Database Connection**
   ```env
   DATABASE_URL=postgresql://safeguardian_user:secure_password@localhost:5432/safeguardian_db
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Set Security Configuration**
   ```env
   SECRET_KEY=your_generated_secret_key
   JWT_SECRET=your_generated_jwt_secret
   ENCRYPTION_KEY=your_generated_encryption_key
   ```

## Deployment Steps

### Step 1: System Preparation

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y curl wget git build-essential
   ```

2. **Install Python and Node.js**
   ```bash
   # Install Python 3.11
   sudo apt install -y python3.11 python3.11-venv python3.11-dev
   
   # Install Node.js 20.x
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

3. **Install Database and Redis**
   ```bash
   # Install PostgreSQL
   sudo apt install -y postgresql postgresql-contrib
   
   # Install Redis
   sudo apt install -y redis-server
   
   # Install Nginx
   sudo apt install -y nginx
   ```

### Step 2: Database Setup

1. **Create Database and User**
   ```sql
   sudo -u postgres psql
   
   CREATE DATABASE safeguardian_db;
   CREATE USER safeguardian_user WITH ENCRYPTED PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE safeguardian_db TO safeguardian_user;
   ALTER USER safeguardian_user CREATEDB;
   \q
   ```

2. **Configure PostgreSQL**
   ```bash
   # Edit postgresql.conf
   sudo nano /etc/postgresql/15/main/postgresql.conf
   
   # Enable SSL and configure connections
   ssl = on
   listen_addresses = 'localhost'
   max_connections = 200
   ```

3. **Initialize Database Schema**
   ```bash
   cd /opt/safeguardian/backend
   python manage.py db init
   python manage.py db migrate
   python manage.py db upgrade
   ```

### Step 3: Backend Deployment

1. **Clone and Setup Backend**
   ```bash
   sudo mkdir -p /opt/safeguardian
   sudo chown $USER:$USER /opt/safeguardian
   cd /opt/safeguardian
   
   # Copy backend files
   cp -r /path/to/safeguardian/backend ./
   cd backend
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Backend Service**
   ```bash
   sudo nano /etc/systemd/system/safeguardian-backend.service
   ```
   
   ```ini
   [Unit]
   Description=SafeGuardian Backend API
   After=network.target postgresql.service redis.service
   
   [Service]
   Type=exec
   User=safeguardian
   Group=safeguardian
   WorkingDirectory=/opt/safeguardian/backend
   Environment=PATH=/opt/safeguardian/backend/venv/bin
   ExecStart=/opt/safeguardian/backend/venv/bin/python src/main.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Start Backend Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable safeguardian-backend
   sudo systemctl start safeguardian-backend
   sudo systemctl status safeguardian-backend
   ```

### Step 4: Frontend Deployment

1. **Build Mobile App**
   ```bash
   cd /opt/safeguardian
   cp -r /path/to/safeguardian/mobile ./
   cd mobile
   
   # Install dependencies
   npm install
   
   # Build for production
   npm run build
   ```

2. **Build Dashboard**
   ```bash
   cd /opt/safeguardian
   cp -r /path/to/safeguardian/dashboard ./
   cd dashboard
   
   # Install dependencies
   npm install
   
   # Build for production
   npm run build
   ```

3. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/safeguardian
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /path/to/ssl/certificate.crt;
       ssl_certificate_key /path/to/ssl/private.key;
       
       # Mobile App
       location / {
           root /opt/safeguardian/mobile/dist;
           try_files $uri $uri/ /index.html;
       }
       
       # Dashboard
       location /dashboard {
           alias /opt/safeguardian/dashboard/dist;
           try_files $uri $uri/ /dashboard/index.html;
       }
       
       # API Backend
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       # WebSocket
       location /ws {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

4. **Enable Nginx Configuration**
   ```bash
   sudo ln -s /etc/nginx/sites-available/safeguardian /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Step 5: SSL Certificate Setup

1. **Install Certbot**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. **Obtain SSL Certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Configure Auto-Renewal**
   ```bash
   sudo crontab -e
   # Add line:
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Step 6: Monitoring and Logging

1. **Configure Log Rotation**
   ```bash
   sudo nano /etc/logrotate.d/safeguardian
   ```
   
   ```
   /opt/safeguardian/logs/*.log {
       daily
       missingok
       rotate 30
       compress
       delaycompress
       notifempty
       create 644 safeguardian safeguardian
       postrotate
           systemctl reload safeguardian-backend
       endscript
   }
   ```

2. **Set Up System Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install -y htop iotop nethogs
   
   # Configure system alerts
   sudo apt install -y mailutils
   ```

### Step 7: Backup Configuration

1. **Database Backup Script**
   ```bash
   sudo nano /opt/safeguardian/scripts/backup-database.sh
   ```
   
   ```bash
   #!/bin/bash
   BACKUP_DIR="/opt/safeguardian/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   # Database backup
   pg_dump -h localhost -U safeguardian_user safeguardian_db > $BACKUP_DIR/db_backup_$DATE.sql
   
   # Compress backup
   gzip $BACKUP_DIR/db_backup_$DATE.sql
   
   # Remove backups older than 30 days
   find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
   ```

2. **Schedule Backups**
   ```bash
   sudo crontab -e
   # Add line:
   0 2 * * * /opt/safeguardian/scripts/backup-database.sh
   ```

## Post-Deployment Verification

### Health Checks

1. **Backend API Health**
   ```bash
   curl -k https://your-domain.com/api/health
   ```

2. **Database Connection**
   ```bash
   curl -k https://your-domain.com/api/status
   ```

3. **WebSocket Connection**
   ```bash
   # Test WebSocket endpoint
   wscat -c wss://your-domain.com/ws
   ```

### Performance Testing

1. **Load Testing**
   ```bash
   # Install Apache Bench
   sudo apt install -y apache2-utils
   
   # Test API performance
   ab -n 1000 -c 10 https://your-domain.com/api/health
   ```

2. **Database Performance**
   ```sql
   -- Check database performance
   SELECT * FROM pg_stat_activity;
   SELECT * FROM pg_stat_database;
   ```

### Security Verification

1. **SSL Configuration**
   ```bash
   # Test SSL configuration
   openssl s_client -connect your-domain.com:443 -servername your-domain.com
   ```

2. **Firewall Status**
   ```bash
   sudo ufw status verbose
   ```

3. **Service Security**
   ```bash
   # Check running services
   sudo netstat -tulpn
   
   # Check open ports
   sudo ss -tulpn
   ```

## Maintenance Procedures

### Regular Maintenance Tasks

1. **Daily Tasks**
   - Monitor system logs
   - Check service status
   - Verify backup completion
   - Review security alerts

2. **Weekly Tasks**
   - Update system packages
   - Review performance metrics
   - Check disk space usage
   - Analyze user activity logs

3. **Monthly Tasks**
   - Security audit
   - Performance optimization
   - Database maintenance
   - Backup verification

### Update Procedures

1. **Backend Updates**
   ```bash
   cd /opt/safeguardian/backend
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart safeguardian-backend
   ```

2. **Frontend Updates**
   ```bash
   cd /opt/safeguardian/mobile
   git pull origin main
   npm install
   npm run build
   
   cd /opt/safeguardian/dashboard
   git pull origin main
   npm install
   npm run build
   
   sudo systemctl reload nginx
   ```

## Troubleshooting

### Common Issues

1. **Backend Service Won't Start**
   ```bash
   # Check logs
   sudo journalctl -u safeguardian-backend -f
   
   # Check configuration
   cd /opt/safeguardian/backend
   source venv/bin/activate
   python src/main.py
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Test connection
   psql -h localhost -U safeguardian_user -d safeguardian_db
   ```

3. **Frontend Not Loading**
   ```bash
   # Check Nginx logs
   sudo tail -f /var/log/nginx/error.log
   
   # Test Nginx configuration
   sudo nginx -t
   ```

### Performance Issues

1. **High CPU Usage**
   ```bash
   # Monitor processes
   htop
   
   # Check backend performance
   curl https://your-domain.com/api/stats
   ```

2. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Monitor database memory
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Database Performance**
   ```sql
   -- Analyze slow queries
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;
   ```

## Security Considerations

### Access Control

1. **User Management**
   - Implement role-based access control
   - Regular access reviews
   - Strong password policies
   - Multi-factor authentication

2. **Network Security**
   - Firewall configuration
   - VPN access for administrators
   - Regular security updates
   - Intrusion detection system

### Data Protection

1. **Encryption**
   - Data at rest encryption
   - Data in transit encryption
   - Key management procedures
   - Regular key rotation

2. **Backup Security**
   - Encrypted backups
   - Secure backup storage
   - Regular restore testing
   - Offsite backup copies

### Compliance

1. **Legal Requirements**
   - GDPR compliance
   - COPPA compliance
   - Local privacy laws
   - Data retention policies

2. **Audit Trail**
   - Comprehensive logging
   - Log integrity protection
   - Regular audit reviews
   - Incident response procedures

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancing**
   ```nginx
   upstream safeguardian_backend {
       server 10.0.1.10:5000;
       server 10.0.1.11:5000;
       server 10.0.1.12:5000;
   }
   ```

2. **Database Clustering**
   - Master-slave replication
   - Connection pooling
   - Read replicas
   - Sharding strategies

### Vertical Scaling

1. **Resource Optimization**
   - CPU optimization
   - Memory tuning
   - Storage optimization
   - Network optimization

2. **Performance Monitoring**
   - Application metrics
   - Database metrics
   - System metrics
   - User experience metrics

## Support and Documentation

### Getting Help

- **Documentation:** https://docs.safeguardian.com
- **Support Email:** support@safeguardian.com
- **Emergency Contact:** emergency@safeguardian.com
- **Community Forum:** https://community.safeguardian.com

### Additional Resources

- **API Documentation:** https://api.safeguardian.com/docs
- **User Guides:** https://help.safeguardian.com
- **Developer Resources:** https://dev.safeguardian.com
- **Security Guidelines:** https://security.safeguardian.com

---

*This deployment guide is maintained by the SafeGuardian development team. For updates and corrections, please contact the development team.*

