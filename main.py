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
        
        # Create scrollable main content area
        self.canvas = tk.Canvas(self.master, bg='#1E1E1E', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw", width=self.master.winfo_width())
        
        # Configure canvas scrolling
        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def initialize_variables(self):
        """Initialize instance variables and constants."""
        self.data_file = "data.csv"
        self.github_data_url = "https://raw.githubusercontent.com/ert11er/tumyayinlarzkutuphane/main/data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.data = []
        self.images = []  # Store references to prevent garbage collection
        self.category_filter = tk.StringVar(value="All")
        self.category_buttons = []

    def setup_styles(self):
        """Configure ttk styles for widgets."""
        self.style = ttk.Style()
        self.style.configure("Dark.TFrame", background="#1E1E1E")
        self.style.configure("Red.TFrame", background="#FF4136")
        self.style.configure("Separator.TFrame", background="white")

    def check_data_file(self):
        """Check if data.csv exists, download it if not, or compare with GitHub version if it exists"""
        try:
            # Try to get the GitHub version of the file
            response = requests.get(self.github_data_url)
            if response.status_code != 200:
                messagebox.showerror("Error", f"Failed to access GitHub data file: {response.status_code}")
                return
            
            github_content = response.text
            
            # Check if local file exists
            if not os.path.exists(self.data_file):
                # File doesn't exist, download it
                with open(self.data_file, "w", encoding="utf-8") as file:
                    file.write(github_content)
                messagebox.showinfo("Information", "Data file downloaded from GitHub.")
            else:
                # File exists, compare with GitHub version
                with open(self.data_file, "r", encoding="utf-8") as file:
                    local_content = file.read()
                
                # Compare the files
                if local_content != github_content:
                    # Files are different, ask user if they want to update
                    if messagebox.askyesno("Update Available", 
                                          "A new version of the data file is available on GitHub. Would you like to update?"):
                        with open(self.data_file, "w", encoding="utf-8") as file:
                            file.write(github_content)
                        messagebox.showinfo("Information", "Data file updated from GitHub.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while checking data file: {e}")

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
        self.content = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw", width=self.master.winfo_width())
        
        # Configure canvas scrolling
        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event):
        # Update the width of the window inside the canvas
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
        # Book item container
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='ne')
        
        # Load cover image
        cover_image = self.load_cover_image_for_book(app_data["coverimageurl"])
        if cover_image:
            cover_label = ttk.Label(frame, image=cover_image, background="#1E1E1E")
            cover_label.pack()
        
        # Red download button
        download_btn = tk.Button(
            frame,
            text="İNDİR",
            bg="#FF4136",
            fg="white",
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            width=20,  # Make button wider
            command=lambda: self.download_app(app_data)
        )
        download_btn.pack(fill=tk.X, pady=(5, 0))

    def display_books(self):
        print("[LOG] Starting to display books")
        # Clear existing books
        for widget in self.content.winfo_children():
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
        
        # Create book widgets
        for i, app in enumerate(filtered_data):
            row = i // num_columns
            col = i % num_columns
            print(f"[LOG] Creating widget for book: {app['name']} at position ({row}, {col})")
            self.create_book_widget(self.content, app, row, col)
        
        print("[LOG] Updating scrollbar configuration")
        self.content.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        print("[LOG] Book display complete")

    def select_category(self, category):
        # Reset all buttons to default style
        for btn in self.category_buttons:
            btn.configure(bg="#1E1E1E", fg="white")
        
        # Highlight the selected button
        if category != "All":
            for btn in self.category_buttons:
                if btn["text"] == category:
                    btn.configure(bg="#FF4136", fg="white")
        
        self.category_filter.set(category)
        self.display_books()

    def update_category_tabs(self):
        # Clear previous content
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Get unique categories from data (excluding 'all')
        categories = sorted(list({app["category"] for app in self.data if app["category"] != "all"}))
        
        # Create category sections
        for category in categories:
            # Create category section frame
            section_frame = ttk.Frame(self.content, style='Dark.TFrame')
            section_frame.pack(fill=tk.X, pady=10)
            
            # Left side panel for category and buttons
            left_panel = ttk.Frame(section_frame, style='Dark.TFrame')
            left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
            # Category number (large)
            category_label = ttk.Label(
                left_panel,
                text=category,
                background="#1E1E1E",
                foreground="white",
                font=('Arial', 48, 'bold')
            )
            category_label.pack(anchor='w', pady=(0, 20))
            
            # Get books for this category
            category_books = [app for app in self.data if app["category"] == category]
            
            # INDIR buttons below category number
            buttons_frame = ttk.Frame(left_panel, style='Dark.TFrame')
            buttons_frame.pack(fill=tk.X)
            
            # Create INDIR buttons in the left panel
            for i, book in enumerate(category_books):
                btn = tk.Button(
                    buttons_frame,
                    text="İNDİR",
                    bg="#FF4136",
                    fg="white",
                    font=('Arial', 10, 'bold'),
                    relief=tk.FLAT,
                    command=lambda b=book: self.download_app(b)
                )
                btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
            
            # Right side panel for book displays
            right_panel = ttk.Frame(section_frame, style='Dark.TFrame')
            right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
            
            # Display books in a grid (2 columns)
            for i, book in enumerate(category_books):
                col = i % 2
                row = i // 2
                self.create_book_widget(right_panel, book, row, col)
            
            # Add white separator line at the bottom
            separator = ttk.Frame(section_frame, height=1, style='Separator.TFrame')
            separator.pack(fill=tk.X, pady=(20, 0))

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
                
                print("[LOG] Updating category tabs")
                self.update_category_tabs()
                
                print("[LOG] Setting initial category display to 'All'")
                self.select_category("All")
        except FileNotFoundError:
            error_msg = f"Data file '{self.data_file}' not found"
            print(f"[LOG] ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"An error occurred while loading data: {e}"
            print(f"[LOG] EXCEPTION: {error_msg}")
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()
