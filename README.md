# TÜM Yayınlar Z-Kütüphane

A digital library application for downloading educational content from various Turkish publishers.

## Legal Notice

All content provided through this application is freely available. The URLs in `data.csv` are:
- Not pirated content
- Not paid content
- Freely available from official sources
- Provided by respective publishers for educational purposes

## Description

This application provides a user-friendly interface to access and download educational materials organized by grade levels (5-7). It features:

- Categorized content display by grade level
- Book cover image previews
- Easy download functionality with activation key management
- Automatic updates from GitHub
- Image caching for faster loading
- Dark theme interface

## Installation

1. Download the `main.py` file
2. Install required dependencies:
```bash
pip install tkinter pillow requests pyperclip
```

## Usage

1. Run the application:
```bash
python main.py
```

2. The application will:
   - Automatically check for and download the latest `data.csv`
   - Create necessary folders (`data/` for downloads, `assets/` for cached images)
   - Display books organized by grade levels
   - Allow downloading with automatic activation key handling

## Features

- **Automatic Updates**: Checks and downloads the latest content database from GitHub
- **Image Caching**: Stores downloaded cover images locally for faster loading
- **Grade-based Categories**: Content organized by grades 5, 6, and 7
- **Publisher Information**: Displays publisher details for each book
- **Download Management**: Handles both direct downloads and website redirects
- **Activation Key System**: Automatically copies activation keys to clipboard when needed

## Directory Structure
├── main.py # Main application file
├── data/ # Downloaded content directory
├── assets/ # Cached images directory
└── data.csv # Content database


## Technical Requirements

- Python 3.6+
- Internet connection for initial setup and downloads
- Windows OS (tested on Windows 10)

## Support

For issues and questions, please open an issue on the GitHub repository.

## Version

Current Version: PERNUS (as of 26.03.2025)

## Contributing

We welcome contributions to improve TÜM Yayınlar Z-Kütüphane! Here's how you can help:

### Ways to Contribute

1. **Code Contributions**
   - Fork the repository
   - Create a new branch (`git checkout -b feature/improvement`)
   - Make your changes
   - Test your changes thoroughly
   - Submit a Pull Request with a clear description of the changes

2. **Bug Reports**
   - Use the GitHub Issues section
   - Include detailed steps to reproduce the bug
   - Provide system information (OS, Python version)
   - Add screenshots if relevant

3. **Feature Requests**
   - Use the GitHub Issues section with the "enhancement" label
   - Clearly describe the feature and its use case
   - Provide examples if possible

4. **Documentation**
   - Help improve the README
   - Add code comments
   - Create user guides or tutorials

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tumyayinlarzkutuphane.git
cd tumyayinlarzkutuphane
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Code Style Guidelines

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Comment complex logic

### Testing

- Add tests for new features
- Ensure existing tests pass
- Test on different Python versions if possible

### Commit Guidelines

- Use clear and descriptive commit messages
- Reference issues and pull requests
- Keep commits focused and atomic
- Format: `type(scope): description`
  - Example: `feat(ui): add dark mode toggle`
  - Types: feat, fix, docs, style, refactor, test, chore

### Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the requirements.txt if you add dependencies
3. The PR will be merged once you have the sign-off of at least one maintainer

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.