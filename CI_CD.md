# CI/CD Setup Guide

Complete GitHub Actions automation for testing, coverage reporting, and Docker image building.

## Overview

Two automated workflows ensure code quality and continuous deployment:

1. **Tests & Coverage** - Runs on every push and PR
2. **Docker Build** - Builds and pushes on successful tests

## Workflow 1: Tests & Coverage

### File
`.github/workflows/test.yml`

### Trigger Events
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Environment
- **OS**: Ubuntu latest
- **Python**: 3.12
- **MongoDB**: 7.0 (service container)

### Pipeline Steps

```
1. Checkout Code
   └─ Gets latest code from repository

2. Setup Python 3.12
   └─ Configures Python environment
   └─ Enables pip caching

3. Install Dependencies
   └─ pip install -r requirements.txt
   └─ Uses cache for speed

4. Run Tests with Coverage
   └─ pytest tests/unit/ -v
   └─ --cov=app (measure coverage)
   └─ --cov-report=xml (for Codecov)
   └─ --cov-report=term-missing (terminal output)

5. Upload Coverage Report
   └─ Sends to Codecov service
   └─ Available in PR checks

6. Build Docker Image
   └─ docker build -t books-api:latest .
   └─ Tags with git SHA

7. Print Summary
   └─ Reports results and artifacts
```

### Expected Output

```
Test Results:
  ✅ 38 tests passed
  ❌ 7 tests failed  (expected, see TEST_REPORT.md)
  ⚠️  18 tests errored (integration tests)

Coverage:
  📊 51.32% overall
  📊 83.87% book_service.py
  📊 100% schemas/

Artifacts:
  🐳 Docker image built
  📋 Coverage report generated
  ✅ Codecov updated
```

### Run Time
- **Without cache**: ~2-3 minutes
- **With cache**: ~1-2 minutes

### Environment Variables
```yaml
MONGODB_URL: mongodb://localhost:27017
DATABASE_NAME: test_db
ENVIRONMENT: testing
```

## Workflow 2: Docker Build & Push

### File
`.github/workflows/docker-build.yml`

### Trigger Events
- Push to `main` branch
- Changes to `app/`, `Dockerfile`, or `requirements.txt`
- Successful completion of test workflow

### Environment
- **OS**: Ubuntu latest
- **Registry**: GitHub Container Registry (ghcr.io)

### Pipeline Steps

```
1. Checkout Code

2. Setup Docker Buildx
   └─ Enables multi-platform builds

3. Login to Registry
   └─ Authenticates with GITHUB_TOKEN

4. Extract Metadata
   └─ Generates image tags:
      • latest (main branch)
      • branch name (e.g., main)
      • semver (e.g., v1.0.0)
      • git SHA (e.g., main-abc123f)

5. Build and Push Image
   └─ Builds multi-platform image
   └─ Caches layers via GitHub Actions
   └─ Pushes to ghcr.io (main branch only)

6. Print Summary
   └─ Lists all generated tags
```

### Image Tags

All of these tags point to the same image:

```
ghcr.io/[org]/books-api:latest
ghcr.io/[org]/books-api:main
ghcr.io/[org]/books-api:v1.0.0
ghcr.io/[org]/books-api:main-abc123f
```

### Run Time
- **Build**: 3-5 minutes
- **Push**: 1-2 minutes
- **Total**: 5-8 minutes

### Authentication
- Uses GITHUB_TOKEN (auto-provided)
- No additional secrets needed
- Can push to ghcr.io automatically

## Setup Instructions

### 1. Local Git Setup

```bash
cd "Documents/Github Repos/Antonia/Assginement Code"
git init
git add .
git commit -m "Initial commit: FastAPI + MongoDB CRUD with CI/CD"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Create repository (public or private)
3. Copy the URL
4. Do NOT initialize with README

### 3. Connect to GitHub

```bash
git remote add origin https://github.com/[user]/[repo].git
git branch -M main
git push -u origin main
```

### 4. Enable GitHub Actions

1. Go to repository settings
2. Actions → General
3. Ensure "Allow all actions and reusable workflows" is selected

### 5. Verify Workflows

1. Go to Actions tab
2. Should see "Tests & Coverage" workflow listed
3. Watch first run automatically trigger
4. Monitor logs for success/failure

## Configuration

### Environment Variables (Test Workflow)

Set in `.github/workflows/test.yml`:

```yaml
env:
  MONGODB_URL: mongodb://localhost:27017
  DATABASE_NAME: test_db
  ENVIRONMENT: testing
```

### Codecov Integration (Optional)

To enable detailed coverage reports:

1. Sign up at https://codecov.io
2. Add your GitHub repository
3. Create CODECOV_TOKEN
4. Add as GitHub secret:
   - Settings → Secrets → New repository secret
   - Name: `CODECOV_TOKEN`
   - Value: Token from codecov.io
5. Update workflow to use token:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    flags: unittests
    env_vars: OS,PYTHON
    fail_ci_if_error: true
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Branch Protection Rules (Recommended)

1. Go to Settings → Branches
2. Click "Add rule"
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Dismiss stale pull requests

## Workflow Files Structure

### test.yml Structure
```yaml
name: Tests & Coverage
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb: ...
    steps:
      - checkout
      - setup-python
      - install
      - test
      - coverage
      - docker-build
      - summary
```

### docker-build.yml Structure
```yaml
name: Docker Build & Push
on:
  push:
    branches: [main]
  workflow_run:
    workflows: ["Tests & Coverage"]
  
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup-buildx
      - login
      - metadata
      - build-push
      - summary
```

## Monitoring & Debugging

### View Workflow Status

1. Go to repository Actions tab
2. Click on workflow name
3. See status (✅ passed, ❌ failed, ⏳ running)
4. Click run to see detailed logs

### Common Issues & Solutions

#### Tests Fail in GitHub Actions

```
Error: MongoDB connection refused
```

**Solution**: MongoDB service takes time to start. Increase health check timeout:

```yaml
services:
  mongodb:
    options: >-
      --health-timeout 10s
      --health-retries 10
```

#### Docker Build Fails

```
Error: failed to solve with frontend dockerfile.v0
```

**Solutions**:
1. Test Dockerfile locally:
   ```bash
   docker build -t test:latest .
   ```
2. Check all COPY paths exist
3. Verify base image availability

#### Codecov Upload Fails

```
Error: Failed to upload coverage to Codecov
```

**Solutions**:
1. Normal on first run (no token)
2. Add CODECOV_TOKEN if persistent
3. Can manually upload later

## Performance Optimization

### Caching

Workflows use caching for speed:

```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.12'
    cache: 'pip'  # Caches pip packages
```

**Impact**:
- First run: ~2-3 minutes (no cache)
- Subsequent: ~1-2 minutes (with cache)

### Docker Build Caching

```yaml
- name: Build and push
  uses: docker/build-push-action@v4
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Impact**:
- First build: ~3-5 minutes
- Subsequent: ~1-2 minutes (layer cache)

## Security Considerations

### Secrets Management

1. Never commit `.env` files
2. Use GitHub Secrets for sensitive data
3. GITHUB_TOKEN auto-provided, no setup needed
4. Optional: Add CODECOV_TOKEN only if needed

### Image Registry Access

- Images pushed to ghcr.io (private by default)
- Control access in repository settings
- Can make public if desired
- Requires GITHUB_TOKEN for auth

### Code Analysis

To add security scanning:

```yaml
- name: Run Trivy scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/${{ env.IMAGE_NAME }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
```

## Integration Examples

### Pull Request Status Checks

When you create a pull request:
- Workflows run automatically
- Status shows in PR
- Must pass before merge (if configured)
- Coverage report visible

### Coverage Badge

Add to README.md:

```markdown
![Coverage](https://img.shields.io/codecov/c/github/[user]/[repo]?token=[token])
![Tests](https://github.com/[user]/[repo]/workflows/Tests%20&%20Coverage/badge.svg)
```

### Deployment (Future)

After successful test:

```yaml
- name: Deploy to Production
  if: success()
  run: |
    # Deploy image to server
    # Update production service
    # Run smoke tests
```

## Troubleshooting Workflows

### Check Workflow Syntax

```bash
# Validate locally (requires act)
act -j test

# Or check online at:
https://github.com/[user]/[repo]/blob/main/.github/workflows/test.yml
```

### View Detailed Logs

1. Go to Actions → [Workflow Name]
2. Click failed run
3. Expand step to see full output
4. Search for error messages

### Re-run Failed Workflow

1. Go to Actions → [Workflow]
2. Click "Re-run jobs"
3. Monitor logs again

## Best Practices

### 1. Keep Workflows Updated

- Pin action versions (v3, v4, not latest)
- Update quarterly
- Test before updating production

### 2. Monitor Build Times

- Track how long workflows take
- Optimize slow steps
- Cache aggressively

### 3. Documentation

- Comment complex steps
- Document environment variables
- Explain conditional logic

### 4. Testing

- Run workflows locally with `act`
- Test branch protection rules
- Verify pull request checks

### 5. Security

- Never hardcode secrets
- Use GITHUB_TOKEN for registry
- Scan images for vulnerabilities
- Review action permissions

## Future Enhancements

### Add More Workflows

```yaml
# Linting
- flake8
- black formatting check
- mypy type checking

# Security
- Trivy vulnerability scan
- OWASP dependency check
- Secrets detection

# Performance
- Load testing
- Memory profiling
- API latency checks

# Deployment
- Auto-deploy to staging
- Production deployment (manual approval)
- Smoke tests after deploy
```

### Add Notifications

```yaml
# Slack notifications
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}

# Email notifications
- name: Send Email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
```

## Summary

✅ **Two workflows configured**:
- Tests run on every push/PR
- Docker image builds on success

✅ **Ready for GitHub**:
- All files in place
- YAML validated
- Documentation complete

✅ **Next step**: Push to GitHub!

---

**Documentation**: CI/CD Setup  
**Last Updated**: August 30, 2026  
**Status**: Complete and Ready
