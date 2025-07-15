# Contributing to genai-processors-pydantic

Thank you for your interest in contributing to genai-processors-pydantic! This document provides guidelines and information for contributors.

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Git

### Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/mbeacom/genai-processors-pydantic.git
   cd genai-processors-pydantic
   ```

2. **Install dependencies with uv**:

   ```bash
   uv sync --dev
   ```

3. **Install pre-commit hooks**:

   ```bash
   uv run pre-commit install
   ```

4. **Verify setup by running tests**:

   ```bash
   uv run pytest
   ```

## 🔧 Development Tools

### Package Management: uv

We use [uv](https://docs.astral.sh/uv/) as our package manager for its speed and reliability:

- **Install dependencies**: `uv sync`
- **Add new dependency**: `uv add package-name`
- **Add dev dependency**: `uv add --dev package-name`
- **Run commands**: `uv run command`
- **Build package**: `uv build`

### Code Quality: Pre-commit

Pre-commit hooks run automatically before each commit to ensure code quality:

- **Manual run**: `uv run pre-commit run --all-files`
- **Update hooks**: `uv run pre-commit autoupdate`

Our pre-commit configuration includes:

- **Ruff**: Fast Python linter and formatter (autofix enabled)
- **Black**: Code formatting
- **Bandit**: Security vulnerability scanning
- **Standard hooks**: trailing whitespace, merge conflicts, JSON/YAML validation

> **Note**: Markdown linting is handled separately due to Ruby version dependencies.

### Testing: pytest

- **Run all tests**: `uv run pytest`
- **Run with verbose output**: `uv run pytest -v`
- **Run specific test**: `uv run pytest genai_processors_pydantic/tests/test_validator.py::TestPydanticValidator::test_successful_validation`
- **Run with coverage**: `uv run pytest --cov=genai_processors_pydantic`

### Code Formatting and Linting

#### Ruff (Primary Linter/Formatter)

Ruff handles most linting and some formatting:

- **Lint**: `uv run ruff check`
- **Lint with autofix**: `uv run ruff check --fix`
- **Format**: `uv run ruff format`

#### Black (Code Formatting)

Black ensures consistent code formatting:

- **Format**: `uv run black .`
- **Check formatting**: `uv run black --check .`

#### Bandit (Security Scanning)

Bandit scans for security vulnerabilities:

- **Scan**: `uv run bandit -c pyproject.toml -r genai_processors_pydantic/`

> **Note**: We use both Ruff and Bandit because Ruff currently supports only a subset of Bandit's security checks. As Ruff's security coverage improves, we may transition fully to Ruff.

## 🚀 CI/CD Pipeline

### GitHub Actions

Our CI/CD pipeline automatically:

1. **On Pull Requests**:
   - Runs all tests across Python 3.11, 3.12, and 3.13
   - Validates code formatting and linting
   - Runs security scans
   - Checks package builds successfully

2. **On Tag/Release** (coming soon):
   - Automatically publishes to PyPI
   - Creates GitHub releases with changelog

### Local Testing

Before submitting a PR, ensure your changes pass all checks:

```bash
# Run pre-commit checks
uv run pre-commit run --all-files

# Run full test suite
uv run pytest -v

# Verify package builds
uv build

# Check security
uv run bandit -c pyproject.toml -r genai_processors_pydantic/
```

## 📝 Contributing Guidelines

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for all function signatures
- Write comprehensive docstrings for public APIs
- Keep line length under 88 characters (Black default)

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases

### Documentation

- Update README.md for user-facing changes
- Update MAINTAINER_FEEDBACK.md for architectural decisions
- Include docstrings for all public functions and classes
- Add examples for new features

### Commit Messages

Use conventional commit format:

- `feat: add new validation feature`
- `fix: resolve serialization issue`
- `docs: update API documentation`
- `test: add missing test cases`
- `refactor: improve error handling`

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: Python version, OS, package version
2. **Reproduction**: Minimal code example that reproduces the issue
3. **Expected vs Actual**: What you expected to happen vs what actually happened
4. **Error messages**: Full stack traces if applicable

Use the issue template when available.

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and why it's valuable
3. **Propose implementation** if you have ideas
4. **Consider breaking changes** and backward compatibility

See [MAINTAINER_FEEDBACK.md](MAINTAINER_FEEDBACK.md) for our current roadmap and known limitations.

## 🔄 Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the guidelines above
3. **Write tests** for any new functionality
4. **Update documentation** as needed
5. **Run all checks** locally before submitting
6. **Submit pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Test coverage information

### PR Checklist

- [ ] Tests pass locally (`uv run pytest`)
- [ ] Code follows style guidelines (`uv run pre-commit run --all-files`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] Breaking changes documented in MAINTAINER_FEEDBACK.md

## 🏗️ Project Structure

```zsh
genai-processors-pydantic/
├── genai_processors_pydantic/     # Main package
│   ├── __init__.py               # Package exports
│   ├── validator.py              # Core PydanticValidator
│   └── tests/                    # Test suite
├── examples/                     # Usage examples
├── docs/                         # Documentation
├── .github/                      # GitHub Actions workflows
├── pyproject.toml               # Project configuration
├── README.md                    # User documentation
├── MAINTAINER_FEEDBACK.md       # Technical roadmap
└── CONTRIBUTING.md              # This file
```

## 📦 Release Process

Releases are automated via GitHub Actions:

1. **Create a tag**: `git tag v0.1.0`
2. **Push tag**: `git push origin v0.1.0`
3. **GitHub Actions** automatically:
   - Builds the package
   - Runs full test suite
   - Publishes to PyPI
   - Creates GitHub release

For maintainers only.

## 🤝 Community

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Pull Requests**: All contributions welcome!

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

---

Thank you for contributing to genai-processors-pydantic! 🎉
