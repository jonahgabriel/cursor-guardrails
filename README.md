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
- [Git Branching Strategy](#git-branching-strategy)
- [Validation Rules](#validation-rules)
- [Validation Scripts](#validation-scripts)
- [Usage](#usage)
- [Bypassing Validations](#bypassing-validations)
- [Contributing](#contributing)
- [Cursor Maintenance and Troubleshooting](#cursor-maintenance-and-troubleshooting)
- [FAQ](#faq)
- [Version History](#version-history)
- [Best Practices](#best-practices)
- [Feedback and Evolution](#feedback-and-evolution)
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

4. **Development Workflow Best Practices**
   - **Incremental Development**
     - Implement features in small, testable chunks
     - Complete one component before moving to the next
     - Regular commits with meaningful messages
     - Daily code reviews and validation
   
   - **Continuous Testing**
     - Write tests before or alongside feature implementation
     - Run tests after each significant change
     - Maintain a test-first mindset
     - Regular test suite execution
   
   - **Quality Gates**
     - Code review requirements
     - Test coverage thresholds
     - Performance benchmarks
     - Security scan requirements
   
   - **Documentation Updates**
     - Keep documentation in sync with code changes
     - Update API documentation immediately
     - Maintain changelog
     - Document breaking changes

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

**Error Handling and Logging**
- [ ] Structured logging implementation
  - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Include contextual information in log messages
  - Implement log rotation and retention policies
  - Use consistent log format across the application
- [ ] Error handling strategy
  - Define custom exception classes for different error types
  - Implement graceful degradation
  - Provide meaningful error messages to users
  - Log detailed error information for debugging
- [ ] Monitoring and alerting
  - Set up error rate monitoring
  - Configure alerts for critical errors
  - Implement health check endpoints
  - Monitor system performance metrics

**Testing Requirements**
- [ ] Unit tests for all operations
  - Write unit tests immediately after completing each individual feature/component
  - This helps catch issues early and reduces the need for extensive refactoring
  - Ensures each component works correctly in isolation
  - Makes it easier to identify the source of bugs
- [ ] Integration tests for API endpoints
  - Implement integration tests after completing each major feature set
  - Tests how different components work together
  - Helps catch interface mismatches and integration issues
  - Reduces the propagation of errors across the system
- [ ] Edge case testing
- [ ] Performance testing
- [ ] Security testing

**Documentation**
- [ ] API documentation
- [ ] Setup instructions
- [ ] Usage examples
- [ ] Error code documentation
- [ ] Performance considerations

**Deployment and Release Management**
- [ ] Version Control Strategy
  - Semantic versioning (MAJOR.MINOR.PATCH)
  - Branch naming conventions
  - Release branch management
  - Tag management for releases
- [ ] Deployment Pipeline
  - Automated build process
  - Environment-specific configurations
  - Deployment validation steps
  - Rollback procedures
- [ ] Release Process
  - Release checklist
  - Changelog maintenance
  - Release notes generation
  - Post-deployment verification
- [ ] Environment Management
  - Development environment setup
  - Staging environment configuration
  - Production environment requirements
  - Environment-specific variables

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

## Git Branching Strategy

### Branch Types and Naming Conventions

1. **Main Branches**
   - `main` - Production-ready code
   - `develop` - Integration branch for features
   - `release/*` - Release preparation branches
   - `hotfix/*` - Production hotfix branches

2. **Feature Branches**
   - Format: `feature/<ticket-number>-<description>`
   - Example: `feature/ABC-123-add-user-authentication`
   - Branch from: `develop`
   - Merge to: `develop`

3. **Bug Fix Branches**
   - Format: `bugfix/<ticket-number>-<description>`
   - Example: `bugfix/ABC-456-fix-login-validation`
   - Branch from: `develop`
   - Merge to: `develop`

4. **Release Branches**
   - Format: `release/v<version>`
   - Example: `release/v1.2.0`
   - Branch from: `develop`
   - Merge to: `main` and `develop`

5. **Hotfix Branches**
   - Format: `hotfix/<ticket-number>-<description>`
   - Example: `hotfix/ABC-789-fix-security-vulnerability`
   - Branch from: `main`
   - Merge to: `main` and `develop`

### Branch Lifecycle

1. **Feature Development**
   - Create feature branch from `develop`
   - Implement changes with regular commits
   - Keep branch up to date with `develop`
   - Create pull request when ready
   - Delete branch after successful merge

2. **Release Process**
   - Create release branch from `develop`
   - Perform release testing and fixes
   - Merge to `main` when ready
   - Tag the release in `main`
   - Merge back to `develop`
   - Delete release branch

3. **Hotfix Process**
   - Create hotfix branch from `main`
   - Implement fix with regular commits
   - Test thoroughly
   - Merge to `main` and `develop`
   - Tag the hotfix release
   - Delete hotfix branch

### Commit Guidelines

1. **Commit Message Format**
   ```
   <type>(<scope>): <description>

   [optional body]

   [optional footer]
   ```

2. **Commit Types**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes
   - `refactor`: Code refactoring
   - `test`: Adding or modifying tests
   - `chore`: Maintenance tasks

3. **Example Commit Messages**
   ```
   feat(auth): add OAuth2 authentication
   fix(api): handle null response in user endpoint
   docs(readme): update installation instructions
   ```

### Branch Protection Rules

1. **Main Branch Protection**
   - Require pull request reviews
   - Require status checks to pass
   - Require up-to-date branches
   - No direct pushes
   - Require signed commits

2. **Develop Branch Protection**
   - Require pull request reviews
   - Require status checks to pass
   - Allow direct pushes for maintainers
   - Require signed commits

3. **Feature Branch Requirements**
   - Must be up to date with develop
   - Must pass all CI checks
   - Must have required reviews
   - Must follow naming convention

### Best Practices

1. **Branch Management**
   - Keep branches short-lived
   - Regular rebasing with develop
   - Clean up merged branches
   - Use meaningful branch names
   - One feature per branch

2. **Pull Request Guidelines**
   - Clear description of changes
   - Link to related issues
   - Include testing steps
   - Update documentation
   - Request appropriate reviewers

3. **Code Review Process**
   - Review within 24 hours
   - Focus on code quality
   - Check test coverage
   - Verify documentation
   - Ensure CI passes

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

## Feedback and Evolution

This project is continuously evolving based on real-world experiences and community feedback. Your input is valuable in helping improve these guardrails for everyone.

### How to Provide Feedback

1. **GitHub Issues**
   - Create an issue for bug reports
   - Suggest improvements or new features
   - Share your experiences with specific rules
   - Report false positives in validations

2. **Rule Improvements**
   - Share examples of rules that worked well for you
   - Suggest modifications to existing rules
   - Propose new validation categories
   - Share edge cases that need consideration

3. **Documentation**
   - Suggest clarifications to existing documentation
   - Share your use cases and success stories
   - Propose additional examples
   - Help improve troubleshooting guides

4. **Community Discussion**
   - Share your experiences with Cursor
   - Discuss alternative approaches
   - Share tips for effective rule implementation
   - Help others with their specific use cases

### Evolution Process

1. **Rule Updates**
   - Rules are regularly reviewed and updated
   - Changes are based on practical experience
   - Updates consider community feedback
   - Documentation is kept in sync with changes

2. **Validation Improvements**
   - Validators are refined based on usage
   - False positives are addressed
   - New validation types are added as needed
   - Performance optimizations are implemented

3. **Documentation Updates**
   - Examples are expanded based on real usage
   - Troubleshooting guides are updated
   - Best practices are refined
   - New sections are added as needed

Remember: This is a community-driven project, and your feedback helps make it better for everyone. Whether you're a beginner or an expert, your perspective is valuable in shaping these guardrails.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
