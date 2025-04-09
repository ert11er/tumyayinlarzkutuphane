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
        self.data_file = "data.csv"
        self.github_data_url = "https://raw.githubusercontent.com/ert11er/tumyayinlarzkutuphane/main/data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.data = []
        self.images = []  # Store references to prevent garbage collection
        self.category_filter = tk.StringVar(value="All")

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
        
        # Main scrollable area
        self.canvas = tk.Canvas(self.master, bg='#1E1E1E', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        
        # Main content frame
        self.content_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event):
        """Update canvas window width when canvas is resized."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def load_cover_image_for_book(self, url, size=(180, 250)):
        try:
            print(f"[LOG] Loading cover image from URL: {url}")
            response = requests.get(url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            self.images.append(photo_img)
            print("[LOG] Successfully loaded and processed cover image")
            return photo_img
        except Exception as e:
            print(f"[LOG] ERROR loading image from {url}: {e}")
            print("[LOG] Creating placeholder image")
            img = Image.new('RGB', size, color='#2E2E2E')
            photo_img = ImageTk.PhotoImage(img)
            self.images.append(photo_img)
            return photo_img

    def create_book_widget(self, parent, app_data, row, col):
        """Create a widget for a single book."""
        # Book frame
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=col, padx=5, pady=5)
        
        # Load cover image
        cover_image = self.load_cover_image_for_book(app_data["coverimageurl"], size=(150, 200))
        if cover_image:
            # Use tk.Label instead of ttk.Label for image display
            cover_label = tk.Label(frame, image=cover_image, bg="#1E1E1E")
            cover_label.pack()
        
        # Red download button banner
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
        
        # Extract unique categories from data, excluding 'all'
        categories = {}
        print("[LOG] Processing books and their categories:")
        for book in self.data:
            category = str(book.get('category')).strip()  # Convert to string and strip whitespace
            print(f"[LOG] Book: {book['name']}, Category: '{category}'")
            if category and category.lower() != 'all':
                if category not in categories:
                    categories[category] = []
                categories[category].append(book)
        
        # Sort categories numerically if possible
        sorted_categories = sorted(categories.keys(), key=lambda x: int(x) if x.isdigit() else x)
        print(f"[LOG] Found categories: {sorted_categories}")
        print(f"[LOG] Number of books per category:")
        for cat in sorted_categories:
            print(f"[LOG] Category {cat}: {len(categories[cat])} books")
        
        # Create category sections
        row = 0
        for category in sorted_categories:
            if categories[category]:
                print(f"[LOG] Creating section for category: {category}")
                # Category header
                category_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
                category_frame.grid(row=row, column=0, sticky='ew', pady=(20, 0))
                
                # Large category number
                category_label = ttk.Label(
                    category_frame,
                    text=category,
                    style="Category.TLabel"
                )
                category_label.pack(side=tk.LEFT, padx=20)
                
                # Books container for this category
                books_frame = ttk.Frame(self.content_frame, style='Dark.TFrame')
                books_frame.grid(row=row + 1, column=0, sticky='ew', padx=20)
                
                # Display books horizontally
                for i, book in enumerate(categories[category]):
                    print(f"[LOG] Adding book {book['name']} to category {category}")
                    self.create_book_widget(books_frame, book, 0, i)
                
                # Add separator (using tk.Frame for separator)
                separator = tk.Frame(self.content_frame, height=2, bg='white')
                separator.grid(row=row + 2, column=0, sticky='ew', pady=10)
                
                row += 3

    def download_app(self, app_data):
        try:
            url = app_data["downloadurl"]
            print(f"[LOG] Attempting to process URL: {url}")
            
            # Check if URL starts with "site://"
            if url.startswith("site://"):
                actual_url = url[7:]
                print(f"[LOG] Opening browser with URL: {actual_url}")
                webbrowser.open(actual_url)
                return
            
            print(f"[LOG] Starting download for: {app_data['name']}")
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                print(f"[LOG] Download request successful with status code: {response.status_code}")
                
                # Create download folder if it doesn't exist
                os.makedirs(self.download_folder, exist_ok=True)
                print(f"[LOG] Download folder verified: {self.download_folder}")
                
                # Get filename from URL
                filename = os.path.join(self.download_folder, url.split('/')[-1])
                print(f"[LOG] Saving file as: {filename}")
                
                # Download the file
                with open(filename, 'wb') as f:
                    print("[LOG] Writing file data...")
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print("[LOG] File write complete")
                
                messagebox.showinfo("Success", f"{app_data['name']} başarıyla indirildi!")
                print(f"[LOG] Success message shown for: {app_data['name']}")
                
                # Open the download folder
                print("[LOG] Opening download folder")
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
                        messagebox.showinfo("Information", "Data file downloaded from GitHub.")
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
                                messagebox.showinfo("Information", "Data file updated from GitHub.")
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
