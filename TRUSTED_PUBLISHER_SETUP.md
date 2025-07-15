# PyPI Trusted Publisher Setup Guide

This guide walks you through setting up PyPI trusted publishing for automatic releases when creating GitHub tags/releases.

## What is Trusted Publishing?

Trusted publishing uses OpenID Connect (OIDC) to securely authenticate GitHub Actions to PyPI without requiring API tokens. This is the recommended modern approach for automated publishing.

## Setup Steps

### 1. Configure PyPI Trusted Publisher

1. **Go to PyPI**: Visit [pypi.org](https://pypi.org) and log in to your account
2. **Navigate to your project**: Go to your `ssh-tools-suite` project page
3. **Go to Publishing settings**: 
   - Click "Manage" on your project
   - Click "Publishing" in the left sidebar
4. **Add Trusted Publisher**:
   - Click "Add a new publisher"
   - Select "GitHub Actions"
   - Fill in the details:
     - **Owner**: `NicholasKozma` (your GitHub username)
     - **Repository name**: `ssh_tools_suite`
     - **Workflow name**: `publish-pypi.yml`
     - **Environment name**: `release` (important!)

### 2. Create GitHub Environment (Required)

1. **Go to your GitHub repository**: `https://github.com/NicholasKozma/ssh_tools_suite`
2. **Go to Settings**: Click the "Settings" tab
3. **Navigate to Environments**: Click "Environments" in the left sidebar
4. **Create new environment**:
   - Click "New environment"
   - Name it: `release`
   - **Optional**: Add protection rules (e.g., require manual approval for releases)

### 3. Current Workflow Configuration

The workflow is already configured in `.github/workflows/publish-pypi.yml` with:

- ✅ `environment: release` - Matches the PyPI trusted publisher config
- ✅ `permissions.id-token: write` - Required for OIDC authentication
- ✅ Uses `pypa/gh-action-pypi-publish@release/v1` - The official trusted publishing action
- ✅ Automatic version extraction from Git tags
- ✅ Updates all version references in the codebase

## How to Release

### Option 1: Create a GitHub Release (Recommended)

1. **Go to Releases**: In your GitHub repo, click "Releases"
2. **Create new release**: Click "Create a new release"
3. **Choose tag**: Create a new tag like `v1.0.1`
4. **Fill release info**:
   - Release title: `v1.0.1`
   - Description: Add changelog/release notes
5. **Publish release**: Click "Publish release"

The workflow will automatically:
- Extract version `1.0.1` from the tag `v1.0.1`
- Update all version references in your code
- Build the package
- Publish to PyPI

### Option 2: Create a Git Tag

```bash
# Create and push a new tag
git tag v1.0.1
git push origin v1.0.1

# Then create a release from the tag on GitHub
```

### Option 3: Manual Trigger

You can also manually trigger the workflow from the GitHub Actions tab if needed.

## Troubleshooting

### Common Issues

1. **"Publisher not configured"**: Make sure the PyPI trusted publisher is set up with exactly matching details
2. **"Environment not found"**: Ensure you created the `release` environment in GitHub
3. **"Permission denied"**: Check that `id-token: write` permission is set
4. **"Workflow not found"**: Ensure the workflow file is named exactly `publish-pypi.yml`

### Verification

- Check the Actions tab to see workflow runs
- Look for the OIDC token exchange logs
- Verify the package appears on PyPI after successful run

## Benefits

- 🔒 **More secure**: No API tokens to manage or rotate
- 🚀 **Automatic**: Just create a tag/release and publishing happens automatically
- 📝 **Traceable**: Full audit trail of what was published when
- 🔄 **Version sync**: Automatically updates all version references in your codebase
- 🏗️ **Consistent**: Same build environment every time

## Next Steps

1. Set up the PyPI trusted publisher (step 1 above)
2. Create the GitHub `release` environment (step 2 above)
3. Test with a new tag like `v1.0.1`
4. Monitor the GitHub Actions run to ensure it works

Once set up, future releases are as simple as creating a new GitHub release!
