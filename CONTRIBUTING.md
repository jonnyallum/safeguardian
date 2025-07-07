# Contributing to SafeGuardian

Thank you for your interest in contributing to SafeGuardian! This project aims to protect children from online grooming and other digital threats. Your contributions can help make the internet safer for children worldwide.

## 🛡️ Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Child Safety First**: All contributions must prioritize child protection and safety
- **Ethical Development**: Respect privacy rights while enabling protection
- **Professional Conduct**: Maintain respectful and constructive communication
- **Legal Compliance**: Ensure all contributions comply with applicable laws
- **Transparency**: Be open about the purpose and functionality of your contributions

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7.0+
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/jonnyallum/safeguardian.git
   cd safeguardian
   ```

2. **Backend Setup**
   ```bash
   cd safeguardian-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup**
   ```bash
   # Mobile App
   cd safeguardian-mobile
   npm install
   
   # Dashboard
   cd ../safeguardian-dashboard
   npm install
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb safeguardian_dev
   
   # Run migrations
   cd safeguardian-backend
   python manage.py migrate
   ```

5. **Run Tests**
   ```bash
   # Backend tests
   cd safeguardian-backend
   python -m pytest
   
   # Frontend tests
   cd safeguardian-mobile
   npm test
   
   cd ../safeguardian-dashboard
   npm test
   ```

## 📝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the appropriate template** for bug reports or feature requests
3. **Provide detailed information** including:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, browser, versions)
   - Screenshots or logs if applicable

### Submitting Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

2. **Make Your Changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new grooming detection pattern"
   ```
   
   Use conventional commit format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/modifications
   - `refactor:` for code refactoring
   - `security:` for security-related changes

4. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a pull request on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/demos for UI changes
   - Test results

## 🎯 Areas for Contribution

### High Priority
- **AI/ML Improvements**: Enhance grooming detection algorithms
- **Security Enhancements**: Strengthen encryption and authentication
- **Performance Optimization**: Improve real-time monitoring efficiency
- **Mobile App Features**: Enhance user experience and functionality
- **Documentation**: Improve user guides and technical documentation

### Medium Priority
- **Platform Integrations**: Add support for new social media platforms
- **Analytics Dashboard**: Enhance reporting and visualization
- **Internationalization**: Add support for multiple languages
- **Accessibility**: Improve accessibility for users with disabilities

### Ongoing Needs
- **Testing**: Increase test coverage and add integration tests
- **Bug Fixes**: Address reported issues and edge cases
- **Code Quality**: Refactor and optimize existing code
- **Documentation**: Keep documentation up-to-date

## 📋 Coding Standards

### Python (Backend)

```python
# Use type hints
def analyze_message(content: str, sender_age: int) -> Dict[str, Any]:
    """Analyze message content for risk factors.
    
    Args:
        content: The message content to analyze
        sender_age: Age of the message sender
        
    Returns:
        Dictionary containing analysis results
    """
    pass

# Follow PEP 8
# Use descriptive variable names
# Add docstrings to all functions and classes
# Use logging instead of print statements
```

### JavaScript/TypeScript (Frontend)

```javascript
// Use const/let instead of var
const analyzeMessage = async (content, senderAge) => {
  // Use descriptive function names
  // Add JSDoc comments for complex functions
  // Use async/await for promises
  // Handle errors appropriately
};

// Component naming (PascalCase)
const MessageAnalyzer = ({ message, onAnalysisComplete }) => {
  // Use hooks appropriately
  // Add PropTypes or TypeScript types
  // Follow React best practices
};
```

### General Guidelines

- **Security First**: Never commit secrets, API keys, or sensitive data
- **Performance**: Consider performance implications of your changes
- **Accessibility**: Ensure UI changes are accessible
- **Mobile-First**: Design for mobile devices first
- **Error Handling**: Implement comprehensive error handling
- **Logging**: Add appropriate logging for debugging and monitoring

## 🧪 Testing Guidelines

### Backend Testing

```python
# Unit tests
def test_grooming_detection():
    detector = GroomingDetector()
    result = detector.analyze("concerning message content")
    assert result['risk_level'] == 'high'

# Integration tests
def test_alert_generation_flow():
    # Test complete flow from message to alert
    pass
```

### Frontend Testing

```javascript
// Component tests
test('MessageAnalyzer displays risk level', () => {
  render(<MessageAnalyzer message={mockMessage} />);
  expect(screen.getByText('High Risk')).toBeInTheDocument();
});

// Integration tests
test('alert creation workflow', async () => {
  // Test user interactions and API calls
});
```

### Test Requirements

- **Unit Tests**: All new functions and methods
- **Integration Tests**: API endpoints and user workflows
- **Security Tests**: Authentication and authorization
- **Performance Tests**: Critical paths and bottlenecks
- **Accessibility Tests**: UI components and workflows

## 🔒 Security Considerations

### Sensitive Data Handling

- **Never log sensitive information** (messages, personal data)
- **Use encryption** for all stored data
- **Implement proper authentication** and authorization
- **Follow OWASP guidelines** for web security
- **Validate all inputs** to prevent injection attacks

### AI/ML Security

- **Model Security**: Protect against adversarial attacks
- **Data Privacy**: Ensure training data doesn't leak personal information
- **Bias Prevention**: Test for and mitigate algorithmic bias
- **Explainability**: Ensure AI decisions can be explained

## 📚 Documentation

### Required Documentation

- **Code Comments**: Explain complex logic and algorithms
- **API Documentation**: Document all endpoints and parameters
- **User Guides**: Step-by-step instructions for end users
- **Deployment Guides**: Infrastructure and deployment instructions
- **Security Documentation**: Security measures and best practices

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date with code changes
- Use proper markdown formatting

## 🎉 Recognition

Contributors will be recognized in:

- **README.md**: Listed in the contributors section
- **Release Notes**: Mentioned for significant contributions
- **Documentation**: Credited for documentation improvements
- **Community**: Highlighted in community discussions

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the docs/ directory for guides
- **Code Review**: Request reviews from maintainers

## 🚨 Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security concerns to: security@safeguardian.com
2. Include detailed information about the vulnerability
3. Allow time for the issue to be addressed before public disclosure
4. We will acknowledge receipt within 48 hours

## 📄 Legal Considerations

By contributing to SafeGuardian, you:

- **Grant License**: Agree to license your contributions under the MIT License
- **Confirm Ownership**: Confirm you have the right to contribute the code
- **Accept Responsibility**: Understand the ethical implications of child protection software
- **Comply with Laws**: Ensure your contributions comply with applicable laws

## 🌟 Thank You

Your contributions help protect children online. Every improvement, no matter how small, makes a difference in keeping kids safe in the digital world.

Together, we can build a safer internet for children everywhere! 🛡️👶

