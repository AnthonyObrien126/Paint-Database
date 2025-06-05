# Miniature Paint Manager

A desktop GUI application to help hobbyists and painters manage their miniature paint collection with ease. Built using Python, CustomTkinter, and MongoDB, it provides an intuitive interface for tracking paint inventory, searching and sorting paints, exporting data, and identifying missing colors from pasted lists.

## Features

- Add and update paints with quantity tracking
- Filter and sort your paint collection by brand, name, type, or status
- Export your entire paint list to CSV
- Paste a list of paint names to check which you already own
- Fuzzy matching to suggest close matches for missing paints
- Export missing paints from pasted lists to CSV

## Tech Stack

- Python 3.8+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [MongoDB](https://www.mongodb.com/)
- Tkinter and ttk for table view
- CSV export for data portability

## Setup Instructions

1. **Install Python packages**  
   Make sure you have Python 3.8+ installed, then run:
   ```bash
   pip install customtkinter pymongo
   ```

2. **Run MongoDB locally**  
   Start your local MongoDB server (default URI is `mongodb://localhost:27017/`).

3. **Launch the app**  
   ```bash
   python Paint_Update.py
   ```

The app will connect to a local MongoDB database named `MiniaturePaints` and use a collection called `Paints`.

## Data Structure

Each paint entry includes:

| Field    | Example           | Description                           |
|----------|-------------------|---------------------------------------|
| Brand    | Citadel           | Paint brand                           |
| Name     | Mephiston Red     | Paint color name                      |
| Type     | Base, Layer, etc. | Paint type (e.g., Base, Shade, Dry)   |
| Status   | Owned, Empty, Wishlist | Inventory status                 |
| Quantity | 1, 2, 3...         | Number of bottles owned               |

## Exporting Options

- `Export to CSV`: Saves all paints to `paint_collection.csv`
- `Check Paint List`: Paste one paint per line and find missing colors
  - Fuzzy match suggestions
  - Optionally export missing results to `missing_paints.csv`

## Future Improvements

- Add editing/deleting individual paints
- Support for cloud-based MongoDB
- Dark/light mode toggle
- Import paint lists from CSV or JSON

## License

This project is licensed under the MIT License. Feel free to modify and share it!
