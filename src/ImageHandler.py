import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import shutil
import re
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

class ImageGenerator:
    def __init__(self, csv_path, output_dir, font_path="arialbd.ttf", linux_mode=False):
        # Initialize paths and fonts
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.font_path = font_path
        self.linux_mode = linux_mode

        # Load fonts
        try:
            if self.linux_mode:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                self.font_player = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            else:
                self.font = ImageFont.truetype(self.font_path, 30)
                self.font_player = ImageFont.truetype(self.font_path, 24)
        except IOError:
            print("Font file not found, using default font.")
            self.font = ImageFont.load_default()
            self.font_player = ImageFont.load_default()

        # Define color mapping
        self.colors = {
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'yellow': (255, 255, 0),
            'blue': (0, 0, 255),
            'brown': (139, 69, 19),
            'green': (0, 255, 0),
            'purple': (128, 0, 128),
            'cyan': (0, 255, 255),
            'black': (0, 0, 0)
        }

        # Row color assignments
        self.row_colors = {
            'first': 'white',
            'second': ['red', 'red', 'yellow', 'yellow', 'blue'],
            'third': ['brown', 'brown', 'green', 'green', 'purple', 'cyan'],
            'fourth': 'white'
        }

        # Prepare the output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

        # Load CSV data
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
            print(f"Loaded CSV with {len(self.df)} rows.")
        else:
            print(f"CSV file not found: {self.csv_path}")
            self.df = pd.DataFrame()

    def format_value(self, value, column):
        """Format values based on column type (handle numeric and special cases)."""
        try:
            # Handle "Hands" separately (remove commas, divide by 1000)
            if column == "Hands":
                if isinstance(value, str):
                    value = value.replace(",", "")
                value = float(value) / 1000
                return f"{value:.1f}"  # Format as thousands with 1 decimal

            # Handle other numeric columns
            if isinstance(value, str):
                value = value.replace(",", "").replace("%", "").strip()
            value = float(value)

            if column == "4Bet+ Ratio":
                return f"{value:.1f}"  # One decimal for ratios
            else:
                return str(round(value))  # Default: round to whole number

        except (ValueError, TypeError):
            return str(value)  # Fallback for non-numeric values

    def sanitize_filename(self, player_name):
        """Sanitize player name to be a valid filename."""
        return re.sub(r'[<>:"/\\|?*]', '_', player_name)

    def generate_image(self, row):
        """Generate an image based on the player row data."""
        print(f"Generating image for player: {row['Player']}")

        # Create blank black image
        img = Image.new('RGB', (310, 165), color=self.colors['black'])
        draw = ImageDraw.Draw(img)

        # First row: RFI stats in white
        first_row = ["RFI (EP)", "RFI (MP)", "RFI (CO)", "RFI (BU)", "RFI (SB)"]
        y_pos = 10
        x_pos = 10
        for i, col in enumerate(first_row):
            value = self.format_value(row[col], col)
            draw.text((x_pos, y_pos), value, fill=self.colors[self.row_colors['first']], font=self.font)
            x_pos += len(value) * 10 + 20  # Adjust the position for a smaller space after delimiter
            if i < len(first_row) - 1:
                # Add delimiter between values
                draw.text((x_pos - 10, y_pos), " / ", fill=self.colors[self.row_colors['first']], font=self.font)
                x_pos += 10  # Adjust position after delimiter

        # Second row: VPIP, PFR in red, 3Bet PF, 2Bet PF & Fold in yellow, 4Bet+ Ratio in blue
        second_row = ["VPIP", "PFR", "3Bet PF", "2Bet PF & Fold", "4Bet+ Ratio"]
        y_pos = 50
        x_pos = 10
        for i, col in enumerate(second_row):
            value = self.format_value(row[col], col)
            draw.text((x_pos, y_pos), value, fill=self.colors[self.row_colors['second'][i]], font=self.font)
            x_pos += len(value) * 10 + 20  # Adjust the position for a smaller space after delimiter
            if i < len(second_row) - 1:
                # Add delimiter between values
                draw.text((x_pos - 10, y_pos), " / ", fill=self.colors[self.row_colors['second'][i]], font=self.font)
                x_pos += 10  # Adjust position after delimiter

        # Third row: CBet stats in brown, green, purple, cyan
        third_row = ["CBet F", "CBet T", "Fold to F Float", "Fold to T Float", "CBet F & Fold", "RCp XFf OOP"]
        y_pos = 90
        x_pos = 10
        for i, col in enumerate(third_row):
            value = self.format_value(row[col], col)
            draw.text((x_pos, y_pos), value, fill=self.colors[self.row_colors['third'][i]], font=self.font)
            x_pos += len(value) * 10 + 20  # Adjust the position for a smaller space after delimiter
            if i < len(third_row) - 1:
                # Add delimiter between values
                draw.text((x_pos - 10, y_pos), " / ", fill=self.colors[self.row_colors['third'][i]], font=self.font)
                x_pos += 10  # Adjust position after delimiter

        # Fourth row: Player and Hands in white
        fourth_row = ["Player", "Hands"]
        y_pos = 130
        x_pos = 10
        for i, col in enumerate(fourth_row):
            value = self.format_value(row[col], col)
            draw.text((x_pos, y_pos), value, fill=self.colors[self.row_colors['fourth']], font=self.font_player)
            x_pos += len(value) * 10 + 90  # Adjust the position for a smaller space after delimiter

        draw.rectangle(
            [(0, 0), (img.width - 1, img.height - 1)],
            outline=self.colors['white'],
            width=2  # thickness of the frame
        )

        # Sanitize player name and save the image with player's name as filename
        player_name = self.sanitize_filename(row["Player"])
        img.save(os.path.join(self.output_dir, f"{player_name}.png"))
        print(f"Image saved as: {player_name}.png")

    def generate_images(self):
        """Generate images for all players in the CSV."""
        if self.df.empty:
            print("No data to generate images.")
            return

        for _, row in self.df.iterrows():
            self.generate_image(row)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Generator")

        # Initialize variables
        self.image_handler = None
        self.checkboxes = []
        self.selected = {}

        # Determine the base directory (where the .exe is located)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Use the paths relative to base_dir
        self.csv_path = os.path.join(base_dir, "ReportExport.csv")
        self.output_dir = os.path.join(base_dir, "images")

        self.create_widgets()

    def create_widgets(self):
        """Create and place widgets for the GUI."""
        # Add Linux mode checkbox
        self.linux_mode_var = tk.BooleanVar()
        self.linux_checkbox = tk.Checkbutton(self.root, text="Linux mode", variable=self.linux_mode_var)
        self.linux_checkbox.pack(side="bottom", pady=2)

        # Generate Images button with smaller font and bottom position
        self.generate_button = tk.Button(self.root, text="Generate Images", command=self.generate_images,
                                         font=("Arial", 9))
        self.generate_button.pack(side="bottom", pady=5)

        # Frame for checkboxes and scrollable area
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.scroll_y = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scroll_y.set)

        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        self.checkbox_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")

        # Search entry to filter players
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(pady=10)
        self.search_var.trace_add('write', self.update_checkboxes)

        # Button to show selected images
        self.show_button = tk.Button(self.root, text="Show Selected Players", command=self.show_selected_images)
        self.show_button.pack(pady=10)

        # Button to clear all selections
        self.clear_button = tk.Button(self.root, text="Clear All Selections", command=self.clear_selection)
        self.clear_button.pack(pady=10)

        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Number of columns selection
        column_frame = tk.Frame(self.root)
        column_frame.pack()

        tk.Label(column_frame, text="Number of columns:").pack(side="left")

        self.num_columns_var = tk.IntVar(value=2)
        tk.Spinbox(column_frame, from_=1, to=10, textvariable=self.num_columns_var, width=5).pack(side="left")

    def generate_images(self):
        """Generate images and display player names."""
        if os.path.exists(self.csv_path):
            # Recreate output_dir by deleting it first if it exists
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir)

            self.image_handler = ImageGenerator(self.csv_path, self.output_dir)
            self.image_handler.generate_images()

            # Clear previous selections
            self.checkbox_frame.destroy()
            self.checkbox_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")

            # Get player names from generated images
            self.players = [f[:-4] for f in os.listdir(self.output_dir) if f.endswith(".png")]
            self.selected = {}

            # Update the checkboxes with players
            self.update_checkboxes()

            messagebox.showinfo("Success", "Images generated successfully!")
        else:
            messagebox.showerror("Error", "CSV file not found.")

    def update_checkboxes(self, *args):
        """Update the checkboxes based on the search term."""
        # Clear existing checkboxes
        for cb in self.checkboxes:
            cb.destroy()
        self.checkboxes.clear()

        search_term = self.search_var.get().lower()

        for player in self.players:
            if search_term in player.lower():
                var = tk.BooleanVar()
                # Preserve previous state
                if player in self.selected and self.selected[player].get():
                    var.set(True)
                cb = tk.Checkbutton(self.checkbox_frame, text=player, variable=var)
                cb.pack(anchor="w")
                self.selected[player] = var
                self.checkboxes.append(cb)

        # Update the scroll region to accommodate the new checkboxes
        self.checkbox_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def show_selected_images(self):
        """Display selected images in a new window."""
        selected_players = [player for player, var in self.selected.items() if var.get()]

        if not selected_players:
            messagebox.showwarning("No selection", "Please select at least one player.")
            return

        display_window = tk.Toplevel(self.root)
        display_window.title("Selected Players")

        display_window.images = []  # Keep image references to avoid garbage collection

        num_columns = self.num_columns_var.get()

        for i, player in enumerate(selected_players):
            image_path = os.path.join(self.output_dir, f"{player}.png")
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            display_window.images.append(photo)

            label = tk.Label(display_window, image=photo)
            label.grid(row=i // num_columns, column=i % num_columns, padx=0, pady=0)

    def clear_selection(self):
        """Clear all selections and uncheck checkboxes."""
        for var in self.selected.values():
            var.set(False)
        self.update_checkboxes()

    def on_mouse_wheel(self, event):
        """Enable scrolling with the mouse wheel."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# Run the Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

