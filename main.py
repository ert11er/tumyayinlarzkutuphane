"""
this program will get the datas from data.csv and show it to the user. it will be a gui interface. if the user clicks one one of them, it will download it and put it into the data folder. it will display the unlock key and when the user clicks the button which is under the displayed unlock key, it will open the downloaded app. it will delete the downloaded app(the app will create its own folder as well but we dont delete that), it will go back to the main menu.

data.csv categories: name,downloadurl,unlockkey,category,publisher,coverimageurl
"""
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

class AppDownloader:
    def __init__(self, master):
        self.master = master
        master.title("E-Kitap App Downloader")

        self.data_file = "data.csv"
        self.download_folder = os.path.join(os.path.dirname(__file__), "data")
        self.data = []
        self.selected_app = None

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Treeview for displaying app list
        self.tree = ttk.Treeview(self.main_frame, columns=("Name", "Category", "Publisher"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Publisher", text="Publisher")
        self.tree.column("Name", width=200)
        self.tree.column("Category", width=100)
        self.tree.column("Publisher", width=150)
        self.tree.bind("<ButtonRelease-1>", self.on_app_select)
        self.tree.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Scrollbar for Treeview
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))

        # Cover Image Label
        self.cover_label = ttk.Label(self.main_frame)
        self.cover_label.grid(row=1, column=0, sticky=(tk.W))

        # Download Button
        self.download_button = ttk.Button(self.main_frame, text="Download", command=self.download_app, state=tk.DISABLED)
        self.download_button.grid(row=1, column=1, sticky=(tk.E))

        # Unlock Key Label
        self.unlock_key_label = ttk.Label(self.main_frame, text="Unlock Key: ")
        self.unlock_key_label.grid(row=2, column=0, sticky=(tk.W))

        # Open App Button
        self.open_app_button = ttk.Button(self.main_frame, text="Open App", command=self.open_app, state=tk.DISABLED)
        self.open_app_button.grid(row=3, column=0, sticky=(tk.W))

        # Back Button
        self.back_button = ttk.Button(self.main_frame, text="Back", command=self.go_back, state=tk.DISABLED)
        self.back_button.grid(row=3, column=1, sticky=(tk.E))

        # Configure row and column weights for resizing
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def load_data(self):
        try:
            with open(self.data_file, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.data = list(reader)
                for app in self.data:
                    self.tree.insert("", tk.END, values=(app["name"], app["category"], app["publisher"]), iid=app["name"])
        except FileNotFoundError:
            messagebox.showerror("Error", f"Data file '{self.data_file}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")

    def on_app_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.selected_app_name = selected_item[0]
            self.selected_app = next((app for app in self.data if app["name"] == self.selected_app_name), None)
            if self.selected_app:
                self.download_button.config(state=tk.NORMAL)
                self.unlock_key_label.config(text=f"Unlock Key: {self.selected_app['unlockkey']}")
                self.load_cover_image(self.selected_app["coverimageurl"])
            else:
                self.download_button.config(state=tk.DISABLED)
                self.unlock_key_label.config(text="Unlock Key: ")
                self.cover_label.config(image="")
                self.cover_label.image = None

    def load_cover_image(self, image_url):
        if not image_url or image_url.strip() == "None":  # Check for empty or "None"
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
                self.open_app_button.config(state=tk.NORMAL)
                self.back_button.config(state=tk.NORMAL)
                self.download_button.config(state=tk.DISABLED)
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Download Error", f"Error downloading {app_name}: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def open_app(self):
        if hasattr(self, "downloaded_app_path") and self.downloaded_app_path:
            try:
                if os.name == 'nt':  # Windows
                    subprocess.Popen([self.downloaded_app_path])
                elif os.name == 'posix':  # macOS or Linux
                    subprocess.Popen(['open', self.downloaded_app_path])
                else:
                    webbrowser.open(self.downloaded_app_path)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while opening the app: {e}")

    def go_back(self):
        if hasattr(self, "downloaded_app_path") and self.downloaded_app_path:
            try:
                os.remove(self.downloaded_app_path)
                self.downloaded_app_path = None
                self.open_app_button.config(state=tk.DISABLED)
                self.back_button.config(state=tk.DISABLED)
                self.unlock_key_label.config(text="Unlock Key: ")
                self.cover_label.config(image="")
                self.cover_label.image = None
                self.tree.selection_remove(self.selected_app_name)
                self.selected_app = None
                self.selected_app_name = None
            except FileNotFoundError:
                messagebox.showerror("Error", "Downloaded app not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while deleting the app: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDownloader(root)
    root.mainloop()

