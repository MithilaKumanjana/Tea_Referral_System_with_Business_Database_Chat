# Tea Business AI Management System

**Intelligent customer management and referral tracking system combining rule-based queries with AI-powered conversation for small tea businesses.**


## What Makes This Special?

This isn't just another chatbot demo. It's a production-ready business management system that solves real problems for small tea businesses through intelligent automation.

### Key Differentiators

- **Hybrid Intelligence**: Combines lightning-fast rule-based queries with natural AI conversation
- **Smart Context Management**: AI receives only relevant data, not entire datasets
- **Complete Business Solution**: Customer registration, referral tracking, discount automation
- **Production Architecture**: Docker containerization, persistent storage, health monitoring
- **Graceful Degradation**: Works perfectly with or without AI connectivity

## Features

### Customer Management
- Automated customer registration with unique ID generation
- Phone number validation and duplicate prevention
- Customer search and information retrieval
- Registration history tracking

### Referral System
- 3-tier referral code system (each customer gets 3 unique codes)
- Automatic discount eligibility tracking (3 referrals = discount earned)
- Real-time referral usage monitoring
- Referral chain visualization

### Intelligent Chat Interface
- **Rule-based queries** for fast, accurate data retrieval
- **AI-powered conversation** for business advice and general chat
- **Smart query routing** determines optimal response method
- Conversation history and context awareness

### Analytics & Reporting
- Customer acquisition metrics
- Referral program performance
- Discount distribution analysis
- Business growth tracking

### Data Management
- Excel-based persistent storage
- Automatic database backup
- Data validation and error handling
- Export capabilities for external analysis

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/MithilaKumanjana/Tea_Referral_System_with_Business_Database_Chat.git
cd tea-business-ai-system

# Create environment file
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Build and run
docker-compose up --build

# Access the application
open http://localhost:7860
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/MithilaKumanjana/Tea_Referral_System_with_Business_Database_Chat.git
cd tea-business-ai-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="your_api_key_here"

# Run application
python main.py
```

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Hybrid Chat    │    │   Data Storage  │
│    (Gradio)     │◄──►│     System       │◄──►│    (Excel)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Query Router    │
                    │                  │
                    ▼                  ▼
              ┌───────────┐    ┌──────────────┐
              │Rule-Based │    │ AI-Powered   │
              │Responses  │    │Conversation  │
              └───────────┘    └──────────────┘
```

## Usage Examples

### Customer Registration
```python
# Register new customer
register_customer("John Doe", "0771234567", referral_code="AB1234R1")

# Generated output:
# - Customer ID: JO4567
# - Referral codes: JO4567R1, JO4567R2, JO4567R3
# - Status: Active, 0/3 referrals completed
```

### Chat Interface Examples

**Data Queries (Rule-based):**
```
User: "How many customers do I have?"
Bot: "You have 127 customers registered in your tea business database."

User: "Who are my top referrers?"
Bot: "Top 5 Referrers:
      1. Sarah Johnson - 3/3 referrals (DISCOUNT EARNED)
      2. Mike Chen - 2/3 referrals (In Progress)"
```

**AI Conversation:**
```
User: "What tea would be good for winter mornings?"
Bot: "For winter mornings, I'd recommend warming teas like chai blends 
     with cinnamon and cardamom, or a robust Earl Grey. These provide 
     comfort and energy for cold mornings."
```

**Smart Data Integration:**
```
User: "Tell me about customer Sarah"
Bot: "Sarah Johnson is one of your star customers! She's completed 3/3 
     referrals and earned her discount. She registered on March 15th and 
     has been actively referring friends."
```

## API Reference

### Customer Management
```python
# Register customer
POST /api/customer/register
{
    "name": "Customer Name",
    "phone": "0771234567",
    "referral_code": "AB1234R1"  # optional
}

# Search customer
GET /api/customer/search?query=john

# Validate referral code
GET /api/referral/validate?code=AB1234R1
```

### Chat Interface
```python
# Send message
POST /api/chat
{
    "message": "How many customers do I have?",
    "session_id": "optional_session_id"
}
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_PATH=./data
DEBUG_MODE=false
SERVER_HOST=0.0.0.0
SERVER_PORT=7860
```

### Docker Configuration
```yaml
# docker-compose.yml
services:
  tea-business:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./data:/app/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

## File Structure
```
tea-business-ai-system/
├── main.py                     # Application entry point
├── database_system.py          # Data management
├── chat_syetem_with_chat_gpt.py # Hybrid chat system
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-container setup
├── .env                       # Environment variables
├── data/                      # Database files
│   ├── tea_customers.xlsx     # Customer data
│   ├── tea_referrals.xlsx     # Referral tracking
│   └── tea_sales.xlsx         # Sales records
└── README.md                  # This file
```

## Advanced Features

### Smart Query Routing
The system intelligently routes queries:
- **Data queries** → Rule-based (fast, accurate)
- **Conversational queries** → AI-powered (natural, flexible)
- **Customer-specific queries** → AI with relevant data only

### Scalability Considerations
- **Database migration path**: Excel → SQLite → PostgreSQL
- **Horizontal scaling**: Multiple container instances
- **API rate limiting**: Built-in OpenAI request management
- **Caching layer**: Ready for Redis integration

### Error Handling
- Graceful AI API failures
- Data validation at input level
- Automatic retry mechanisms
- Comprehensive logging

## Development

### Setting Up Development Environment
```bash
# Clone repository
git clone https://github.com/yourusername/tea-business-ai-system.git
cd tea-business-ai-system

# Install development tools
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

### Adding New Features
1. **New chat commands**: Extend `try_rule_based_response()` in chat system
2. **Database schema changes**: Update Excel templates in `database_system.py`
3. **UI modifications**: Modify Gradio interface in `main.py`
4. **API endpoints**: Add routes to FastAPI integration

### Testing
```bash
# Run all tests
pytest

# Test specific module
pytest tests/test_database.py

# Test with coverage
pytest --cov=.

# Test Docker build
docker-compose -f docker-compose.test.yml up --build
```

## Deployment

### Production Deployment
```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# With SSL and reverse proxy
docker-compose -f docker-compose.prod.yml \
               -f docker-compose.ssl.yml up -d
```

### Cloud Platforms

**AWS ECS:**
```bash
# Build for AWS
docker build -t tea-business-system .
docker tag tea-business-system:latest your-aws-account.dkr.ecr.region.amazonaws.com/tea-business-system:latest
docker push your-aws-account.dkr.ecr.region.amazonaws.com/tea-business-system:latest
```

**Google Cloud Run:**
```bash
# Deploy to Cloud Run
gcloud run deploy tea-business-system \
  --image gcr.io/your-project/tea-business-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Heroku:**
```bash
# Heroku deployment
heroku create tea-business-system
heroku config:set OPENAI_API_KEY=your_key_here
git push heroku main
```

## Performance Optimization

### Database Performance
- Index customer_id and phone fields
- Implement data archiving for old records
- Consider PostgreSQL migration for > 10k customers

### AI Integration
- Cache frequently asked questions
- Implement request batching
- Use streaming responses for long conversations

### Monitoring
```bash
# Container resource usage
docker stats tea-business-app

# Application metrics
curl http://localhost:7860/health

# Database size monitoring
ls -la data/*.xlsx
```

## Security Considerations

### API Key Management
- Store API keys in environment variables
- Use secrets management in production
- Rotate keys regularly

### Data Protection
- Encrypt customer data at rest
- Implement access logging
- Regular security audits

### Container Security
- Use non-root user in containers
- Scan images for vulnerabilities
- Keep base images updated

## Troubleshooting

### Common Issues

**Container not accessible:**
```bash
# Check if app binds to all interfaces
# In main.py: app.launch(server_name="0.0.0.0", ...)
```

**API key errors:**
```bash
# Verify API key format
echo $OPENAI_API_KEY | wc -c  # Should be > 50 characters

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Database issues:**
```bash
# Check file permissions
ls -la data/
chmod 644 data/*.xlsx

# Verify Excel file integrity
python -c "import pandas as pd; print(pd.read_excel('data/tea_customers.xlsx').head())"
```

### Performance Issues
```bash
# Check memory usage
docker exec tea-business-app free -h

# Monitor Python processes
docker exec tea-business-app ps aux

# Check disk space
docker exec tea-business-app df -h
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes with tests
4. Ensure code quality: `black . && flake8 . && mypy .`
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request

### Code Standards
- Follow PEP 8 Python style guidelines
- Add type hints to new functions
- Include docstrings for public methods
- Write unit tests for new features
- Update documentation for API changes

### Issue Reporting
- Use the issue template
- Include system information
- Provide reproduction steps
- Add logs and error messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Version 2.0 (Coming Soon)
- SQLite database migration
- Advanced analytics dashboard
- Email notification system
- Mobile-responsive design
- Multi-language support

### Version 3.0 (Future)
- Machine learning customer insights
- Automated marketing campaigns
- Multi-tenant support
- Advanced reporting suite
- Mobile app integration

## Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Community**: Join our Discord server

### FAQ

**Q: Can I use this for other businesses besides tea?**
A: Yes! The system is easily adaptable. Modify the prompts and database schema for any referral-based business.

**Q: How many customers can it handle?**
A: Current Excel-based system handles ~10k customers efficiently. For larger scale, migrate to SQLite or PostgreSQL.

**Q: Do I need an OpenAI API key?**
A: No! The system works perfectly in rule-based mode without AI features. AI adds conversational capabilities but isn't required.

**Q: Can I deploy this commercially?**
A: Yes, under the MIT license you can use this for commercial purposes. Just follow the license terms.

**Q: How do I backup my data?**
A: Your data is stored in the `data/` directory as Excel files. Simply backup this directory regularly.

## Acknowledgments

- Built with [Gradio](https://gradio.app/) for the web interface
- Powered by [OpenAI GPT-3.5](https://openai.com/) for AI capabilities
- Uses [Pandas](https://pandas.pydata.org/) for data processing
- Containerized with [Docker](https://docker.com/)

## Contact

**Project Maintainer**: Your Name  
**Email**: your.email@domain.com  
**Project Link**: https://github.com/yourusername/tea-business-ai-system

---

**Built with ❤️ for small tea businesses worldwide**

*This project demonstrates production-ready AI application development, bridging the gap between AI experimentation and real business value creation.*
