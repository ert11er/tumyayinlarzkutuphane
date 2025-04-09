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