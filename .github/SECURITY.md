# Security Policy

## Overview

We take the security of ROMA (Recursive-Open-Meta-Agent) seriously. This document describes our security policies and procedures, as well as how to report security vulnerabilities.

## Supported Versions

| Version | Status | Security Updates |
|---------|--------|-----------------|
| 0.1 (Beta) | Active | ✅ Full support |

## Reporting Security Vulnerabilities

**Please do not open public GitHub issues for security vulnerabilities.** 

Instead, please report security issues by:

1. **Private Security Advisory**: Use GitHub's [private reporting feature](https://github.com/saskw2010/ROMA/security/advisories)
2. **Email**: Contact the maintainer directly (check repository profile for contact info)

### What to Include

When reporting a security vulnerability, please provide:

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if you have one)
- Your name and contact information

## Security Features

### Automated Dependency Scanning

- **Dependabot**: Weekly automated checks for vulnerable dependencies
- **npm audit**: Integrated into CI/CD pipeline
- **GitHub CodeQL**: Continuous code analysis for security vulnerabilities

### Continuous Integration

All pull requests undergo:
- Dependency vulnerability scanning
- Code quality checks
- Security analysis with CodeQL

### Dependencies

We actively monitor and update:
- Direct dependencies in `frontend/package.json`
- GitHub Actions workflows
- Development dependencies

## Security Best Practices

### For Contributors

1. **Keep dependencies updated**: Respond promptly to Dependabot PRs
2. **Review security advisories**: Check GitHub security alerts regularly
3. **Report vulnerabilities responsibly**: Use private disclosure methods
4. **Avoid hardcoding secrets**: Never commit API keys, tokens, or credentials

### For Users

1. **Keep ROMA updated**: Always use the latest version
2. **Review dependencies**: Understand the packages you're using
3. **Report vulnerabilities**: Help us improve security by reporting issues
4. **Use environment variables**: Never hardcode sensitive information

## Security Scanning

### npm audit

```bash
cd frontend
npm audit
npm audit fix  # Auto-fix vulnerabilities (use with caution)
npm audit fix --force  # Force updates (may break compatibility)
```

### Manual Security Review

```bash
# Check outdated packages
npm outdated

# Update packages safely
npm update
npm upgrade
```

## Vulnerability Response Process

1. **Triage**: We assess the severity and impact
2. **Prioritize**: Critical vulnerabilities get immediate attention
3. **Fix**: We develop and test fixes
4. **Release**: Updates are released as soon as possible
5. **Notify**: Users are informed through releases and advisories

## Severity Levels

- **Critical**: Immediate exploitation risk, data breach potential
- **High**: Could enable unauthorized access or data loss
- **Moderate**: Potential security issue requiring attention
- **Low**: Minor security concern with low likelihood of exploitation

## Acknowledgments

We appreciate the security research community and responsible disclosure. Researchers who report vulnerabilities may be acknowledged in our security releases (with permission).

## Related Documentation

- [GitHub Security Advisory Documentation](https://docs.github.com/en/code-security)
- [npm Security Documentation](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Questions?

If you have questions about security in ROMA, please open a [GitHub Discussion](https://github.com/saskw2010/ROMA/discussions) or contact the maintainer.

---

**Last Updated**: 2026-09-02
**Status**: Active
