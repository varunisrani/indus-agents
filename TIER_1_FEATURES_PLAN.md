# Tier 1 Features Plan - indus-agents
## Priority Implementation Roadmap

**Last Updated**: November 2025
**Status**: Planning Phase
**Target**: Core Production-Ready Framework

---

## 📊 Current Status Analysis

### ✅ **Implemented (Core Foundation)**
- [x] Basic Agent class with LLM integration (agent.py)
- [x] Tool system with registry (tools.py)
- [x] Memory management system (memory.py)
- [x] Multi-agent orchestration (orchestrator.py)
- [x] CLI interface (cli.py)
- [x] Project structure and packaging (pyproject.toml)
- [x] Comprehensive documentation

### ❌ **Missing from Roadmap (README.md:288-303)**
- [ ] OpenAI function calling integration
- [ ] Anthropic Claude integration
- [ ] Memory management system (persistence)
- [ ] Multi-agent coordination (advanced)
- [ ] Plugin system
- [ ] Web interface
- [ ] Documentation site
- [ ] Advanced tool library
- [ ] Streaming responses
- [ ] Token usage tracking
- [ ] Agent templates

---

## 🎯 Tier 1 Features (Must-Have for Production)

**Goal**: Create a stable, reliable, production-ready agent framework with essential features.

**Timeline**: 2-3 weeks
**Priority**: HIGH - Block all other development

---

### **Feature 1.1: Robust API Integration**
**Status**: ⚠️ Partially Complete
**Priority**: CRITICAL
**Estimated Time**: 3-4 days

#### Current State:
- OpenAI integration exists but needs testing
- Anthropic integration missing
- No fallback/retry logic
- No error handling for rate limits

#### Required Implementation:

```python
# Target Architecture
class LLMProvider(ABC):
    """Abstract base for all LLM providers"""

    @abstractmethod
    async def complete(self, messages: List[dict]) -> str:
        pass

    @abstractmethod
    async def complete_with_tools(self, messages: List[dict], tools: List[dict]) -> dict:
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4, GPT-3.5 support"""
    # Implements retry logic, rate limiting, error handling
    pass

class AnthropicProvider(LLMProvider):
    """Claude 3.5 Sonnet, Opus support"""
    # Implements retry logic, rate limiting, error handling
    pass
```

#### Tasks:
1. [ ] Refactor agent.py to use provider abstraction
2. [ ] Implement OpenAIProvider with retry logic
3. [ ] Implement AnthropicProvider with proper tool calling
4. [ ] Add exponential backoff for rate limits
5. [ ] Add comprehensive error handling
6. [ ] Write integration tests for both providers
7. [ ] Document provider switching in README

#### Success Criteria:
- ✅ Agent works with both OpenAI and Anthropic
- ✅ Automatic retry on transient failures (3 attempts)
- ✅ Rate limit handling with backoff
- ✅ Clear error messages for API failures
- ✅ 90%+ test coverage on provider code

#### Deliverables:
- `src/my_agent_framework/providers/base.py`
- `src/my_agent_framework/providers/openai.py`
- `src/my_agent_framework/providers/anthropic.py`
- `tests/test_providers.py`
- Updated `agent.py` using providers

---

### **Feature 1.2: Enhanced Tool System**
**Status**: ⚠️ Basic Implementation Exists
**Priority**: HIGH
**Estimated Time**: 4-5 days

#### Current State:
- Basic tool registry exists
- Manual tool definition required
- No validation of tool outputs
- Limited error handling

#### Required Enhancements:

```python
# Target Architecture
from pydantic import BaseModel, Field
from typing import Callable, Optional

class ToolParameter(BaseModel):
    """Type-safe tool parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class Tool(BaseModel):
    """Enhanced tool with validation and error handling"""
    name: str
    description: str
    parameters: List[ToolParameter]
    function: Callable
    timeout: int = 30  # seconds
    retry_on_failure: bool = True

    async def execute(self, **kwargs) -> ToolResult:
        """Execute with validation, timeout, error handling"""
        pass

class ToolResult(BaseModel):
    """Standardized tool output"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float
    metadata: dict = {}
```

#### Tasks:
1. [ ] Create Pydantic models for tools (Tool, ToolParameter, ToolResult)
2. [ ] Add input validation using Pydantic
3. [ ] Add timeout handling for tool execution
4. [ ] Implement tool execution sandboxing (safety)
5. [ ] Create standard library of 10+ common tools:
   - [ ] Calculator (enhanced)
   - [ ] Web search (mock/real with API)
   - [ ] File operations (read/write with safety)
   - [ ] Date/time utilities
   - [ ] Weather API integration
   - [ ] Currency conversion
   - [ ] Unit conversions
   - [ ] JSON parser/validator
   - [ ] URL fetcher
   - [ ] Email sender (mock)
6. [ ] Add tool discovery mechanism
7. [ ] Write comprehensive tests for all tools

#### Success Criteria:
- ✅ Type-safe tool definitions with Pydantic
- ✅ All tool inputs validated automatically
- ✅ Timeout prevents hanging operations
- ✅ At least 10 working tools in standard library
- ✅ Tool errors don't crash the agent
- ✅ 85%+ test coverage

#### Deliverables:
- `src/my_agent_framework/tools/base.py` (updated)
- `src/my_agent_framework/tools/standard_library.py`
- `tests/test_tools_standard_library.py`
- Documentation: `docs/TOOLS.md`

---

### **Feature 1.3: Production-Grade Memory System**
**Status**: ⚠️ Basic Implementation Exists
**Priority**: HIGH
**Estimated Time**: 3-4 days

#### Current State:
- Basic in-memory conversation storage
- No persistence
- No search/retrieval
- No memory management (cleanup)

#### Required Enhancements:

```python
# Target Architecture
class MemoryBackend(ABC):
    """Abstract memory storage"""

    @abstractmethod
    async def save(self, key: str, value: dict) -> None:
        pass

    @abstractmethod
    async def load(self, key: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[dict]:
        pass

class JSONMemoryBackend(MemoryBackend):
    """File-based persistence"""
    pass

class SQLiteMemoryBackend(MemoryBackend):
    """SQLite-based persistence with search"""
    pass

class ConversationMemory:
    """Enhanced memory with persistence and search"""

    def __init__(self, backend: MemoryBackend, max_tokens: int = 4000):
        self.backend = backend
        self.max_tokens = max_tokens

    async def add_message(self, role: str, content: str):
        """Add with automatic token management"""
        pass

    async def get_context(self, last_n: int = 10) -> List[dict]:
        """Retrieve recent context"""
        pass

    async def search_history(self, query: str) -> List[dict]:
        """Semantic search in history"""
        pass
```

#### Tasks:
1. [ ] Create MemoryBackend abstraction
2. [ ] Implement JSONMemoryBackend (file persistence)
3. [ ] Implement SQLiteMemoryBackend (structured storage)
4. [ ] Add token counting and automatic trimming
5. [ ] Add conversation summarization (when context too large)
6. [ ] Add memory search functionality
7. [ ] Add memory export/import (JSON)
8. [ ] Integrate with Agent class
9. [ ] Write comprehensive tests

#### Success Criteria:
- ✅ Memory persists across agent restarts
- ✅ Automatic token limit management
- ✅ Can search conversation history
- ✅ Support for multiple storage backends
- ✅ No data loss on crashes
- ✅ 90%+ test coverage

#### Deliverables:
- `src/my_agent_framework/memory/backends.py`
- `src/my_agent_framework/memory/core.py` (updated)
- `tests/test_memory_persistence.py`
- Documentation: `docs/MEMORY.md`

---

### **Feature 1.4: Enhanced CLI & User Experience**
**Status**: ⚠️ Basic CLI Exists
**Priority**: MEDIUM-HIGH
**Estimated Time**: 2-3 days

#### Current State:
- Basic commands (run, version, interactive)
- Minimal error handling
- No configuration management
- No streaming output

#### Required Enhancements:

```bash
# Target CLI Interface
my-agent init              # Setup project with config wizard
my-agent run "query"       # Run single query
my-agent chat              # Interactive mode (renamed)
my-agent config            # Manage configuration
my-agent tools list        # List available tools
my-agent tools test <name> # Test a specific tool
my-agent memory clear      # Clear conversation history
my-agent memory export     # Export to JSON
my-agent agents list       # List available agents
my-agent --help            # Comprehensive help
```

#### Tasks:
1. [ ] Add `init` command with configuration wizard
2. [ ] Add `config` command for settings management
3. [ ] Enhance `chat` command with:
   - [ ] Streaming output support
   - [ ] Better prompt formatting
   - [ ] Command history
   - [ ] Multi-line input support
4. [ ] Add `tools` subcommands (list, test, add)
5. [ ] Add `memory` subcommands (clear, export, import, search)
6. [ ] Add `agents` subcommands (list, create, switch)
7. [ ] Improve error messages and help text
8. [ ] Add progress indicators for long operations
9. [ ] Add colored output for different message types

#### Success Criteria:
- ✅ Intuitive command structure
- ✅ Excellent help documentation
- ✅ Streaming responses in chat mode
- ✅ Configuration persists between sessions
- ✅ Beautiful, colorful terminal output
- ✅ All commands have examples in help text

#### Deliverables:
- `src/my_agent_framework/cli.py` (updated)
- `src/my_agent_framework/config.py` (new)
- `tests/test_cli_commands.py`
- Documentation: `docs/CLI.md`

---

### **Feature 1.5: Configuration Management**
**Status**: ❌ Not Implemented
**Priority**: MEDIUM-HIGH
**Estimated Time**: 2-3 days

#### Required Implementation:

```python
# Target Architecture
from pydantic_settings import BaseSettings

class AgentFrameworkConfig(BaseSettings):
    """Global configuration with environment and file support"""

    # API Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_provider: str = "anthropic"
    default_model: str = "claude-3-5-sonnet-20241022"

    # Agent Configuration
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 60

    # Memory Configuration
    memory_backend: str = "json"  # json, sqlite, memory
    memory_path: str = "~/.my-agent/memory"
    max_conversation_tokens: int = 4000

    # Tool Configuration
    enable_dangerous_tools: bool = False
    tool_timeout: int = 30

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "~/.my-agent/agent.log"

    class Config:
        env_prefix = "MY_AGENT_"
        env_file = ".env"
        case_sensitive = False

# Load from multiple sources
config = AgentFrameworkConfig(
    _env_file=".env",              # 1. Environment variables
    _env_file_encoding="utf-8",    # 2. .env file
    **load_user_config()           # 3. ~/.my-agent/config.yaml
)
```

#### Tasks:
1. [ ] Create AgentFrameworkConfig with Pydantic Settings
2. [ ] Add support for .env files
3. [ ] Add support for YAML config files (~/.my-agent/config.yaml)
4. [ ] Add configuration wizard in CLI (`my-agent init`)
5. [ ] Add config validation and helpful error messages
6. [ ] Add `my-agent config` commands (show, set, reset)
7. [ ] Document all configuration options

#### Success Criteria:
- ✅ Configuration from multiple sources (env, .env, yaml)
- ✅ Easy setup with wizard
- ✅ Clear configuration priority (env > .env > yaml > defaults)
- ✅ All options documented
- ✅ Validation with helpful errors

#### Deliverables:
- `src/my_agent_framework/config.py`
- `tests/test_config.py`
- Documentation: `docs/CONFIGURATION.md`
- Example configs: `.env.example`, `config.yaml.example`

---

### **Feature 1.6: Testing & Quality Assurance**
**Status**: ⚠️ Partial Test Coverage
**Priority**: HIGH
**Estimated Time**: 3-4 days

#### Current State:
- Some basic tests exist
- No integration tests
- No performance tests
- Test coverage unknown

#### Required Implementation:

#### Tasks:
1. [ ] Achieve 85%+ code coverage
2. [ ] Write unit tests for all core modules:
   - [ ] Agent tests
   - [ ] Tool tests
   - [ ] Memory tests
   - [ ] Orchestrator tests
   - [ ] Provider tests
3. [ ] Write integration tests:
   - [ ] End-to-end agent workflows
   - [ ] Multi-turn conversations
   - [ ] Tool calling flows
   - [ ] Memory persistence
4. [ ] Add performance tests:
   - [ ] Response time benchmarks
   - [ ] Token usage tracking
   - [ ] Memory usage tests
5. [ ] Set up CI/CD with GitHub Actions:
   - [ ] Run tests on push
   - [ ] Check code coverage
   - [ ] Lint with ruff/black
   - [ ] Type check with mypy
6. [ ] Add pre-commit hooks

#### Success Criteria:
- ✅ 85%+ test coverage
- ✅ All core features have tests
- ✅ CI/CD pipeline passing
- ✅ Pre-commit hooks configured
- ✅ Tests run in <30 seconds

#### Deliverables:
- `tests/unit/` (all unit tests)
- `tests/integration/` (integration tests)
- `tests/performance/` (performance benchmarks)
- `.github/workflows/test.yml` (CI/CD)
- `.pre-commit-config.yaml` (updated)
- Coverage report

---

## 📈 Tier 1 Success Metrics

### Required Before Moving to Tier 2:

1. **Functionality**:
   - ✅ Agent works with OpenAI and Anthropic
   - ✅ 10+ tools in standard library
   - ✅ Memory persists across restarts
   - ✅ CLI has all core commands
   - ✅ Configuration system works

2. **Quality**:
   - ✅ 85%+ test coverage
   - ✅ All tests passing
   - ✅ No critical bugs
   - ✅ CI/CD pipeline green

3. **Documentation**:
   - ✅ README updated
   - ✅ API documentation complete
   - ✅ CLI help comprehensive
   - ✅ Configuration documented

4. **User Experience**:
   - ✅ Easy installation (pip install)
   - ✅ Quick start in <5 minutes
   - ✅ Excellent error messages
   - ✅ Beautiful CLI output

---

## 🚀 Implementation Timeline

### Week 1: Core Infrastructure
- **Day 1-2**: Feature 1.1 - API Providers
- **Day 3-4**: Feature 1.2 - Tool System (Part 1)
- **Day 5**: Feature 1.2 - Tool System (Part 2)

### Week 2: User Experience
- **Day 1-2**: Feature 1.3 - Memory System
- **Day 3**: Feature 1.4 - CLI Enhancements
- **Day 4-5**: Feature 1.5 - Configuration Management

### Week 3: Quality & Polish
- **Day 1-3**: Feature 1.6 - Testing & QA
- **Day 4**: Documentation update
- **Day 5**: Bug fixes and polish

---

## 🎯 Next Steps

1. **Review this plan** with the team
2. **Set up project tracking** (GitHub Projects or similar)
3. **Assign features** to developers
4. **Start with Feature 1.1** (API Providers) - highest priority
5. **Daily standups** to track progress
6. **Weekly demos** of completed features

---

## 📝 Notes

- All features are **independent** and can be worked on in parallel
- Each feature has **clear deliverables** and **success criteria**
- Focus on **production quality** - this is Tier 1, must be rock solid
- **Test everything** - quality is not negotiable
- **Document as you go** - don't leave it for the end

---

**Ready to start? See TIER_2_FEATURES_PLAN.md for the next phase after Tier 1 is complete.**
