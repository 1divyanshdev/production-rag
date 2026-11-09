# Publishing to PyPI

This guide covers how to publish `production-rag` to PyPI, both manually and automatically via GitHub Actions.

## Prerequisites

1. **PyPI Account**: Create one at https://pypi.org/account/register/
2. **API Token**: Generate at https://pypi.org/manage/account/token/
   - Scope: "Entire account" (or project-specific after first upload)
   - Save the token securely (starts with `pypi-`)

## Method 1: Manual Publishing (First Time)

### Step 1: Install Publishing Tools
```bash
pip install build twine
```

### Step 2: Build the Package
```bash
python -m build
```

This creates:
- `dist/production_rag-X.X.X.tar.gz` (source distribution)
- `dist/production_rag-X.X.X-py3-none-any.whl` (wheel)

### Step 3: Upload to PyPI
```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: `pypi-AgEIcHlwaS5vcmc...` (your full API token)

### Step 4: Verify Upload
Visit: https://pypi.org/project/production-rag/

Test installation:
```bash
pip install production-rag
```

## Method 2: Automated Publishing via GitHub Actions

### Setup (One-Time)

1. **Add PyPI Token to GitHub Secrets**:
   - Go to: https://github.com/1divyanshdev/production-rag/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (entire token including `pypi-` prefix)
   - Click "Add secret"

2. **Push the Workflow** (already created at `.github/workflows/publish.yml`):
   ```bash
   git add .github/workflows/publish.yml
   git commit -m "Add automated PyPI publishing workflow"
   git push origin main
   ```

### Publishing a New Release

1. **Update Version** in `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"  # Increment version
   ```

2. **Commit Changes**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push origin main
   ```

3. **Create and Push Git Tag**:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

4. **GitHub Actions Automatically**:
   - Builds the package
   - Uploads to PyPI
   - View progress at: https://github.com/1divyanshdev/production-rag/actions

### Creating GitHub Release (Optional but Recommended)

After tagging, create a release on GitHub:
1. Go to: https://github.com/1divyanshdev/production-rag/releases/new
2. Select the tag you just created
3. Add release notes (changes, fixes, new features)
4. Click "Publish release"

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `0.1.0` → Initial release
- `0.1.1` → Bug fix
- `0.2.0` → New feature added
- `1.0.0` → Production-ready, stable API

## Troubleshooting

### "File already exists" Error
PyPI doesn't allow re-uploading the same version. Solutions:
- Delete `dist/` folder
- Increment version in `pyproject.toml`
- Rebuild: `python -m build`
- Upload new version

### "Invalid or non-existent authentication"
- Verify token is correct
- Check token hasn't expired
- Ensure username is `__token__` (not your PyPI username)

### "403 Forbidden"
- Project name already taken (highly unlikely for "production-rag")
- Token doesn't have upload permissions
- Re-generate token with correct scope

## Post-Publishing Checklist

- [ ] Verify package appears at https://pypi.org/project/production-rag/
- [ ] Test installation: `pip install production-rag`
- [ ] Test import: `python -c "from rag_core import RAGPipeline"`
- [ ] Update README with installation badge
- [ ] Create GitHub release with changelog
- [ ] Announce on social media / community forums

## Resources

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/
- GitHub Actions: https://docs.github.com/en/actions
