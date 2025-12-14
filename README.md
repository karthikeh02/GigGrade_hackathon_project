# 🎯 GitGrade: AI Repository Analyzer

Lightning-fast comprehensive GitHub repository analysis with automated scoring and AI-powered recommendations.
CHECKOUT MY WEBSITE - https://gitgradehackathon.streamlit.app/


## 🚀 Features

- **Instant Analysis**: Analyze any public GitHub repository in seconds
- **AI-Powered Insights**: Get intelligent summaries and improvement roadmaps
- **Comprehensive Scoring**: 7 different quality metrics
- **Beautiful UI**: Clean, intuitive interface with real-time progress

## 📊 Metrics Analyzed

1. **Code Quality** - Complexity and maintainability analysis
2. **Structure** - Project organization and best practices
3. **Documentation** - README quality and completeness
4. **Tests** - Test coverage and quality
5. **Community** - Stars, forks, and engagement
6. **Activity** - Commit frequency and consistency
7. **Collaboration** - Branches and pull request workflow

## 🛠️ Setup

### Local Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gitgrade.git
cd gitgrade

# Create virtual environment
python -m venv gitgrade_env
source gitgrade_env/bin/activate  # On Windows: gitgrade_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Configuration

1. Generate a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `public_repo`
   - Copy the token

2. Update `app.py` line 11 with your token:
   ```python
   GITHUB_TOKEN = "your_token_here"
   ```

## 🌐 Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Click "Deploy an app"
4. Select your repository
5. Set main file: `app.py`
6. Click "Deploy"!

## 📝 Usage

1. Enter any public GitHub repository URL
2. Click "Analyze Repository"
3. View comprehensive analysis with scores
4. Get AI-generated improvement recommendations

## 🎯 Example Repositories to Try

- https://github.com/pallets/flask
- https://github.com/psf/requests
- https://github.com/django/django
- https://github.com/streamlit/streamlit

## 🔒 Security Note

Never commit your GitHub token to public repositories. Use Streamlit secrets for deployment.

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

Built by Karthik. 
