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
    def __init__(self, master):
        self.master = master
        master.title("TÜM Yayinlar Z-Kütüphane")
        
        # Configure the window
        master.configure(bg='#1E1E1E')  # Dark background
        master.state('zoomed')  # Make window maximized
        
        self.data_file = "data.csv"
        self.github_data_url = "https://raw.githubusercontent.com/ert11er/tumyayinlarzkutuphane/main/data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.data = []
        self.selected_app = None
        self.category_filter = tk.StringVar(value="All")
        self.images = []  # Store references to all images
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Red.TButton", 
                           background="#FF4136", 
                           foreground="white",
                           padding=10)
        self.style.configure("Dark.TFrame", background="#1E1E1E")
        
        self.create_widgets()
        self.check_data_file()
        self.load_data()

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
        # Main Frame
        self.main_frame = ttk.Frame(self.master, style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create page navigation frame
        self.nav_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Home button
        self.home_button = tk.Button(self.nav_frame, 
                                   text="⌂", 
                                   font=('Arial', 14), 
                                   bg="#1E1E1E", 
                                   fg="white",
                                   relief=tk.FLAT,
                                   command=lambda: self.select_category("All"))
        self.home_button.pack(side=tk.LEFT, padx=5)
        
        # Category tabs (dynamic categories)
        self.tab_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.tab_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.category_buttons = []

        # Create canvas with scrollbar for book display
        self.canvas_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='#1E1E1E', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.books_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.books_frame, anchor="nw")
        
        # Configure scroll region when books frame changes
        self.books_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Status bar showing current time and date
        self.status_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, 
                                    text="26.03.2025",
                                    foreground="white", 
                                    background="#1E1E1E",
                                    font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT)
        
        self.version_label = ttk.Label(self.status_frame, 
                                     text="PERNUS",
                                     foreground="white", 
                                     background="#1E1E1E",
                                     font=('Arial', 8))
        self.version_label.pack(side=tk.RIGHT)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the width of the window inside the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_cover_image_for_book(self, url, size=(180, 250)):
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            self.images.append(photo_img)  # Keep a reference to prevent garbage collection
            return photo_img
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            # Create a default placeholder image
            img = Image.new('RGB', size, color='#2E2E2E')
            photo_img = ImageTk.PhotoImage(img)
            self.images.append(photo_img)
            return photo_img

    def create_book_widget(self, parent, app_data, row, col):
        # Main frame for the book item
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=col, padx=10, pady=10)
        
        # Load and display cover image
        cover_image = self.load_cover_image_for_book(app_data["coverimageurl"])
        if cover_image:
            cover_label = ttk.Label(frame, image=cover_image, background="#1E1E1E")
            cover_label.pack(side=tk.TOP, pady=0)
        
        # Download button with red background (positioned at the bottom of the book cover)
        download_btn = tk.Button(frame,
                               text="İNDİR",
                               bg="#FF4136",  # Red background
                               fg="white",    # White text
                               font=('Arial', 10, 'bold'),
                               relief=tk.FLAT,
                               padx=10,
                               pady=2,
                               command=lambda: self.download_app(app_data))
        download_btn.pack(fill=tk.X)

    def display_books(self):
        # Clear existing books
        for widget in self.books_frame.winfo_children():
            widget.destroy()
        
        # Clear image references
        self.images = []

        filtered_data = self.data
        if self.category_filter.get() != "All":
            filtered_data = [app for app in self.data if app["category"] == self.category_filter.get()]

        # Calculate number of columns based on window width
        window_width = self.master.winfo_width()
        num_columns = max(4, window_width // 220)  # Adjust columns based on window width
        
        # Create book widgets in a grid
        for i, app in enumerate(filtered_data):
            row = i // num_columns
            col = i % num_columns
            self.create_book_widget(self.books_frame, app, row, col)
        
        # Update the scrollbar
        self.books_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

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
        # Clear previous bookshelves if any
        for widget in self.tab_frame.winfo_children():
            widget.destroy()

        # Get unique categories from data
        categories = sorted(list({app["category"] for app in self.data}))

        # Create a bookshelf for each category
        for category in categories:
            # Bookshelf label
            shelf_label = ttk.Label(self.tab_frame,
                                   text=f"{category}. Sınıf",
                                   background="#1E1E1E",
                                   foreground="white",
                                   font=('Arial', 14, 'bold'))
            shelf_label.pack(fill=tk.X, pady=(10, 5))

            # Display books for the category
            self.display_books_for_category(category)

    def display_books_for_category(self, category):
        # Filter books by category
        filtered_data = [app for app in self.data if app["category"] == category]

        # Create a frame for the books
        books_frame = ttk.Frame(self.tab_frame, style='Dark.TFrame')
        books_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Display each book in the category
        for i, app in enumerate(filtered_data):
            self.create_book_widget(books_frame, app, row=0, col=i)

    def download_app(self, app_data):
        try:
            url = app_data["downloadurl"]
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                # Create download folder if it doesn't exist
                os.makedirs(self.download_folder, exist_ok=True)
                
                # Get filename from URL
                filename = os.path.join(self.download_folder, url.split('/')[-1])
                
                # Download the file
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                messagebox.showinfo("Success", f"{app_data['name']} başarıyla indirildi!")
                
                # Open the download folder
                os.startfile(self.download_folder)
            else:
                messagebox.showerror("Error", f"Download failed with status code: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while downloading: {e}")

    def load_data(self):
        try:
            with open(self.data_file, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.data = list(reader)
                
                # Update category tabs
                self.update_category_tabs()
                
                # Display all books initially
                self.select_category("All")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Data file '{self.data_file}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()
