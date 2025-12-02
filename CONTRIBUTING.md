# Contributing to MembrrHub

Thank you for your interest in contributing to MembrrHub!

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/membrhub.git
   cd membrhub
   ```

2. **Install dependencies**

   ```bash
   poetry install
   ```

3. **Install pre-commit hooks**

   ```bash
   poetry run pre-commit install
   ```

4. **Copy environment file**

   ```bash
   cp .env.example .env
   ```

5. **Start the database**

   ```bash
   just up
   ```

6. **Run migrations**

   ```bash
   just migrate
   ```

7. **Start the development server**

   ```bash
   just run
   ```

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automatic versioning and changelog generation.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | A new feature | Minor |
| `fix` | A bug fix | Patch |
| `perf` | Performance improvement | Patch |
| `docs` | Documentation only | None |
| `style` | Code style (formatting, semicolons, etc.) | None |
| `refactor` | Code refactoring (no feature/fix) | None |
| `test` | Adding or updating tests | None |
| `build` | Build system or dependencies | None |
| `ci` | CI/CD configuration | None |
| `chore` | Other changes (not affecting src/test) | None |
| `revert` | Reverting a previous commit | Depends |

### Scopes (Optional)

Use the module name as scope:

- `auth` - Authentication module
- `users` - User management
- `communities` - Community management
- `membership` - Membership management
- `committees` - Committee management
- `funds` - Fund management
- `content` - Blog/content management
- `newsletters` - Newsletter management
- `websites` - Website hosting
- `api` - API general changes
- `db` - Database changes
- `deps` - Dependencies

### Examples

```bash
# Feature (bumps minor version: 0.1.0 → 0.2.0)
feat(auth): add JWT refresh token rotation

# Bug fix (bumps patch version: 0.1.0 → 0.1.1)
fix(users): prevent duplicate email registration

# Performance (bumps patch version)
perf(db): add index for community member lookup

# Breaking change (bumps major version: 0.1.0 → 1.0.0)
feat(api)!: change authentication endpoint structure

BREAKING CHANGE: The /auth/login endpoint now returns tokens in a different format.

# Documentation (no version bump)
docs(readme): update installation instructions

# Multiple scopes
feat(auth,users): implement SSO login flow
```

### Breaking Changes

For breaking changes, either:

1. Add `!` after the type/scope:

   ```
   feat(api)!: remove deprecated endpoints
   ```

2. Or add a `BREAKING CHANGE:` footer:

   ```
   feat(api): restructure response format

   BREAKING CHANGE: All API responses now use a standardized envelope format.
   ```

## Code Quality

Before submitting a PR, ensure:

1. **All checks pass**

   ```bash
   just check-all
   ```

2. **Tests pass**

   ```bash
   just test
   ```

3. **Pre-commit hooks pass**

   ```bash
   just pre-commit
   ```

## Pull Request Process

1. Create a feature branch from `develop`:

   ```bash
   git checkout -b feat/my-feature develop
   ```

2. Make your changes with conventional commits

3. Push and create a PR to `develop`

4. After review and approval, the PR will be merged

5. When `develop` is merged to `main`, semantic release will:
   - Determine version bump based on commits
   - Update `pyproject.toml` version
   - Generate/update `CHANGELOG.md`
   - Create a Git tag
   - Create a GitHub release
   - Trigger Docker image build

## Questions?

Feel free to open an issue for any questions or concerns.
