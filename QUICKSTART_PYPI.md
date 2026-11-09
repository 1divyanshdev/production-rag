# PyPI Publishing Quick Start

## First Time Setup (Do Once)

### 1. Get Your PyPI API Token
- Go to: https://pypi.org/manage/account/token/
- Click "Add API token"
- Token name: `production-rag-publisher`
- Scope: "Entire account"
- Copy the token (starts with `pypi-`)

### 2. Configure GitHub Secret
- Go to: https://github.com/1divyanshdev/production-rag/settings/secrets/actions
- Click "New repository secret"
- Name: `PYPI_API_TOKEN`
- Value: Paste your full token
- Save

### 3. Push the Automation Workflow
```bash
git add .github/workflows/publish.yml docs/PUBLISHING.md QUICKSTART_PYPI.md
git commit -m "Add automated PyPI publishing"
git push origin main
```

---

## Publishing the First Release (v0.1.0)

### Option A: Manual (Right Now)
```bash
# In your terminal, run:
twine upload dist/*

# When prompted:
# Username: __token__
# Password: (paste your PyPI token)
```

### Option B: Automated (Use GitHub)
```bash
# Create and push a version tag:
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"
git push origin v0.1.0

# GitHub Actions will automatically publish to PyPI
# Watch progress at: https://github.com/1divyanshdev/production-rag/actions
```

---

## Future Releases (Example: v0.2.0)

1. **Update version** in `pyproject.toml`
2. **Commit and push** changes
3. **Create tag**:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```
4. **Done!** GitHub Actions publishes automatically

---

## Verify Publication

```bash
# Check PyPI
open https://pypi.org/project/production-rag/

# Test installation
pip install production-rag

# Test import
python -c "from rag_core import RAGPipeline; print('Success!')"
```

---

## Need Help?
See full guide: `docs/PUBLISHING.md`
