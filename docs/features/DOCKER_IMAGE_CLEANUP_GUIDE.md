# Docker Image Cleanup Guide - Customer Server

**Date:** November 13, 2025  
**Purpose:** Remove old/unused Docker images from customer server  
**⚠️ IMPORTANT:** Follow steps carefully to avoid deleting active images

---

## 🔍 **STEP 1: Check Current Images**

### **List All Images:**
```bash
docker images

# Expected output shows:
# REPOSITORY                          TAG        IMAGE ID       CREATED        SIZE
# iolta-guard-backend-alpine         latest     abc123def456   2 days ago     350MB
# iolta-guard-frontend-alpine        latest     def456ghi789   2 days ago     45MB
# postgres                           16-alpine  ghi789jkl012   2 weeks ago    260MB
# (and possibly old images)
```

### **Check Running Containers:**
```bash
# CRITICAL: Don't delete images used by running containers!
docker ps -a

# Shows which images are currently in use
```

### **Check Image Usage:**
```bash
# See which containers use which images
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

---

## 🗑️ **STEP 2: Safe Cleanup Options**

### **Option 1: Remove Dangling Images (SAFEST)**
```bash
# Removes only unused/dangling images (no tag, not used by containers)
docker image prune

# With confirmation prompt:
# WARNING! This will remove all dangling images.
# Are you sure you want to continue? [y/N] y
```

**What it removes:**
- ✅ Build cache layers
- ✅ Intermediate images
- ✅ Images with `<none>` tag
- ❌ Does NOT remove tagged images
- ❌ Does NOT remove images used by stopped containers

---

### **Option 2: Remove All Unused Images (MODERATE)**
```bash
# Removes all images not used by any container (running or stopped)
docker image prune -a

# With confirmation prompt:
# WARNING! This will remove all images without at least one container associated to them.
# Are you sure you want to continue? [y/N] y
```

**What it removes:**
- ✅ All dangling images
- ✅ All unused tagged images
- ❌ Does NOT remove images used by stopped containers

**⚠️ Caution:** If you have stopped containers you want to keep, their images won't be deleted

---

### **Option 3: Remove Specific Old Images (TARGETED)**
```bash
# First, list images with old tags/names
docker images | grep -E "iolta|trust"

# Remove specific old image by name:tag
docker rmi iolta-guard-backend:old-tag
docker rmi iolta-guard-frontend:old-tag

# Remove specific image by IMAGE ID
docker rmi abc123def456

# Force remove (if image is used by stopped container)
docker rmi -f abc123def456
```

---

### **Option 4: Complete Cleanup (AGGRESSIVE)**
```bash
# ⚠️ WARNING: This removes EVERYTHING not currently running

# 1. Stop all containers (if safe to do so)
docker-compose -f docker-compose.alpine.yml down

# 2. Remove all stopped containers
docker container prune -f

# 3. Remove all unused images
docker image prune -a -f

# 4. Remove all unused volumes (⚠️ DELETES DATA!)
docker volume prune -f

# 5. Remove all unused networks
docker network prune -f

# 6. Restart services
docker-compose -f docker-compose.alpine.yml up -d
```

**⚠️ EXTREME CAUTION:** This deletes all unused resources including volumes!

---

## 📋 **RECOMMENDED CLEANUP SEQUENCE**

### **For Customer Server (Safe Approach):**

```bash
# Step 1: Check what's running
docker ps

# Expected output:
# iolta_db_alpine          Up 2 days
# iolta_backend_alpine     Up 2 days
# iolta_frontend_alpine    Up 2 days

# Step 2: Check all images
docker images

# Look for:
# - Old images with different names
# - Images with <none> tag
# - Debian-based images (python:3.12-slim, nginx:latest without alpine)

# Step 3: Remove dangling images (safest)
docker image prune

# Type: y

# Step 4: Check space saved
docker system df

# Shows:
# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          5         3         1.2GB     500MB (41%)
# Containers      3         3         120MB     0B (0%)
# Local Volumes   5         5         2.5GB     0B (0%)

# Step 5: If more cleanup needed, remove unused images
docker image prune -a

# Type: y
```

---

## 🎯 **IDENTIFY OLD NON-ALPINE IMAGES**

### **Find Debian-Based Images:**
```bash
# List images and check base OS
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Look for:
# - Larger sizes (Debian images are ~800MB vs Alpine ~350MB)
# - Tags without "alpine" in name
# - Old repository names
```

### **Check Image Details:**
```bash
# Inspect image to see base OS
docker inspect <image-id> | grep -i "alpine\|debian"

# Alpine images show: "alpine" or "musl"
# Debian images show: "debian" or "glibc"
```

### **Remove Old Debian Images:**
```bash
# List non-alpine images
docker images | grep -v alpine | grep iolta

# Remove them (replace with actual image names)
docker rmi iolta-guard-backend:latest
docker rmi iolta-guard-frontend:latest
docker rmi trust-account-backend:latest
```

---

## 🔍 **VERIFY CLEANUP**

### **After Cleanup:**
```bash
# 1. Check remaining images
docker images

# Should only show:
# - iolta-guard-backend-alpine:latest
# - iolta-guard-frontend-alpine:latest
# - postgres:16-alpine3.20 (or 16-alpine)

# 2. Verify services still running
docker ps

# All 3 containers should be Up

# 3. Check disk space saved
docker system df

# 4. Test application
curl http://localhost/
curl http://localhost/api/health/
```

---

## 💾 **DISK SPACE ANALYSIS**

### **Check Docker Disk Usage:**
```bash
# Summary
docker system df

# Detailed breakdown
docker system df -v

# Shows:
# - Images (with size and usage)
# - Containers (with size)
# - Volumes (with size)
# - Build cache (with size)
```

### **Check System Disk Space:**
```bash
# Overall disk usage
df -h

# Docker specific
sudo du -sh /var/lib/docker/*
```

---

## 🚨 **TROUBLESHOOTING**

### **Problem: "Image is being used by stopped container"**
```bash
# List stopped containers
docker ps -a --filter "status=exited"

# Remove stopped containers
docker container prune

# Or remove specific container
docker rm <container-name>

# Then try removing image again
docker rmi <image-id>
```

### **Problem: "Image is being used by running container"**
```bash
# ⚠️ DON'T force remove! This will break running services

# Instead:
# 1. Stop the service
docker stop <container-name>

# 2. Remove the container
docker rm <container-name>

# 3. Remove the image
docker rmi <image-id>

# 4. Recreate with new image
docker-compose -f docker-compose.alpine.yml up -d
```

### **Problem: "No space left on device"**
```bash
# Emergency cleanup (use with caution)
docker system prune -a --volumes -f

# This removes:
# - All stopped containers
# - All unused images
# - All unused volumes (⚠️ DATA LOSS!)
# - All unused networks
# - All build cache
```

---

## 📊 **EXPECTED CLEANUP RESULTS**

### **Before Cleanup (Typical Customer Server):**
```
Images:           8 images      ~2.5GB
- postgres:16-alpine           260MB   (keep)
- iolta-guard-backend-alpine   350MB   (keep)
- iolta-guard-frontend-alpine   45MB   (keep)
- iolta-guard-backend:latest   800MB   (DELETE - old Debian)
- trust-account-backend:old    800MB   (DELETE - old)
- python:3.12-slim             900MB   (DELETE - unused)
- nginx:latest                 150MB   (DELETE - old)
- <none>:<none>                200MB   (DELETE - dangling)
```

### **After Cleanup:**
```
Images:           3 images      ~655MB
- postgres:16-alpine           260MB
- iolta-guard-backend-alpine   350MB
- iolta-guard-frontend-alpine   45MB

Space Saved: ~1.85GB (74% reduction)
```

---

## ⚙️ **AUTOMATED CLEANUP (Optional)**

### **Create Cleanup Script:**
```bash
cat > /usr/local/bin/docker-cleanup.sh << 'SCRIPT'
#!/bin/bash
# Docker cleanup script - Run weekly

echo "=== Docker Cleanup $(date) ==="

# Remove dangling images
echo "Removing dangling images..."
docker image prune -f

# Remove stopped containers older than 24 hours
echo "Removing old stopped containers..."
docker container prune --filter "until=24h" -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Show disk usage
echo "Current disk usage:"
docker system df

echo "=== Cleanup complete ==="
SCRIPT

chmod +x /usr/local/bin/docker-cleanup.sh

# Test it
/usr/local/bin/docker-cleanup.sh
```

### **Schedule Weekly Cleanup (Cron):**
```bash
# Add to crontab
crontab -e

# Add line (runs every Sunday at 3 AM):
0 3 * * 0 /usr/local/bin/docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1
```

---

## ✅ **SAFE CLEANUP CHECKLIST**

**Before Cleanup:**
- [ ] Verified which containers are running: `docker ps`
- [ ] Checked which images are in use: `docker ps -a`
- [ ] Listed all images: `docker images`
- [ ] Identified old/unused images
- [ ] Backed up important data (if any)

**During Cleanup:**
- [ ] Started with safest option (dangling images only)
- [ ] Confirmed each deletion
- [ ] Monitored for errors
- [ ] Didn't force remove images used by running containers

**After Cleanup:**
- [ ] Verified services still running: `docker ps`
- [ ] Tested application: `curl http://localhost/`
- [ ] Checked disk space saved: `docker system df`
- [ ] Verified only Alpine images remain: `docker images`
- [ ] Documented what was removed

---

## 🎯 **QUICK REFERENCE**

```bash
# Safe cleanup (recommended)
docker image prune

# Aggressive cleanup (removes all unused)
docker image prune -a

# Complete system cleanup (⚠️ careful!)
docker system prune -a

# Remove specific image
docker rmi <image-name>:<tag>

# Force remove (use carefully)
docker rmi -f <image-id>

# Check disk usage
docker system df

# List all images
docker images

# List running containers
docker ps
```

---

**Recommendation for Customer Server:**

1. **Start Safe:** `docker image prune` (removes only dangling)
2. **Check Results:** `docker system df`
3. **If More Needed:** `docker image prune -a` (removes all unused)
4. **Verify:** `docker ps` and test application
5. **Only Keep:** Alpine-based images (postgres:16-alpine, *-alpine:latest)

---

**Status:** Ready to clean customer server  
**Recommended Command:** `docker image prune -a`  
**Expected Space Saved:** ~1-2 GB

---

*Safe cleanup procedure for removing old Docker images.*
