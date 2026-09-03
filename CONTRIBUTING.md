# Contributing to ROMA Fork

## 🙏 Thank You!

We appreciate your interest in contributing to this enhanced fork of ROMA. This document provides guidelines and instructions for contributing.

---

## 📖 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Submitting Changes](#submitting-changes)
8. [Pull Request Process](#pull-request-process)
9. [Reporting Bugs](#reporting-bugs)
10. [Security](#security)

---

## 💻 Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Assume good intentions
- Report violations to maintainers

---

## 🤝 How to Contribute

### Types of Contributions

1. **Bug Reports** - Found an issue? Report it!
2. **Feature Requests** - Have an idea? Share it!
3. **Code Contributions** - Fix bugs or add features
4. **Documentation** - Improve guides and examples
5. **Examples** - Add use cases and demos
6. **Testing** - Improve test coverage
7. **Performance** - Optimize and benchmark

### Good First Issues

Looking for where to start? Check issues labeled:
- `good-first-issue`
- `help-wanted`
- `documentation`

---

## 🔧 Development Setup

### Prerequisites

- Python 3.12+
- Git
- UV package manager
- Docker (for full testing)

### Fork & Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR-USERNAME/ROMA.git
cd ROMA

# Add upstream remote
git remote add upstream https://github.com/sentient-agi/ROMA.git
```

### Setup Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_agents.py::test_atomizer
```

---

## 📝 Coding Standards

### Python Style

- **Format:** Black
  ```bash
  black src/ tests/
  ```

- **Lint:** Ruff
  ```bash
  ruff check src/ tests/
  ```

- **Type Hints:** Required for all public APIs
  ```python
  def process_task(task: TaskNode) -> Result:
      """Process a task node and return result."""
      pass
  ```

- **Docstrings:** Google style
  ```python
  def create_agent(name: str, config: Dict) -> Agent:
      """Create a new agent with given configuration.
      
      Args:
          name: Name of the agent
          config: Configuration dictionary
          
      Returns:
          Initialized Agent instance
          
      Raises:
          ValueError: If name is empty
      """
      pass
  ```

### Commit Messages

Follow Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (no functional change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test additions/changes
- `chore`: Maintenance

**Example:**
```
feat(agents): Add circuit breaker pattern to executor

Implement automatic retry with exponential backoff for failed agent calls.
Includes configurable thresholds and recovery mechanisms.

Fixes #123
```

---

## ✅ Testing

### Test Requirements

- New features must include tests
- Bug fixes must include regression tests
- Minimum 80% code coverage
- All tests must pass locally

### Test Structure

```
tests/
├── unit/
│   ├── test_agents.py
│   ├── test_graph.py
│   └── test_context.py
├── integration/
│   ├── test_end_to_end.py
│   └── test_workflows.py
└── fixtures/
    └── conftest.py
```

### Writing Tests

```python
import pytest
from src.sentientresearchagent.agents import Atomizer

def test_atomizer_identifies_simple_task():
    """Test atomizer correctly identifies atomic tasks."""
    atomizer = Atomizer()
    result = atomizer.evaluate("Search for Python documentation")
    assert result.is_atomic == True

@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent execution with async tasks."""
    agent = create_test_agent()
    result = await agent.execute("test task")
    assert result.status == "completed"
```

---

## 📚 Documentation

### Documentation Requirements

- README section for new features
- Docstrings for all public functions
- Architecture Decision Records (ADRs) for major changes
- Examples in `/docs/examples/`

### Adding Documentation

1. **Update README.md** for user-facing features
2. **Add docstring** to functions/classes
3. **Create ADR** for architectural decisions
4. **Add example** in `/docs/examples/`

---

## 🔄 Submitting Changes

### Step 1: Create Feature Branch

```bash
# Always sync with upstream first
git fetch upstream main
git rebase upstream/main

# Create feature branch
git checkout -b feature/my-feature
```

### Step 2: Make Changes

```bash
# Make your changes
# Test thoroughly
pytest tests/
black src/
ruff check src/
```

### Step 3: Commit Changes

```bash
# Commit with conventional format
git commit -m "feat(agents): Add new feature

Detailed description of changes."
```

### Step 4: Push & Create PR

```bash
git push origin feature/my-feature
# Go to GitHub and create Pull Request
```

---

## 📋 Pull Request Process

### PR Title Format

```
[FORK] feat(agents): Add circuit breaker pattern
[UPSTREAM] fix(graph): Resolve deadlock issue
[DOCS] docs: Update architecture guide
```

### PR Description Template

```markdown
## Description
Brief description of changes.

## Motivation & Context
Why these changes? What problem do they solve?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Added tests
- [ ] All tests passing
- [ ] Tested locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings generated

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**
   - Tests pass ✅
   - Coverage maintained ✅
   - Linting passes ✅

2. **Code Review**
   - 1+ maintainer approval required
   - Address feedback
   - Request re-review if needed

3. **Merge**
   - Squash commits (if requested)
   - Delete branch
   - Close related issues

---

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen?

## Actual Behavior
What actually happened?

## Environment
- Python version: 3.12
- OS: Ubuntu 22.04
- Dependencies versions (if relevant)

## Logs/Errors
```
Error message here
```

## Possible Solution (optional)
```

---

## 🔒 Security

**Do NOT open public issues for security vulnerabilities!**

See SECURITY.md for reporting procedures.

---

## ❓ Questions?

- 📖 Check Documentation
- 💬 Open a Discussion
- 🐛 Search existing Issues
- 📧 Contact maintainers

---

## 🎉 Thank You!

Your contributions make ROMA better for everyone!