# Cursor Guardrails

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive validation and standardization system for development environments, ensuring consistent code quality, security, and best practices across projects.

> **Note**: This repository serves as a collection of examples and best practices that have worked in my development environment. While these rules and validations have proven effective in my workflow, they should be adapted and customized to fit your specific needs and development practices. Feel free to use, modify, or ignore any parts that don't align with your requirements.

> **Important**: While these guardrails help maintain consistency, it's crucial to understand that Cursor is an AI assistant that may need frequent reminders about rules and procedures. The checklists and validation rules serve as a structured way to keep Cursor focused and on track with the intended development goals. Think of them as a "conversation guide" that helps maintain consistency in development practices.

> **Disclaimer**: I am not an expert in all aspects of development, and this repository is a living document of what has worked for me in my journey. I am constantly learning and updating these rules as I discover better practices or encounter new challenges. The rules in the `rules/` directory are regularly updated and revised based on my experiences and feedback. While I strive to maintain high standards, these rules should be viewed as a starting point rather than definitive guidelines. Your expertise and specific needs may lead you to different, equally valid approaches.

## Table of Contents
- [Overview](#overview)
- [Preplanning and Requirements](#preplanning-and-requirements)
- [Project Structure](#project-structure)
- [Git Hooks](#git-hooks)
- [Validation Rules](#validation-rules)
- [Validation Scripts](#validation-scripts)
- [Usage](#usage)
- [Bypassing Validations](#bypassing-validations)
- [Contributing](#contributing)
- [Cursor Maintenance and Troubleshooting](#cursor-maintenance-and-troubleshooting)
- [FAQ](#faq)
- [Version History](#version-history)
- [License](#license)

## Overview

Cursor Guardrails is a collection of validation rules, scripts, and Git hooks designed to enforce development standards and best practices. It helps maintain code quality, security, and consistency across projects by implementing automated checks and validations.

### Key Features
- Automated pre-push validation
- Comprehensive code quality checks
- Security standards enforcement
- Performance optimization guidelines
- Development environment standardization
- Customizable validation rules
- Integration with CI/CD pipelines

### Prerequisites
- Python 3.8 or higher
- Git
- Docker (for container validation)
- Poetry (for dependency management)

## Preplanning and Requirements

Before implementing any feature, it's crucial to follow a structured approach that combines our validation rules with detailed requirements planning. This ensures that all development work meets our standards from the outset.

### Requirements Planning Process

1. **Feature Analysis**
   - Define the feature's purpose and scope
   - Identify user stories and acceptance criteria
   - Document technical requirements
   - List dependencies and integrations

2. **Validation Checklist**
   - Review applicable validation rules
   - Create a checklist of required validations
   - Identify potential security considerations
   - Plan for testing requirements

3. **Implementation Planning**
   - Break down into manageable tasks
   - Define API contracts if applicable
   - Plan database schema changes
   - Consider performance implications

### Example: Calculator App Requirements

Here's an example of how to structure requirements for a simple Calculator application:

#### 1. Feature Requirements

**Basic Operations**
- [ ] Addition of two numbers
- [ ] Subtraction of two numbers
- [ ] Multiplication of two numbers
- [ ] Division of two numbers (with zero division handling)
- [ ] Support for decimal numbers
- [ ] Clear function to reset calculator

**Advanced Features**
- [ ] Memory functions (M+, M-, MR, MC)
- [ ] Percentage calculations
- [ ] Square root function
- [ ] Power/exponentiation

#### 2. Technical Requirements

**API Design**
- [ ] RESTful endpoints for each operation
- [ ] Input validation for all parameters
- [ ] Proper error handling and status codes
- [ ] Rate limiting implementation
- [ ] API versioning

**Security**
- [ ] Input sanitization
- [ ] Protection against injection attacks
- [ ] Rate limiting per user/IP
- [ ] Secure error messages
- [ ] Input size limits

**Testing Requirements**
- [ ] Unit tests for all operations
- [ ] Integration tests for API endpoints
- [ ] Edge case testing
- [ ] Performance testing
- [ ] Security testing

**Documentation**
- [ ] API documentation
- [ ] Setup instructions
- [ ] Usage examples
- [ ] Error code documentation
- [ ] Performance considerations

#### 3. Validation Checklist

**Code Standards**
- [ ] Follow PEP 8 style guide
- [ ] Proper function and variable naming
- [ ] Comprehensive docstrings
- [ ] Type hints implementation
- [ ] Code organization

**Testing Standards**
- [ ] Minimum 80% test coverage
- [ ] Test documentation
- [ ] Test organization
- [ ] Mock usage where appropriate
- [ ] Test naming conventions

**Security Standards**
- [ ] Input validation
- [ ] Error handling
- [ ] Logging implementation
- [ ] Security headers
- [ ] CORS configuration

**Performance Standards**
- [ ] Response time < 200ms
- [ ] Memory usage optimization
- [ ] Database query optimization
- [ ] Caching implementation
- [ ] Load testing results

#### 4. Implementation Tasks

1. **Setup Phase**
   - [ ] Project structure setup
   - [ ] Dependencies configuration
   - [ ] Development environment setup
   - [ ] CI/CD pipeline configuration

2. **Core Implementation**
   - [ ] Basic operation functions
   - [ ] API endpoints
   - [ ] Input validation
   - [ ] Error handling
   - [ ] Logging system

3. **Testing Implementation**
   - [ ] Unit test suite
   - [ ] Integration tests
   - [ ] Performance tests
   - [ ] Security tests
   - [ ] Documentation tests

4. **Documentation**
   - [ ] API documentation
   - [ ] Setup guide
   - [ ] Usage examples
   - [ ] Deployment guide
   - [ ] Maintenance guide

## Project Structure

```
.
├── git_hooks/           # Git hooks for pre-push validation
├── rules/              # Markdown files containing validation rules
├── scripts/            # Validation and utility scripts
│   └── validators/     # Specific validation implementations
```

## Git Hooks

### Pre-push Hook

The pre-push hook (`git_hooks/pre-push`) performs the following checks before allowing code to be pushed:

1. **Test Execution**
   - Runs automated tests using `scripts/run_pre_push_tests.sh`
   - Can be bypassed using `SKIP_TESTS=1 git push`
   - Skipped for specific branches (e.g., `chore/standardize-dev-environment`)

2. **Standards Check**
   - Validates code against defined standards using `scripts/check_standards.py`
   - Can be bypassed using `SKIP_STANDARDS=1 git push`
   - Skipped for specific branches

## Validation Rules

The project includes comprehensive rules covering various aspects of development:

### Core Rules Categories

1. **Development Environment**
   - Standardized development environment setup
   - Tool configurations
   - Local development requirements

2. **Code Style & Architecture**
   - Coding standards
   - Architectural patterns
   - File organization

3. **Security**
   - Security best practices
   - Secret management
   - Access controls

4. **Testing**
   - Test coverage requirements
   - Testing methodologies
   - Test organization

5. **API Standards**
   - API design guidelines
   - Documentation requirements
   - Versioning standards

6. **Container Standards**
   - Dockerfile best practices
   - Docker Compose configurations
   - Container security

7. **Documentation**
   - Documentation requirements
   - Code comments
   - API documentation

## Validation Scripts

### Core Validators

1. **Container Validation**
   - `container_validator.py`: Validates container configurations
   - `dockerfile_validator.py`: Checks Dockerfile compliance
   - `compose_validator.py`: Validates Docker Compose files

2. **API Validation**
   - `api_validator.py`: Ensures API compliance with standards

3. **Dependency Management**
   - `poetry_validator.py`: Validates Poetry dependency management

4. **Service Structure**
   - `check_service_structure.py`: Validates service organization
   - `check_standards.py`: General standards compliance

5. **Security**
   - `check_env_secrets.py`: Environment variable security
   - `check_dockerfile.py`: Dockerfile security checks

## Usage

1. **Installation**
   ```bash
   # Clone the repository
   git clone [repository-url]
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Running Validations**
   ```bash
   # Run all validations
   python scripts/validate.py
   
   # Run specific validator
   python scripts/validators/container_validator.py
   ```

3. **Git Hook Setup**
   ```bash
   # Make the pre-push hook executable
   chmod +x git_hooks/pre-push
   
   # Install the hook
   ln -s ../../git_hooks/pre-push .git/hooks/pre-push
   ```

## Bypassing Validations

While validations are important, there are legitimate cases where they might need to be bypassed:

1. **Test Bypass**
   ```bash
   SKIP_TESTS=1 git push
   ```

2. **Standards Bypass**
   ```bash
   SKIP_STANDARDS=1 git push
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run validations
5. Submit a pull request

## Cursor Maintenance and Troubleshooting

### Performance Optimization

If you experience Cursor slowdowns or crashes, you can perform a complete reset of Cursor's configuration and cache. This will help improve performance but will reset your context and preferences.

#### Warning
⚠️ The following commands will:
- Delete all Cursor settings and preferences
- Remove cached data
- Clear application logs
- Reset all custom configurations

#### Reset Commands
```bash
# Remove Cursor application support files
rm -rf ~/Library/Application\ Support/Cursor

# Remove Cursor configuration directory
rm -rf ~/.cursor

# Remove Cursor preferences
rm -rf ~/Library/Preferences/com.cursor.plist

# Clear Cursor cache
rm -rf ~/Library/Caches/Cursor

# Remove Cursor logs
rm -rf ~/Library/Logs/Cursor
```

#### After Reset
1. Restart Cursor
2. Reconfigure your preferences
3. Reinstall any custom extensions
4. Rebuild your workspace context

#### Alternative Solutions
Before performing a complete reset, try these alternatives:
1. Clear individual cache directories
2. Restart Cursor
3. Update to the latest version
4. Check for conflicting extensions

## FAQ

### Common Questions

1. **Q: How do I customize validation rules?**
   A: You can modify the rules in the `rules/` directory and update the corresponding validators in `scripts/validators/`.

2. **Q: What happens if a validation fails?**
   A: The pre-push hook will prevent the push and provide detailed error messages about what needs to be fixed.

3. **Q: Can I add custom validators?**
   A: Yes, you can create new validators in the `scripts/validators/` directory and register them in `scripts/validate.py`.

4. **Q: How do I handle false positives?**
   A: Use the bypass flags (`SKIP_TESTS=1` or `SKIP_STANDARDS=1`) for legitimate cases, but document the reason.

### Troubleshooting Guide

1. **Validation Failures**
   - Check the error messages in the logs
   - Verify the validation rules are up to date
   - Ensure all dependencies are installed
   - Check for conflicting configurations

2. **Performance Issues**
   - Review the Cursor maintenance section
   - Check for large files in the workspace
   - Verify system resources
   - Monitor extension conflicts

3. **Git Hook Issues**
   - Verify hook permissions
   - Check hook installation
   - Review hook logs
   - Ensure correct path configuration

## Version History

### v1.0.0 (Current)
- Initial release
- Basic validation rules
- Pre-push hook implementation
- Core validators

## Best Practices

### Development Workflow
1. Always run validations locally before pushing
2. Keep validation rules up to date
3. Document any bypass decisions
4. Regular maintenance of Cursor environment
5. Use checklists to guide Cursor's development process
6. Regularly review and reinforce important rules with Cursor

### Code Organization
1. Follow the established project structure
2. Maintain clear separation of concerns
3. Keep validation rules modular
4. Document all custom validators
5. Use checklists to ensure Cursor follows the intended architecture

### Security Considerations
1. Regular security audits
2. Keep dependencies updated
3. Follow security best practices
4. Monitor for vulnerabilities
5. Use security checklists to guide Cursor's implementation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
