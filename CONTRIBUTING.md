# Contributing to Video RAG Engine

Thank you for your interest in contributing! Here's how you can help:

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/video-rag-engine.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dev dependencies: `pip install -r requirements-dev.txt`

## Development Setup

```bash
# Install all dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run setup script
python scripts/setup.py

# Download AI models
python scripts/download_models.py
```

## Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black src/ main.py scripts/ examples/

# Check style
flake8 src/ main.py scripts/ examples/

# Type check
mypy src/
```

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_pipeline.py::test_process
```

## Making Changes

1. Create a feature branch with a descriptive name
2. Make your changes
3. Add tests for new functionality
4. Update documentation
5. Ensure all tests pass

## Commit Messages

Use clear, descriptive commit messages:
```
fix: correct scene detection threshold handling
feat: add GPU acceleration support
docs: update configuration guide
```

## Pull Request Process

1. Update the README.md with any new features
2. Ensure tests pass and coverage is maintained
3. Update CHANGELOG.md
4. Link any related issues
5. Request review from maintainers

## Areas for Contribution

### High Priority
- [ ] GPU acceleration improvements
- [ ] Real-time processing pipeline
- [ ] Web UI for scene browser
- [ ] Cloud storage integration

### Medium Priority
- [ ] Multi-format output support (MOV, ProRes)
- [ ] Webhook support for automation
- [ ] Database optimization
- [ ] Performance profiling tools

### Low Priority
- [ ] Additional example scripts
- [ ] Documentation improvements
- [ ] Unit test expansion
- [ ] Configuration templates

## Questions?

Open an issue or start a discussion in the repository.

Thank you! 🎉
