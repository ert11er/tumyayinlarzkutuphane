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
import pyperclip  # Import pyperclip for clipboard functionality

class AppDownloader:
    def __init__(self, master):
        self.master = master
        master.title("E-Kitap App Downloader")

        self.data_file = "data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.data = []
        self.selected_app = None
        self.category_filter = tk.StringVar(value="All")  # Default to showing all categories

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Category Filter
        self.category_label = ttk.Label(self.main_frame, text="Category:")
        self.category_label.grid(row=0, column=0, sticky=(tk.W))

        self.category_options = ["All"]  # Initialize with "All"
        self.category_combobox = ttk.Combobox(self.main_frame, textvariable=self.category_filter, values=self.category_options, state="readonly")
        self.category_combobox.grid(row=0, column=1, sticky=(tk.W))
        self.category_combobox.bind("<<ComboboxSelected>>", self.filter_by_category)

        # Bookshelf Frame
        self.bookshelf_frame = ttk.Frame(self.main_frame)
        self.bookshelf_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Canvas for Bookshelf
        self.bookshelf_canvas = tk.Canvas(self.bookshelf_frame, bg="#D2B48C")  # Light brown for bookshelf
        self.bookshelf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for Canvas
        self.bookshelf_scrollbar = ttk.Scrollbar(self.bookshelf_frame, orient="vertical", command=self.bookshelf_canvas.yview)
        self.bookshelf_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.bookshelf_canvas.configure(yscrollcommand=self.bookshelf_scrollbar.set)
        self.bookshelf_canvas.bind("<Configure>", lambda e: self.bookshelf_canvas.configure(scrollregion=self.bookshelf_canvas.bbox("all")))

        # Inner Frame for Books
        self.books_frame = ttk.Frame(self.bookshelf_canvas)
        self.bookshelf_canvas.create_window((0, 0), window=self.books_frame, anchor="nw")

        # Configure row and column weights for resizing
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def load_data(self):
        try:
            with open(self.data_file, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.data = list(reader)

                # Update category options
                self.category_options.extend(sorted(list(set(app["category"] for app in self.data))))
                self.category_combobox.config(values=self.category_options)

                self.display_books()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Data file '{self.data_file}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")

    def display_books(self):
        # Clear existing books
        for widget in self.books_frame.winfo_children():
            widget.destroy()

        filtered_data = self.data
        if self.category_filter.get() != "All":
            filtered_data = [app for app in self.data if app["category"] == self.category_filter.get()]

        row, col = 0, 0
        for app in filtered_data:
            book_frame = ttk.Frame(self.books_frame, padding=5)
            book_frame.grid(row=row, column=col, padx=5, pady=5)

            # Load and display cover image
            cover_image = self.load_cover_image_for_book(app["coverimageurl"])
            if cover_image:
                cover_label = ttk.Label(book_frame, image=cover_image)
                cover_label.image = cover_image
                cover_label.pack()

            # Book name label
            name_label = ttk.Label(book_frame, text=app["name"], wraplength=100, justify="center")
            name_label.pack()

            # Download and Open Button
            download_open_button = ttk.Button(book_frame, text="Open", command=lambda a=app: self.download_and_open(a))
            download_open_button.pack()

            col += 1
            if col > 4:  # Adjust number of books per row
                col = 0
                row += 1

        self.books_frame.update_idletasks()
        self.bookshelf_canvas.configure(scrollregion=self.bookshelf_canvas.bbox("all"))

    def load_cover_image_for_book(self, image_url):
        if not image_url or image_url.strip() == "None":
            return None

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((100, 100))  # Smaller thumbnails for bookshelf
            photo = ImageTk.PhotoImage(image)
            return photo
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
            return None
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def filter_by_category(self, event):
        self.display_books()

    def download_and_open(self, app):
        self.selected_app = app
        self.download_app()

    def load_cover_image(self, image_url):
        if not image_url or image_url.strip() == "None" or image_url.strip() == "none":  # Check for empty or "None"
            self.cover_label.config(image="")  # Clear the image label
            self.cover_label.image = None  # Remove reference
            return  # Exit the function early

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image_width, image_height = image.size
            if image_width > 150 or image_height > 150:
                image.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(image)

            self.cover_label.config(image=photo)
            self.cover_label.image = photo
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
            self.cover_label.config(image="")
            self.cover_label.image = None
        except Exception as e:
            print(f"Error loading image: {e}")
            self.cover_label.config(image="")
            self.cover_label.image = None

    def download_app(self):
        if self.selected_app:
            download_url = self.selected_app["downloadurl"]
            app_name = self.selected_app["name"]
            file_extension = os.path.splitext(download_url)[1]
            download_path = os.path.join(self.download_folder, f"{app_name}{file_extension}")

            if not os.path.exists(self.download_folder):
                os.makedirs(self.download_folder)

            try:
                response = requests.get(download_url, stream=True)
                response.raise_for_status()

                with open(download_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                messagebox.showinfo("Download Complete", f"{app_name} downloaded successfully!")
                self.downloaded_app_path = download_path
                self.open_app()
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Download Error", f"Error downloading {app_name}: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def open_app(self):
        if hasattr(self, "downloaded_app_path") and self.downloaded_app_path:
            try:
                # Copy unlock key to clipboard
                pyperclip.copy(self.selected_app["unlockkey"])

                if os.name == 'nt':  # Windows
                    subprocess.Popen([self.downloaded_app_path])
                elif os.name == 'posix':  # macOS or Linux
                    subprocess.Popen(['open', self.downloaded_app_path])
                else:
                    webbrowser.open(self.downloaded_app_path)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while opening the app: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()
