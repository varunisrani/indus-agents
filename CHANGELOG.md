# Changelog

All notable changes to indus-agents will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- OpenAI function calling integration
- Anthropic Claude integration
- Memory management system
- Multi-agent coordination
- Plugin system
- Web interface
- Streaming responses
- Token usage tracking

## [0.1.0] - 2025-01-XX

### Added

- Initial release of indus-agents
- Core agent implementation with `Agent` and `BaseAgent` classes
- Agent configuration system with `AgentConfig` model
- Tool system foundation with `BaseTool`, `ToolConfig`, and `ToolResult`
- Async-first architecture for all agent operations
- Command-line interface with Typer and Rich
- Configuration management with environment variables and `.env` support
- Logging utilities with customizable log levels
- Comprehensive project structure with modular design
- Type-safe implementation using Pydantic models
- Full package configuration with `pyproject.toml`
- Development tools integration:
  - pytest for testing
  - pytest-asyncio for async test support
  - pytest-cov for coverage reporting
  - black for code formatting
  - ruff for linting
  - mypy for type checking
  - pre-commit for git hooks
- CLI commands:
  - `my-agent version` - Display version information
  - `my-agent run` - Run agent with a prompt
  - `my-agent config` - Manage configuration
- Complete documentation:
  - README with installation and usage instructions
  - CONTRIBUTING guidelines
  - DEPLOYMENT guide
  - Code examples
- MIT License
- Python 3.9+ support

### Project Structure

- `src/my_agent_framework/` - Main package
  - `agent/` - Agent implementations
  - `core/` - Core functionality
  - `tools/` - Tool system
  - `utils/` - Utility functions
- `tests/` - Test suite
- `examples/` - Example scripts
- `docs/` - Documentation

### Dependencies

- openai >= 1.0.0 - OpenAI API client
- typer >= 0.9.0 - CLI framework
- rich >= 13.0.0 - Terminal formatting
- pydantic >= 2.0.0 - Data validation
- pydantic-settings >= 2.0.0 - Settings management
- python-dotenv >= 1.0.0 - Environment variable loading
- httpx >= 0.25.0 - HTTP client

### Development

- Set up modern Python packaging with Hatchling
- Configured code quality tools (black, ruff, mypy)
- Added comprehensive test infrastructure
- Created development workflow documentation
- Added pre-commit hooks configuration

## Version History

### Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

### Release Process

1. Update version in `pyproject.toml`
2. Update version in `src/my_agent_framework/__init__.py`
3. Update this CHANGELOG with release date
4. Create a git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
5. Push tag: `git push origin v0.1.0`
6. Build and publish to PyPI (see DEPLOYMENT.md)

## Links

- [Repository](https://github.com/yourusername/my-agent-framework)
- [Issue Tracker](https://github.com/yourusername/my-agent-framework/issues)
- [Documentation](https://github.com/yourusername/my-agent-framework#readme)

---

**Note**: For detailed upgrade instructions between versions, see the [Migration Guide](docs/MIGRATION.md).
