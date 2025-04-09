# TÜM Yayınlar Z-Kütüphane

Hey there! 👋 Welcome to TÜM Yayınlar Z-Kütüphane, your one-stop digital library for Turkish educational content. Whether you're a student, teacher, or parent, we've got you covered with a wide range of materials from various Turkish publishers.

## 📚 What's This All About?

This is a user-friendly app that helps you access and download educational materials, specifically designed for grades 5-7. Think of it as your digital bookshelf where you can:

- Browse through different grade levels easily
- Preview book covers before downloading
- Download content with just one click
- Get automatic updates to stay current
- Enjoy fast loading thanks to our image caching
- Use a sleek dark theme interface that's easy on the eyes

## 🚀 Getting Started

1. First things first, grab the `main.py` file
2. Install the stuff we need (don't worry, it's simple!):
```bash
pip install tkinter pillow requests pyperclip
```

3. Ready to roll? Just run:
```bash
python main.py
```

And that's it! The app will:
- Check for the latest content automatically
- Set up your folders (`data/` for downloads, `assets/` for images)
- Show you all the available books by grade level
- Handle downloads and activation keys for you

## ✨ Cool Features

- **Always Up-to-Date**: The app checks GitHub for the newest content database
- **Smart Image Handling**: We save book covers locally so they load super fast next time
- **Easy Navigation**: Everything's organized by grade (5, 6, and 7)
- **Publisher Info**: Know exactly where your content is coming from
- **Smart Downloads**: Handles both direct downloads and website redirects
- **Activation Keys**: Automatically copies them to your clipboard when needed

## 📁 How It's Organized
```
├── main.py         # The main app
├── data/           # Where your downloads live
├── assets/         # Where we keep the book covers
└── data.csv        # The content database
```

## 🔧 What You'll Need

- Python 3.6 or newer
- Internet connection (for first-time setup and downloads)
- Windows OS (we've tested it on Windows 10)

## 🤝 Want to Help?

Awesome! We love contributions. Here's how you can help make this project even better:

### Ways to Pitch In

1. **Code Contributions**
   - Fork it
   - Create your feature branch (`git checkout -b feature/awesome-feature`)
   - Make your changes
   - Test everything works
   - Send us a Pull Request

2. **Found a Bug?**
   - Open an issue on GitHub
   - Tell us how to recreate the bug
   - Let us know your system info
   - Screenshots help!

3. **Got Ideas?**
   - We're all ears! Open an issue with the "enhancement" tag
   - Tell us what you're thinking
   - Share examples if you can

4. **Documentation**
   - Help improve this README
   - Add helpful code comments
   - Create guides or tutorials

### Setting Up for Development

1. Get the code:
```bash
git clone https://github.com/yourusername/tumyayinlarzkutuphane.git
cd tumyayinlarzkutuphane
```

2. Set up your virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install what you need:
```bash
pip install -r requirements.txt
```

### Code Style

- Follow PEP 8 (but don't stress too much about it)
- Use names that make sense
- Document your functions
- Keep things simple
- Comment the tricky bits

### Making Pull Requests

1. Update the README if you've added something new
2. Update requirements.txt if you've added dependencies
3. Get a thumbs up from at least one maintainer

## 📝 Legal Stuff

All content in this app is freely available and legit:
- Not pirated
- Not paid content
- From official sources
- Provided by publishers for education

## 🎉 Version

Currently running Version 0.9.3 Beta (as of 9 April 2025)

## 📜 License

This project is under the MIT License - check out the [LICENSE](LICENSE) file for the details.

## 🤝 Code of Conduct

By participating in this project, you're agreeing to be awesome to everyone else who participates too. Let's keep it friendly!

Need help? Found a bug? Have a cool idea? Open an issue on GitHub and let's talk!