# Alpine Migration - Quick Reference Card

**Created:** November 7, 2025
**Project:** IOLTA Guard (100+ firm deployment)

---

## 🚀 One-Command Migration

```bash
./migrate-to-alpine.sh
```

**Duration:** 30-45 minutes
**What it does:** Backup → Build → Migrate → Verify

---

## 📋 Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `migrate-to-alpine.sh` | Full migration automation | `./migrate-to-alpine.sh` |
| `compare-pdfs.sh` | Setup PDF comparison workspace | `./compare-pdfs.sh` |
| `monitor-alpine.sh` | Monitor Alpine stack health | `./monitor-alpine.sh --watch` |

---

## ⚡ Quick Commands

### Build & Deploy

```bash
# Build Alpine images
docker-compose -f docker-compose.alpine.yml build

# Start Alpine stack
docker-compose -f docker-compose.alpine.yml up -d

# Check status
docker-compose -f docker-compose.alpine.yml ps
```

### Health Checks

```bash
# Quick health check
curl http://localhost/api/health/

# Continuous monitoring
./monitor-alpine.sh --watch

# Full report
./monitor-alpine.sh --full
```

### Logs

```bash
# All services
docker-compose -f docker-compose.alpine.yml logs -f

# Backend only
docker-compose -f docker-compose.alpine.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.alpine.yml logs --tail=100
```

### Troubleshooting

```bash
# Restart services
docker-compose -f docker-compose.alpine.yml restart

# Rebuild without cache
docker-compose -f docker-compose.alpine.yml build --no-cache

# Remove everything and start fresh
docker-compose -f docker-compose.alpine.yml down -v
docker-compose -f docker-compose.alpine.yml up -d
```

---

## 🔄 Migration Workflow

```
1. Review Documentation
   ↓
2. Run Migration Script
   ./migrate-to-alpine.sh
   ↓
3. Verify Services
   ./monitor-alpine.sh
   ↓
4. Compare PDFs (CRITICAL!)
   ./compare-pdfs.sh
   ↓
5. Bank Validation
   Submit test check
   ↓
6. Load Testing
   See TESTING_CHECKLIST_ALPINE.md
   ↓
7. Pilot Deployment (2-5 firms)
   Monitor for 1-2 weeks
   ↓
8. Full Rollout
   Gradual deployment to all firms
```

---

## 🆘 Emergency Rollback

```bash
# Automated rollback
./migrate-to-alpine.sh --rollback

# OR Manual rollback
docker-compose -f docker-compose.alpine.yml down
docker-compose up -d
```

**Rollback time:** ~5 minutes
**Data preserved:** Yes (same volumes)

---

## 📊 Image Size Comparison

| Service | Debian | Alpine | Saved |
|---------|--------|--------|-------|
| Backend | 900MB | 350MB | 61% |
| Frontend | 150MB | 45MB | 70% |
| Database | 380MB | 260MB | 32% |
| **Total** | **1.4GB** | **655MB** | **53%** |

**At 100 firms:** ~75GB saved

---

## ✅ Pre-Migration Checklist

- [ ] `.env` file configured
- [ ] Backup created
- [ ] Disk space: 20GB+
- [ ] Docker 20.10+
- [ ] Docker Compose 2.0+

```bash
# Quick check
docker --version
docker-compose --version
df -h
```

---

## ⚠️ Critical Testing

### PDF Checks (MANDATORY!)

```bash
# Setup comparison workspace
./compare-pdfs.sh

# Generate and compare PDFs
cd pdf_comparison_*/
# Follow instructions in COMPARISON_INSTRUCTIONS.md
```

**Must verify:**
- ✅ Check printing pixel-perfect
- ✅ Bank approves check format
- ✅ All reports identical

**If ANY differences found:** DO NOT deploy to production

---

## 📈 Monitoring

### Real-time Monitoring

```bash
# Watch mode (refreshes every 5s)
./monitor-alpine.sh --watch

# Custom interval
./monitor-alpine.sh --watch --interval 10

# Monitor for specific duration
./monitor-alpine.sh --duration 300  # 5 minutes
```

### One-time Checks

```bash
# Full report
./monitor-alpine.sh --full

# Just health status
./monitor-alpine.sh --health

# Database stats
./monitor-alpine.sh --db

# Recent errors
./monitor-alpine.sh --logs
```

---

## 🔍 Verification

### After Migration

```bash
# 1. Services running
docker-compose -f docker-compose.alpine.yml ps

# 2. Health endpoints
curl http://localhost/api/health/
curl http://localhost/

# 3. Database accessible
docker-compose -f docker-compose.alpine.yml exec database \
  psql -U iolta_user -d iolta_guard_db -c "SELECT COUNT(*) FROM clients_client;"

# 4. No errors in logs
docker-compose -f docker-compose.alpine.yml logs | grep -i error

# 5. Resource usage reasonable
docker stats --no-stream
```

---

## 💾 Backup & Restore

### Create Backup

```bash
# Automated (part of migration)
./migrate-to-alpine.sh --backup-only

# Manual database backup
docker-compose -f docker-compose.alpine.yml exec database \
  pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d).sql
```

### Restore Backup

```bash
# Locate backup
ls -lh migration_backups/

# Restore database
docker cp backup.sql iolta_db_alpine:/tmp/
docker-compose -f docker-compose.alpine.yml exec database \
  psql -U iolta_user -d iolta_guard_db -f /tmp/backup.sql
```

---

## 🎯 Performance Targets

| Metric | Target | Check |
|--------|--------|-------|
| Startup time | <2 min | `time docker-compose up -d` |
| Health check | <100ms | `curl http://localhost/api/health/` |
| Dashboard load | <2s | Browser dev tools |
| PDF generation | <5s | Test check printing |
| Memory usage | <2GB total | `docker stats` |

---

## 🔒 Security Checks

```bash
# 1. Verify non-root execution
docker-compose -f docker-compose.alpine.yml exec backend whoami
# Should return: iolta

# 2. Verify musl libc
docker-compose -f docker-compose.alpine.yml exec backend ldd --version
# Should show: musl libc

# 3. Check exposed ports
docker-compose -f docker-compose.alpine.yml port backend 8002
# Should return: nothing (not exposed)

# 4. Scan for vulnerabilities (if Trivy installed)
trivy image iolta-guard-backend-alpine:latest
```

---

## 📞 Getting Help

### Documentation Files

```
ALPINE_MIGRATION_SUMMARY.md       ← Start here
BUILD_INSTRUCTIONS_ALPINE.md      ← Build guide
TESTING_CHECKLIST_ALPINE.md       ← Testing protocol
MIGRATION_QUICK_REFERENCE.md      ← This file
amin_20251107.md                  ← Code review notes
```

### Log Locations

```
./migration.log                    ← Migration script log
./migration_backups/               ← Backups directory
./pdf_comparison_*/                ← PDF comparison workspace
```

### Common Issues

| Problem | Quick Fix |
|---------|-----------|
| Build fails | `docker system prune -a && rebuild` |
| Services won't start | Check `.env` file, verify passwords |
| Frontend 502 | `docker-compose restart backend` |
| Database errors | Check logs: `docker-compose logs database` |

---

## 🚦 Deployment Stages

### Stage 1: Development Testing (Week 1)

```bash
# Build and test locally
./migrate-to-alpine.sh
./monitor-alpine.sh --watch
```

### Stage 2: PDF Validation (Week 2)

```bash
# Critical testing
./compare-pdfs.sh
# Follow PDF comparison checklist
```

### Stage 3: Pilot (Week 3)

- Deploy to 2-5 firms
- Monitor closely
- Collect feedback

### Stage 4: Gradual Rollout (Week 4+)

- 10 firms/week
- Monitor error rates
- Adjust as needed

---

## 📊 Success Metrics

Track these after migration:

- [ ] All services healthy
- [ ] Zero PDF differences
- [ ] Bank approves checks
- [ ] Performance meets targets
- [ ] No security vulnerabilities
- [ ] Pilot firms satisfied
- [ ] Error rate <0.1%

---

## ⚙️ Environment Variables

**Required in `.env`:**

```env
DB_PASSWORD=<secure-password>
DJANGO_SECRET_KEY=<50-char-key>
```

**Generate:**

```bash
# Database password
openssl rand -base64 32

# Django secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 🔢 Key Numbers (100 Firms)

| Metric | Value |
|--------|-------|
| Image size savings | 75GB |
| Annual cost savings | $8-13K |
| Security improvement | 40x smaller code |
| Build time | 20-25 min |
| Deploy time | 2 min |
| Rollback time | 5 min |

---

## 📝 Quick Testing

```bash
# 1-minute smoke test
curl http://localhost/api/health/ && \
docker-compose -f docker-compose.alpine.yml ps && \
docker stats --no-stream && \
echo "✓ Basic checks passed"
```

---

## 🎓 Key Learnings

**Alpine Benefits:**
- ✅ 53% smaller images
- ✅ musl libc security
- ✅ Faster deployments
- ✅ Lower costs at scale

**Challenges:**
- ⚠️ Longer build times (first build)
- ⚠️ PDF testing critical
- ⚠️ Bank validation required

**Decision:**
- ✅ Worth it for 100+ firms
- ✅ Worth it for security
- ❌ Not worth it for single deployment

---

**Last Updated:** November 7, 2025
**Version:** 1.0
**Status:** Ready for Use
