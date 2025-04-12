import csv
import os
import requests
import subprocess
# Remove Tkinter imports
# import tkinter as tk
# from tkinter import ttk
# from tkinter import messagebox
from PIL import Image # Keep for placeholder creation
# from PIL import ImageTk # Remove Tkinter-specific image type
# import io # Remove
# import webbrowser # Remove
# import pyperclip # Remove
import hashlib
from flask import Flask, abort, g, send_from_directory, request, jsonify, Response, stream_with_context, session, redirect, url_for, flash, render_template_string
from markupsafe import Markup
import urllib.parse # To encode URL for passing as parameter
import random # For password generation
import string # For password generation

# --- REMOVE THE ENTIRE AppDownloader Class Definition ---
# class AppDownloader:
#     """
#     A GUI application for downloading educational content from a digital library.
#     Displays books organized by category with cover images and download buttons.
#     """
#     
#     def __init__(self, master):
#         # ... ALL THE WAY DOWN TO ...
#         messagebox.showerror("Error", error_msg)
# --- END OF AppDownloader Class Removal ---


# --- Configuration (Should be near the top now) ---
DATA_FILE = "data.csv"
GITHUB_DATA_URL = "https://raw.githubusercontent.com/ert11er/tumyayinlarzkutuphane/main/data.csv"
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "data")
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "static")

# Ensure directories exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
# Create a placeholder image if it doesn't exist
placeholder_path = os.path.join(STATIC_FOLDER, "placeholder.png")
if not os.path.exists(placeholder_path):
    try:
        # Use the imported Image from PIL
        img = Image.new('RGBA', (150, 200), color='#444')
        img.save(placeholder_path)
        print("[LOG] Created placeholder.png")
    except NameError: # Catch if PIL wasn't imported or failed
         print("[LOG] Warning: PIL/Pillow not installed or failed. Cannot create placeholder image.")
    except Exception as e:
        print(f"[LOG] Error creating placeholder: {e}")


# --- Flask App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Generate a random secret key each run

# --- Password Generation ---
# Generate a 5-digit random password ONCE at startup
LOGIN_PASSWORD = "".join(random.choices(string.digits, k=5))
print("*" * 40)
print(f"ACCESS PASSWORD: {LOGIN_PASSWORD}")
print("*" * 40)
# Store it in app config for easy access within routes (optional but clean)
app.config['LOGIN_PASSWORD'] = LOGIN_PASSWORD

# --- Data Loading Functions (Now defined AFTER constants) ---
def load_data_from_csv(filename=DATA_FILE): # DATA_FILE is now defined before this line
    """Loads book data from the CSV file."""
    data = []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append({
                    'name': row.get('name', 'N/A').strip(),
                    'downloadurl': row.get('downloadurl', '').strip(),
                    'unlockkey': row.get('unlockkey', 'none').strip(),
                    'category': str(row.get('category', '')).strip(),
                    'publisher': row.get('publisher', 'N/A').strip(),
                    'coverimageurl': row.get('coverimageurl', '').strip()
                })
        print(f"[LOG] Loaded {len(data)} items from {filename}")
        return data
    except FileNotFoundError:
        print(f"[LOG] ERROR: Data file '{filename}' not found.")
        return []
    except Exception as e:
        print(f"[LOG] EXCEPTION loading data: {e}")
        return []

def check_and_update_data():
    """Checks for data file updates from GitHub (Simplified)."""
    if not os.path.exists(DATA_FILE):
        print(f"[LOG] Local data file '{DATA_FILE}' not found. Attempting download...")
        try:
            response = requests.get(GITHUB_DATA_URL, timeout=10)
            response.raise_for_status() # Raise error for bad status
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                file.write(response.text)
            print("[LOG] Data file successfully downloaded.")
        except requests.exceptions.RequestException as e:
             print(f"[LOG] Error downloading data file: {e}")
        except Exception as e:
             print(f"[LOG] Error writing data file: {e}")


# Load data when the application starts
check_and_update_data()
book_data = load_data_from_csv()

# --- HTML Structure (as Python strings/functions) ---

def generate_book_card_html(book):
    """Generates HTML for a single book card."""
    # Basic fallback logic for images
    image_url = book.get('coverimageurl', '') or '/static/placeholder.png'
    image_alt = f"{book.get('name', 'Book')} Cover"
    placeholder_url = '/static/placeholder.png'
    # Use Markup to prevent accidental HTML injection from data
    book_name = Markup.escape(book.get('name', 'N/A'))
    publisher = Markup.escape(book.get('publisher', 'N/A'))
    download_url = book.get('downloadurl', '')
    unlock_key = book.get('unlockkey', 'none') # Get raw key for logic
    js_unlock_key = Markup.escape(unlock_key) # Escape for JS

    # Button Logic
    button_html = ""
    if download_url:
        if download_url.startswith('site://'):
            site_url = Markup.escape(download_url[7:])
            button_html = f'<a href="{site_url}" target="_blank" class="download-button">SİTEYE GİT</a>'
        else:
            # Encode the download URL to safely pass it as a query parameter
            encoded_url = urllib.parse.quote_plus(download_url)
            encoded_key = urllib.parse.quote_plus(unlock_key)
            # Link to the new server-side download route
            action_url = f"/download-and-run?url={encoded_url}&key={encoded_key}"
            button_html = f'''<a href="{action_url}"
                               target="_blank" 
                               class="download-button"
                               onclick="handleServerDownload(this.href, \'{js_unlock_key}\'); return false;">
                               İNDİR & ÇALIŞTIR
                            </a>''' # Changed text slightly
    else:
        button_html = '<span class="download-button" style="background-color: grey; cursor: default;">MEVCUT DEĞİL</span>'

    return f"""
    <div class="book-card">
        <div class="book-cover">
            <img src="{image_url}"
                 alt="{image_alt}"
                 onerror="this.onerror=null; this.src='{placeholder_url}';">
        </div>
        <div class="book-info">
            <div class="name">{book_name}</div>
            <div class="publisher">{publisher}</div>
        </div>
        {button_html}
    </div>
    """

def generate_category_section_html(category_key, category_books):
    """Generates HTML for a category section, including its books."""
    if not category_books:
        return ""

    # Generate HTML for all book cards in this category
    books_html = "".join(generate_book_card_html(book) for book in category_books)

    category_header = Markup.escape(category_key)

    return f"""
    <div class="category-section">
        <div class="books-container">
            {books_html}
        </div>
         <div class="category-header">{category_header}</div>
    </div>
    """

def generate_main_html(categories_data, sorted_keys):
    """Generates the complete HTML page FOR LOGGED IN USERS."""

    # Generate HTML for all category sections
    all_categories_html = "".join(
        generate_category_section_html(key, categories_data.get(key, []))
        for key in sorted_keys
    )

    # Add a logout button
    logout_button = '<div style="text-align: center; margin: 20px;"><a href="/logout" style="color: #FF4136; text-decoration: none; border: 1px solid #FF4136; padding: 5px 10px; border-radius: 3px;">Çıkış Yap</a></div>'

    # Embed everything into the main HTML structure
    return f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TÜM Yayınlar Z-Kütüphane</title>
    <style>
        body {{
            background-color: #1E1E1E; color: white;
            font-family: Arial, sans-serif; margin: 0; padding: 0;
        }}
        .category-section {{
            margin: 20px; padding-bottom: 10px;
            border-bottom: 2px solid white;
        }}
        .category-header {{
            font-size: 2em; font-weight: bold;
            margin-bottom: 15px; padding-left: 10px;
        }}
        .books-container {{
            display: flex; overflow-x: auto; padding-bottom: 15px;
            gap: 15px; min-height: 330px;
        }}
        .books-container::-webkit-scrollbar {{ height: 10px; }}
        .books-container::-webkit-scrollbar-track {{ background: #555; border-radius: 5px; }}
        .books-container::-webkit-scrollbar-thumb {{ background: #888; border-radius: 5px; }}
        .books-container::-webkit-scrollbar-thumb:hover {{ background: #aaa; }}
        .book-card {{
            background-color: #2E2E2E; border-radius: 5px; padding: 10px;
            width: 170px; flex-shrink: 0; text-align: center;
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .book-cover img {{
            width: 150px; height: 200px; object-fit: cover;
            background-color: #444; display: block; margin: 0 auto 10px auto;
        }}
        .book-info .name {{ font-size: 0.9em; margin-bottom: 5px; min-height: 2.4em; }}
        .book-info .publisher {{ font-size: 0.75em; color: gray; margin-bottom: 10px; min-height: 1.2em; }}
        .download-button {{
            display: block; background-color: #FF4136; color: white;
            padding: 8px 0; border: none; border-radius: 3px;
            text-decoration: none; font-weight: bold; cursor: pointer; margin-top: auto;
        }}
        .download-button:hover {{ opacity: 0.9; }}
        footer {{
            padding: 10px 20px; font-size: 0.8em; color: gray;
            display: flex; justify-content: space-between; margin-top: 20px;
        }}
        .status-message {{ position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); background-color: rgba(0,0,0,0.7); color: white; padding: 10px 20px; border-radius: 5px; z-index: 1000; display: none; }} /* Added for feedback */
    </style>
</head>
<body>
    <h1 style="text-align: center; margin-top: 20px;">TÜM Yayınlar Z-Kütüphane</h1>
    {logout_button} 
    {all_categories_html}
    <footer>
        <span>26.03.2025</span> <!-- Placeholder date -->
        <span>PERNUS</span> <!-- Placeholder version -->
    </footer>

    <div id="status-message" class="status-message"></div> <!-- Added for feedback -->
    <script>
        async function copyToClipboard(text) {{
            if (!text || text.toLowerCase() === 'none') return Promise.resolve(); // Return resolved promise
            try {{
                await navigator.clipboard.writeText(text);
                console.log('Activation key copied to clipboard.');
                // Optional: show temporary feedback instead of alert
                // showStatusMessage('Aktivasyon Anahtarı Panoya Kopyalandı', 2000); 
            }} catch (err) {{
                console.error('Clipboard copy failed: ', err);
                alert('Anahtar kopyalanamadı.');
                return Promise.reject(err); // Propagate error if needed
            }}
        }}

        // Display temporary status messages
        function showStatusMessage(message, duration = 3000) {{
            const statusElement = document.getElementById('status-message');
            if (statusElement) {{
                statusElement.textContent = message;
                statusElement.style.display = 'block';
                setTimeout(() => {{
                    statusElement.style.display = 'none';
                }}, duration);
            }}
        }}

        // Renamed function, now calls the backend route
        async function handleServerDownload(actionUrl, unlockKey) {{
            showStatusMessage('İndirme ve çalıştırma başlatılıyor...'); // Immediate feedback
            try {{
                // Copy key first (await ensures it attempts before fetch)
                await copyToClipboard(unlockKey); 

                // Fetch the backend route which triggers download and run
                const response = await fetch(actionUrl); 
                
                // Check if the server responded ok (2xx status code)
                if (!response.ok) {{
                    // Try to get error message from server if available
                    let errorMsg = `Server error: ${response.status}`;
                    try {{
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    }} catch (e) {{ /* Ignore if response is not JSON */ }}
                    throw new Error(errorMsg); // Throw error to be caught below
                }}

                // Get response (expecting JSON)
                const result = await response.json(); 

                // Display success or error message from server
                if (result.status === 'success') {{
                    showStatusMessage(result.message || 'İşlem başarılı.', 5000);
                }} else {{
                    showStatusMessage(`Hata: ${result.error || 'Bilinmeyen sunucu hatası.'}`, 5000);
                }}

            }} catch (error) {{
                console.error('Failed to trigger server download/run:', error);
                showStatusMessage(`İstek başarısız: ${error.message}`, 5000);
            }}
        }}
    </script>
</body>
</html>
    """

# Simple HTML template for the login page
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Giriş Yap</title>
    <style>
        body { background-color: #1E1E1E; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background-color: #2E2E2E; padding: 30px; border-radius: 8px; text-align: center; }
        input[type=password] { padding: 10px; margin-top: 10px; margin-bottom: 20px; border: 1px solid #555; border-radius: 4px; background-color: #444; color: white; }
        input[type=submit] { padding: 10px 20px; border: none; border-radius: 4px; background-color: #FF4136; color: white; font-weight: bold; cursor: pointer; }
        input[type=submit]:hover { opacity: 0.9; }
        .flash-error { color: #FF4136; margin-bottom: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Giriş Gerekli</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="flash-error">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="post">
            <label for="password">Şifre:</label><br>
            <input type="password" id="password" name="password" required autofocus><br>
            <input type="submit" value="Giriş Yap">
        </form>
    </div>
</body>
</html>
"""

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        entered_password = request.form.get('password')
        correct_password = app.config['LOGIN_PASSWORD'] # Get password stored at startup
        if entered_password == correct_password:
            session['logged_in'] = True # Mark session as logged in
            flash('Giriş başarılı!', 'success') # Optional success message
            return redirect(url_for('index')) # Redirect to main page
        else:
            flash('Yanlış şifre.', 'error') # Show error message
            return redirect(url_for('login')) # Redirect back to login page
    
    # If GET request or failed POST, show the login form
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('logged_in', None) # Clear the session flag
    flash('Başarıyla çıkış yapıldı.', 'info') # Optional message
    return redirect(url_for('login')) # Redirect to login page

@app.route('/')
def index():
    """Main route to display the books, requires login."""
    if not session.get('logged_in'):
        return redirect(url_for('login')) # If not logged in, go to login page

    # --- If logged in, proceed to generate the main page ---
    categories = {'5': [], '6': [], '7': []}
    all_category_books = []
    for book in book_data:
        category = book.get('category', '')
        if category.lower() == 'all':
            all_category_books.append(book)
        elif category in categories:
            categories[category].append(book)
    for category_key in categories:
        categories[category_key].extend(all_category_books)
    valid_categories = {k: v for k, v in categories.items() if v}
    sorted_category_keys = sorted(valid_categories.keys(), key=lambda x: int(x))

    html_content = generate_main_html(valid_categories, sorted_category_keys)
    return html_content

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serves static files (placeholder image). No login required."""
    if filename == "placeholder.png":
        try:
            return send_from_directory(STATIC_FOLDER, filename)
        except FileNotFoundError:
            abort(404)
    else:
        abort(404)

# --- Protected Download Route ---
@app.route('/download-and-run')
def download_and_run():
    """Downloads and runs file on server, requires login."""
    if not session.get('logged_in'):
        # You could redirect to login, but returning an error is clearer for API-like calls
        return jsonify({"status": "error", "error": "Authentication required"}), 401 

    # --- If logged in, proceed with download/run logic ---
    download_url = request.args.get('url')
    unlock_key = request.args.get('key', 'none')
    if not download_url: return jsonify({"status": "error", "error": "Missing download URL"}), 400
    print(f"[LOG] Received download/run request for URL: {download_url}")
    print(f"[LOG] Associated Unlock Key: {unlock_key}")
    try:
        print(f"[LOG] Downloading from URL to server: {download_url}")
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        # --- Prepare filename ---
        try:
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                 import cgi; value, params = cgi.parse_header(content_disposition)
                 original_filename = params.get('filename')
            else original_filename = None
            if not original_filename:
                parsed_url = urllib.parse.urlparse(download_url)
                original_filename = os.path.basename(parsed_url.path) if parsed_url.path else "downloaded_file"
        except Exception as e:
             print(f"[WARN] Could not reliably determine filename: {e}")
             original_filename = "downloaded_file"
        # --- Sanitize & Create Path ---
        base_name, extension = os.path.splitext(original_filename)
        safe_base_name = "".join(c for c in base_name if c.isalnum() or c in ('_', '-', '.'))[:100]
        safe_extension = "".join(c for c in extension if c.isalnum() or c == '.')[:10]
        new_filename_base = f"{safe_base_name}_{unlock_key}" if unlock_key.lower() != "none" else safe_base_name
        filename = f"{new_filename_base}{safe_extension}"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        print(f"[LOG] Saving file to server path: {filepath}")
        # --- Save File ---
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        print("[LOG] Server download completed successfully.")
        # --- Execute File ---
        print(f"[LOG] Attempting to launch file on server: {filepath}")
        try:
            os.startfile(filepath)
            print(f"[LOG] Successfully launched {filepath} on server.")
            return jsonify({"status": "success", "message": f"'{filename}' downloaded and launched on server."})
        except FileNotFoundError:
             print(f"[ERROR] File not found after download? Path: {filepath}")
             return jsonify({"status": "error", "error": f"File not found at path: {filepath}"}), 500
        except Exception as e:
            print(f"[ERROR] Could not launch file '{filepath}' on server: {e}")
            return jsonify({"status": "error", "error": f"Could not launch file: {e}"}), 500
    # --- Error Handling for Download ---
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout downloading {download_url}")
        return jsonify({"status": "error", "error": "Download timed out"}), 504
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to download {download_url}: {e}")
        return jsonify({"status": "error", "error": f"Download failed: {e}"}), 502
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during download/run: {e}")
        return jsonify({"status": "error", "error": f"Unexpected server error: {e}"}), 500

# --- Run the App ---
if __name__ == '__main__':
    # Keep localhost restriction AND add password layer
    app.run(debug=True, port=5000) # No host='0.0.0.0'
