import csv
import os
import requests
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import webbrowser
import pyperclip
import hashlib

class AppDownloader:
    """
    A GUI application for downloading educational content from a digital library.
    Displays books organized by category with cover images and download buttons.
    """
    
    def __init__(self, master):
        self.master = master
        self.setup_window()
        self.initialize_variables()
        self.setup_styles()
        self.create_widgets()
        self.check_data_file()
        self.load_data()

    def setup_window(self):
        """Configure the main window settings."""
        self.master.title("TÜM Yayinlar Z-Kütüphane")
        self.master.configure(bg='#1E1E1E')
        self.master.state('zoomed')

    def initialize_variables(self):
        """Initialize instance variables and constants."""
        # File paths and URLs
        self.data_file = "data.csv"
        self.github_data_url = "https://raw.githubusercontent.com/ert11er/tumyayinlarzkutuphane/main/data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.assets_folder = os.path.join(os.path.dirname(__file__), "assets")
        
        # Ensure required directories exist
        os.makedirs(self.download_folder, exist_ok=True)
        os.makedirs(self.assets_folder, exist_ok=True)
        
        # Data storage
        self.data = []
        self.images = {}  # Store image cache with URLs as keys
        self.category_filter = tk.StringVar(value="All")
        
        print("[LOG] Initialized variables and created necessary directories")

    def setup_styles(self):
        """Configure ttk styles for widgets."""
        self.style = ttk.Style()
        self.style.configure("Dark.TFrame", background='#1E1E1E')
        self.style.configure("Red.TFrame", background='#FF4136')
        self.style.configure("Dark.TLabel", background='#1E1E1E', foreground='white')
        self.style.configure("Category.TLabel", background='#1E1E1E', foreground='white', font=('Arial', 24, 'bold'))

    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Create status bar at the bottom
        self.status_frame = ttk.Frame(self.master, style="Dark.TFrame")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Date label
        self.date_label = ttk.Label(
            self.status_frame,
            text="26.03.2025",
            style="Dark.TLabel",
            font=('Arial', 8)
        )
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        # Version label
        self.version_label = ttk.Label(
            self.status_frame,
            text="PERNUS",
            style="Dark.TLabel",
            font=('Arial', 8)
        )
        self.version_label.pack(side=tk.RIGHT, padx=10)
        
        # Create a frame to hold the canvas and scrollbar
        self.canvas_frame = ttk.Frame(self.master)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Main scrollable area
        self.canvas = tk.Canvas(self.canvas_frame, bg='#1E1E1E', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Main content frame
        self.content_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.content_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event):
        """Update canvas window width when canvas is resized."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def get_cached_image(self, url, size=(180, 250), max_retries=3):
        """Get image from cache or download and cache it with retry mechanism."""
        # Create hash of URL for filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(self.assets_folder, f"{url_hash}.png")
        
        # If we already have this image in memory, return it
        if url in self.images:
            print(f"[LOG] Using memory-cached image for: {url}")
            return self.images[url]
        
        try:
            # Check if image exists in cache
            if os.path.exists(cache_path):
                print(f"[LOG] Loading disk-cached image for: {url}")
                try:
                    img = Image.open(cache_path)
                    img = img.convert('RGBA')  # Convert to RGBA to ensure compatibility
                    photo_img = ImageTk.PhotoImage(img)
                    self.images[url] = photo_img
                    return photo_img
                except Exception as e:
                    print(f"[LOG] Error loading cached image, will try downloading again: {e}")
                    # If cached image is corrupted, continue to download
            
            # If not in cache, try downloading with retries
            for attempt in range(max_retries):
                try:
                    print(f"[LOG] Downloading image (attempt {attempt + 1}/{max_retries}): {url}")
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()  # Raise an error for bad status codes
                    
                    img_data = response.content
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Convert to RGBA to ensure compatibility
                    img = img.convert('RGBA')
                    
                    # Resize image
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    
                    # Save to cache
                    img.save(cache_path, 'PNG')
                    print(f"[LOG] Saved image to cache: {cache_path}")
                    
                    # Create PhotoImage and store in memory
                    photo_img = ImageTk.PhotoImage(img)
                    self.images[url] = photo_img
                    return photo_img
                    
                except requests.exceptions.RequestException as e:
                    print(f"[LOG] Download attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:  # Last attempt
                        raise  # Re-raise the exception if all retries failed
                    continue
            
        except Exception as e:
            print(f"[LOG] ERROR loading image from {url}: {e}")
            return self.create_placeholder_image(size, url)

    def create_placeholder_image(self, size=(180, 250), url=None):
        """Create a placeholder image with error text."""
        try:
            print(f"[LOG] Creating placeholder image for: {url}")
            # Create a new image with a dark background
            img = Image.new('RGBA', size, color='#2E2E2E')
            
            # Add some error text to the placeholder
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Add error icon or symbol
            error_text = "!"
            # Try to get a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            # Center the text
            text_bbox = draw.textbbox((0, 0), error_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            # Draw the error symbol
            draw.text((x, y), error_text, fill='#FF4136', font=font)
            
            # Create PhotoImage and store in memory
            photo_img = ImageTk.PhotoImage(img)
            if url:
                self.images[url] = photo_img
            return photo_img
            
        except Exception as e:
            print(f"[LOG] ERROR creating placeholder image: {e}")
            # If everything fails, create a basic colored rectangle
            img = Image.new('RGBA', size, color='#FF4136')
            photo_img = ImageTk.PhotoImage(img)
            if url:
                self.images[url] = photo_img
            return photo_img

    def create_book_widget(self, parent, app_data, row, col):
        """Create a widget for a single book."""
        # Book frame
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=col, padx=5, pady=5)
        
        # Load cover image with loading indicator
        loading_placeholder = self.create_placeholder_image(size=(150, 200))
        cover_label = tk.Label(frame, image=loading_placeholder, bg="#1E1E1E")
        cover_label.pack()
        
        # Update label with actual image
        def update_image():
            try:
                cover_image = self.get_cached_image(app_data["coverimageurl"], size=(150, 200))
                if cover_image:
                    cover_label.configure(image=cover_image)
                    cover_label.image = cover_image  # Keep a reference
            except Exception as e:
                print(f"[LOG] Error updating image: {e}")
        
        # Schedule image loading
        self.master.after(10, update_image)
        
        # Book information
        info_frame = ttk.Frame(frame, style='Dark.TFrame')
        info_frame.pack(fill=tk.X, pady=(5, 5))
        
        # Book name
        name_label = tk.Label(
            info_frame,
            text=app_data["name"],
            bg="#1E1E1E",
            fg="white",
            wraplength=150,
            justify=tk.CENTER
        )
        name_label.pack()
        
        # Publisher info
        publisher_label = tk.Label(
            info_frame,
            text=app_data["publisher"],
            bg="#1E1E1E",
            fg="gray",
            font=('Arial', 8),
            wraplength=150
        )
        publisher_label.pack()
        
        # Download button
        button_frame = ttk.Frame(frame, style='Red.TFrame')
        button_frame.pack(fill=tk.X)
        
        download_btn = tk.Button(
            button_frame,
                               text="İNDİR",
            bg="#FF4136",
            fg="white",
                               font=('Arial', 10, 'bold'),
                               relief=tk.FLAT,
            command=lambda: self.download_app(app_data)
        )
        download_btn.pack(fill=tk.X)

    def display_books(self):
        """Display books organized by categories."""
        print("[LOG] Starting to display books")
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Extract unique categories from data
        categories = {'5': [], '6': [], '7': []}  # Initialize all categories
        all_category_books = []  # Store books with 'all' category
        
        print("[LOG] Processing books and their categories:")
        for book in self.data:
            category = str(book.get('category')).strip()  # Convert to string and strip whitespace
            print(f"[LOG] Book: {book['name']}, Category: '{category}'")
            
            if category.lower() == 'all':
                # Add this book to all categories
                all_category_books.append(book)
            elif category in categories:
                categories[category].append(book)
        
        # Add 'all' category books to each category
        for category in categories:
            categories[category].extend(all_category_books)
        
        # Sort categories numerically
        sorted_categories = sorted(categories.keys(), key=lambda x: int(x))
        print(f"[LOG] Found categories: {sorted_categories}")
        
        # Create category sections
        row = 0
        for category in sorted_categories:
            if categories[category]:
                print(f"[LOG] Creating section for category: {category}")
                
                # Books container for this category
                books_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
                books_frame.grid(row=row, column=0, sticky='ew', padx=20)
                
                # Display books horizontally
                for i, book in enumerate(categories[category]):
                    print(f"[LOG] Adding book {book['name']} to category {category}")
                    self.create_book_widget(books_frame, book, 0, i)
                
                # Category number below books
                category_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
                category_frame.grid(row=row + 1, column=0, sticky='ew', pady=(10, 0))
                
                # Large category number
                category_label = ttk.Label(
                    category_frame,
                    text=category,
                    style="Category.TLabel"
                )
                category_label.pack(side=tk.LEFT, padx=20)
                
                # Add separator (using tk.Frame for separator)
                separator = tk.Frame(self.content_frame, height=2, bg='white')
                separator.grid(row=row + 2, column=0, sticky='ew', pady=10)
                
                row += 3
        
        # Update scrollregion after adding all content
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def download_app(self, app_data):
        """Handle the download and activation process for a book."""
        try:
            url = app_data["downloadurl"]
            unlock_key = app_data["unlockkey"]
            print(f"[LOG] Starting download process for: {app_data['name']}")
            print(f"[LOG] Publisher: {app_data['publisher']}")
            print(f"[LOG] Category: {app_data['category']}")
            
            # Handle site:// URLs
            if url.startswith("site://"):
                actual_url = url[7:]
                print(f"[LOG] Opening browser URL: {actual_url}")
                webbrowser.open(actual_url)
                return
            
            # Handle activation key
            if unlock_key.lower() != "none":
                pyperclip.copy(unlock_key)
                print(f"[LOG] Copied activation key to clipboard: {unlock_key}")
            
            # Download process
            print(f"[LOG] Downloading from URL: {url}")
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                # Prepare filename
                original_filename = url.split('/')[-1]
                base_name, extension = os.path.splitext(original_filename)
                new_filename = f"{base_name}_{unlock_key}{extension}" if unlock_key.lower() != "none" else original_filename
                filename = os.path.join(self.download_folder, new_filename)
                
                print(f"[LOG] Saving file as: {filename}")
                
                # Download with progress tracking
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            print(f"[LOG] Download progress: {downloaded}/{total_size} bytes")
                
                print("[LOG] Download completed successfully")
                
                # Open the file
                print(f"[LOG] Attempting to open file: {filename}")
                try:
                    os.startfile(filename)
                except Exception as e:
                    print(f"[LOG] Could not open file directly: {e}")
                    print(f"[LOG] Opening containing folder instead")
                os.startfile(self.download_folder)
            else:
                error_msg = f"Download failed with status code: {response.status_code}"
                print(f"[LOG] ERROR: {error_msg}")
                messagebox.showerror("Error", error_msg)
            
        except Exception as e:
            error_msg = f"An error occurred while downloading: {e}"
            print(f"[LOG] EXCEPTION: {error_msg}")
            messagebox.showerror("Error", error_msg)

    def load_data(self):
        try:
            print("[LOG] Starting data load")
            with open(self.data_file, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.data = list(reader)
                print(f"[LOG] Loaded {len(self.data)} items from data file")
                
                print("[LOG] Displaying books")
                self.display_books()
        except FileNotFoundError:
            error_msg = f"Data file '{self.data_file}' not found"
            print(f"[LOG] ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"An error occurred while loading data: {e}"
            print(f"[LOG] EXCEPTION: {error_msg}")
            messagebox.showerror("Error", error_msg)

    def check_data_file(self):
        """Check if data.csv exists, download it if not, or compare with GitHub version if it exists"""
        try:
            print("[LOG] Checking data file")
            
            # Check if local file exists first
            if not os.path.exists(self.data_file):
                print("[LOG] Data file not found locally")
                try:
                    # Add timeout to prevent hanging indefinitely
                    print("[LOG] Attempting to download from GitHub with timeout")
                    response = requests.get(self.github_data_url, timeout=10)
                    
                    if response.status_code == 200:
                        with open(self.data_file, "w", encoding="utf-8") as file:
                            file.write(response.text)
                        print("[LOG] Data file successfully downloaded")
                    else:
                        print(f"[LOG] Failed to download: HTTP {response.status_code}")
                        messagebox.showerror("Error", f"Failed to download data file: {response.status_code}")
                        # Create empty data file to prevent future hanging
                        with open(self.data_file, "w", encoding="utf-8") as file:
                            file.write("name,downloadurl,unlockkey,category,publisher,coverimageurl\n")
                except requests.exceptions.Timeout:
                    print("[LOG] GitHub request timed out")
                    messagebox.showerror("Error", "Connection to GitHub timed out. Using local data if available.")
                    # Create empty data file to prevent future hanging
                    with open(self.data_file, "w", encoding="utf-8") as file:
                        file.write("name,downloadurl,unlockkey,category,publisher,coverimageurl\n")
                except Exception as e:
                    print(f"[LOG] Exception during download: {e}")
                    messagebox.showerror("Error", f"Error downloading data: {e}")
                    # Create empty data file to prevent future hanging
                    with open(self.data_file, "w", encoding="utf-8") as file:
                        file.write("name,downloadurl,unlockkey,category,publisher,coverimageurl\n")
            else:
                print("[LOG] Data file exists locally, checking for updates")
                try:
                    # Add timeout to prevent hanging indefinitely
                    response = requests.get(self.github_data_url, timeout=10)
                    
                    if response.status_code == 200:
                        github_content = response.text
                        
                        with open(self.data_file, "r", encoding="utf-8") as file:
                            local_content = file.read()
                        
                        # Compare the files
                        if local_content != github_content:
                            print("[LOG] Local data file differs from GitHub version")
                            if messagebox.askyesno("Update Available", 
                                                  "A new version of the data file is available on GitHub. Would you like to update?"):
                                with open(self.data_file, "w", encoding="utf-8") as file:
                                    file.write(github_content)
                                print("[LOG] Data file updated from GitHub")
                        else:
                            print("[LOG] Data file is up to date")
                    else:
                        print(f"[LOG] Failed to check for updates: HTTP {response.status_code}")
                        messagebox.showwarning("Warning", "Failed to check for data file updates. Using existing data.")
                except requests.exceptions.Timeout:
                    print("[LOG] GitHub request timed out")
                    messagebox.showwarning("Warning", "Connection to GitHub timed out. Using existing data.")
                except Exception as e:
                    print(f"[LOG] Exception checking for updates: {e}")
                    messagebox.showwarning("Warning", f"Error checking for updates: {e}. Using existing data.")
        except Exception as e:
            error_msg = f"An error occurred in check_data_file: {e}"
            print(f"[LOG] CRITICAL ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()
