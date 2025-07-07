# SafeGuardian Mobile App - CapRover Deployment Guide

## 🚀 Overview

This guide will help you deploy the SafeGuardian mobile app to CapRover, a self-hosted Platform-as-a-Service (PaaS) that makes deployment simple and efficient.

## 📋 Prerequisites

### CapRover Server Requirements
- **Server**: VPS or dedicated server with at least 1GB RAM
- **Operating System**: Ubuntu 18.04+ or CentOS 7+
- **Domain**: A domain name pointing to your server
- **Ports**: 80, 443, and 3000 open
- **Docker**: Docker and Docker Compose installed

### Local Requirements
- **Node.js**: Version 18 or higher
- **pnpm**: Package manager (or npm/yarn)
- **CapRover CLI**: Installed globally (`npm install -g caprover`)

## 🛠️ CapRover Server Setup

### 1. Install CapRover on Your Server

```bash
# SSH into your server
ssh root@your-server-ip

# Install CapRover
docker run -p 80:80 -p 443:443 -p 3000:3000 -v /var/run/docker.sock:/var/run/docker.sock -v /captain:/captain caprover/caprover
```

### 2. Complete CapRover Setup

1. Visit `http://your-server-ip:3000` in your browser
2. Follow the setup wizard
3. Set your root domain (e.g., `your-domain.com`)
4. Enable HTTPS with Let's Encrypt
5. Create your captain password

### 3. Configure DNS

Point your domain to your server:
```
A Record: your-domain.com → your-server-ip
A Record: *.your-domain.com → your-server-ip
```

## 📱 Application Deployment

### 1. Prepare the Application

```bash
# Clone or navigate to the SafeGuardian mobile app directory
cd safeguardian-mobile

# Install dependencies
pnpm install

# Build the application (optional - CapRover will do this)
pnpm run build
```

### 2. Configure CapRover CLI

```bash
# Login to your CapRover instance
caprover login

# Follow the prompts:
# - CapRover URL: https://captain.your-domain.com
# - Password: your-captain-password
# - Name: safeguardian (or any name you prefer)
```

### 3. Deploy the Application

#### Option A: Direct Deployment

```bash
# Deploy directly from the current directory
caprover deploy

# Follow the prompts:
# - App Name: safeguardian-mobile
# - Branch: main (or your current branch)
```

#### Option B: Create App First, Then Deploy

```bash
# Create a new app
caprover apps:create safeguardian-mobile

# Deploy to the created app
caprover deploy --appName safeguardian-mobile
```

### 4. Configure App Settings

After deployment, configure your app in the CapRover dashboard:

1. Go to `https://captain.your-domain.com`
2. Navigate to "Apps" → "safeguardian-mobile"
3. Configure the following:

####

