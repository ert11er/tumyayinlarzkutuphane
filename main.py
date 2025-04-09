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

    def setup_styles(self):
        """Configure ttk styles for widgets."""
        self.style = ttk.Style()
        self.style.configure("Dark.TFrame", background="#1E1E1E")
        self.style.configure("Red.TFrame", background="#FF4136")

    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Create status bar at the bottom
        self.status_frame = ttk.Frame(self.master, style="Dark.TFrame")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Date label
        self.date_label = ttk.Label(
            self.status_frame,
            text="26.03.2025",
            background="#1E1E1E",
            foreground="white",
            font=('Arial', 8)
        )
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        # Version label
        self.version_label = ttk.Label(
            self.status_frame,
            text="PERNUS",
            background="#1E1E1E",
            foreground="white",
            font=('Arial', 8)
        )
        self.version_label.pack(side=tk.RIGHT, padx=10)
        
        # Main scrollable area
        self.canvas = tk.Canvas(self.master, bg='#1E1E1E', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        
        # Books container
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
        """Create a widget for a single book with cover image and download button."""
        # Book frame
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10)
        
        # Load cover image
        cover_image = self.load_cover_image_for_book(app_data["coverimageurl"])
        if cover_image:
            cover_label = ttk.Label(frame, image=cover_image, background="#1E1E1E")
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
        """Display all books in a grid layout."""
        print("[LOG] Starting to display books")
        # Clear existing books
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        print("[LOG] Cleared existing book widgets")
        
        # Clear image references
        self.images = []
        print("[LOG] Cleared image references")

        filtered_data = self.data
        if self.category_filter.get() != "All":
            filtered_data = [app for app in self.data 
                            if app["category"] == self.category_filter.get() 
                            and app["category"] != "all"]
            print(f"[LOG] Filtered books for category: {self.category_filter.get()}")
            print(f"[LOG] Found {len(filtered_data)} books in category")

        # Calculate number of columns
        window_width = self.master.winfo_width()
        num_columns = max(4, window_width // 220)
        print(f"[LOG] Display grid will use {num_columns} columns")
        
        # Create book widgets in a grid
        for i, app in enumerate(self.data):
            row = i // num_columns
            col = i % num_columns
            print(f"[LOG] Creating widget for book: {app['name']} at position ({row}, {col})")
            self.create_book_widget(self.content_frame, app, row, col)
        
        print("[LOG] Updating scrollbar configuration")
        self.content_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        print("[LOG] Book display complete")

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
            # Try to get the GitHub version of the file
            print("[LOG] Checking data file")
            response = requests.get(self.github_data_url)
            if response.status_code != 200:
                messagebox.showerror("Error", f"Failed to access GitHub data file: {response.status_code}")
                return
            
            github_content = response.text
            
            # Check if local file exists
            if not os.path.exists(self.data_file):
                # File doesn't exist, download it
                print("[LOG] Data file not found, downloading from GitHub")
                with open(self.data_file, "w", encoding="utf-8") as file:
                    file.write(github_content)
                messagebox.showinfo("Information", "Data file downloaded from GitHub.")
            else:
                # File exists, compare with GitHub version
                print("[LOG] Data file exists, comparing with GitHub version")
                with open(self.data_file, "r", encoding="utf-8") as file:
                    local_content = file.read()
                
                # Compare the files
                if local_content != github_content:
                    # Files are different, ask user if they want to update
                    print("[LOG] Local data file differs from GitHub version")
                    if messagebox.askyesno("Update Available", 
                                          "A new version of the data file is available on GitHub. Would you like to update?"):
                        with open(self.data_file, "w", encoding="utf-8") as file:
                            file.write(github_content)
                        messagebox.showinfo("Information", "Data file updated from GitHub.")
                        print("[LOG] Data file updated from GitHub")
                else:
                    print("[LOG] Data file is up to date")
        except Exception as e:
            error_msg = f"An error occurred while checking data file: {e}"
            print(f"[LOG] ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()
