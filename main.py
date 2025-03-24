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

class AppDownloader:
    def __init__(self, master):
        self.master = master
        master.title("TÜM Yayınları Z-Kütüphane")
        
        # Configure the window
        master.configure(bg='#1E1E1E')  # Dark background
        master.state('zoomed')  # Make window maximized
        
        self.data_file = "data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.data = []
        self.selected_app = None
        self.category_filter = tk.StringVar(value="All")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Red.TButton", 
                           background="#FF4136", 
                           foreground="white",
                           padding=10)
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Category Filter as bookshelf
        self.category_frame = ttk.Frame(self.main_frame)
        self.category_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create category buttons
        self.category_buttons = []
        categories = ["All"] + sorted(list(set(str(i) for i in range(5, 9))))  # 5,6,7,8
        for category in categories:
            btn = tk.Button(self.category_frame,
                          text=f"{category}. Sınıf" if category != "All" else "Tümü",
                          bg="#1E1E1E",
                          fg="white",
                          font=('Arial', 12, 'bold'),
                          relief=tk.FLAT,
                          padx=20,
                          pady=10,
                          command=lambda c=category: self.select_category(c))
            btn.pack(side=tk.LEFT, padx=10)
            self.category_buttons.append(btn)

        # Create canvas with scrollbar
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='#1E1E1E')
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

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the width of the window inside the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_cover_image_for_book(self, url, size=(200, 280)):
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            return None

    def create_book_widget(self, parent, app_data, row, col):
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=col, padx=20, pady=20)
        
        # Load and display cover image
        cover_image = self.load_cover_image_for_book(app_data["coverimageurl"])
        if cover_image:
            cover_label = ttk.Label(frame, image=cover_image)
            cover_label.image = cover_image  # Keep a reference
            cover_label.pack(pady=(0, 10))
        
        # Download button with red background
        download_btn = tk.Button(frame,
                               text="İNDİR",
                               bg="#FF4136",  # Red background
                               fg="white",    # White text
                               font=('Arial', 10, 'bold'),
                               relief=tk.FLAT,
                               command=lambda: self.download_app(app_data))
        download_btn.pack(fill=tk.X)

    def display_books(self):
        # Clear existing books
        for widget in self.books_frame.winfo_children():
            widget.destroy()

        filtered_data = self.data
        if self.category_filter.get() != "All":
            filtered_data = [app for app in self.data if app["category"] == self.category_filter.get()]

        # Calculate number of columns based on window width
        window_width = self.master.winfo_width()
        num_columns = max(3, window_width // 300)  # At least 3 columns, or more based on width

        # Create book widgets in a grid
        for i, app in enumerate(filtered_data):
            row = i // num_columns
            col = i % num_columns
            self.create_book_widget(self.books_frame, app, row, col)

    def select_category(self, category):
        # Update button colors
        for btn in self.category_buttons:
            if btn['text'] == (f"{category}. Sınıf" if category != "All" else "Tümü"):
                btn.configure(bg="#FF4136")  # Selected category
            else:
                btn.configure(bg="#1E1E1E")  # Unselected categories
        
        self.category_filter.set(category)
        self.display_books()

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
                
                # Update category options
                categories = sorted(list(set(app["category"] for app in self.data)))
                self.category_options = ["All"] + categories
                self.select_category("All")
                
                self.display_books()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Data file '{self.data_file}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()
