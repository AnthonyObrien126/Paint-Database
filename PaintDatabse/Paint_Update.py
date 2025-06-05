import customtkinter as ctk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import difflib
import csv

# --- Setup appearance ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- MongoDB setup ---
client = MongoClient("mongodb://localhost:27017/")
db = client["MiniaturePaints"]
collection = db["Paints"]

# --- Normalization ---
def normalize(text):
    return " ".join(text.strip().split()).title()

# --- Refresh Table ---
def refresh_table(filtered=False):
    for row in tree.get_children():
        tree.delete(row)

    query = {}
    if filtered:
        field = filter_by_var.get().lower()
        value = normalize(search_var.get())
        if value:
            query[field] = {"$regex": f"^{value}", "$options": "i"}  # case-insensitive startswith

    for paint in collection.find(query):
        tree.insert("", "end", values=(
            paint['brand'],
            paint['name'],
            paint['type'],
            paint['status'],
            paint['quantity']
        ))

# --- Sort Function ---
def sort_by_column(col, descending):
    data = [(tree.set(child, col), child) for child in tree.get_children()]
    try:
        data.sort(key=lambda t: int(t[0]) if col == "Quantity" else t[0].lower(), reverse=descending)
    except Exception:
        data.sort(reverse=descending)

    for i, (_, k) in enumerate(data):
        tree.move(k, "", i)

    tree.heading(col, command=lambda: sort_by_column(col, not descending))

# --- Add / Update Paint ---
def add_paint():
    brand = normalize(brand_var.get())
    name = normalize(name_var.get())
    ptype = type_var.get()
    status = status_var.get()
    qty = quantity_var.get()

    if not qty.isdigit():
        messagebox.showerror("Invalid Input", "Quantity must be a number.")
        return

    quantity = int(qty)
    if not all([brand, name, ptype, status]):
        messagebox.showerror("Missing Info", "Please fill out all fields.")
        return

    existing = collection.find_one({"brand": brand, "name": name})
    if existing:
        collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {"status": status, "type": ptype}, "$inc": {"quantity": quantity}}
        )
        messagebox.showinfo("Updated", f"Updated quantity for {name}.")
    else:
        collection.insert_one({
            "brand": brand,
            "name": name,
            "type": ptype,
            "status": status,
            "quantity": quantity
        })
        messagebox.showinfo("Added", f"Paint '{name}' added!")

    refresh_table()

# --- Export to CSV ---
def export_to_csv():
    with open("paint_collection.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Brand", "Name", "Type", "Status", "Quantity"])
        for paint in collection.find():
            writer.writerow([
                paint.get("brand", ""),
                paint.get("name", ""),
                paint.get("type", ""),
                paint.get("status", ""),
                paint.get("quantity", 0)
            ])
    messagebox.showinfo("Exported", "Paints exported to 'paint_collection.csv'.")

# --- Compare Paint List ---
def check_paste_list_popup():
    popup = ctk.CTkToplevel(root)
    popup.title("Paste Paint List")
    popup.geometry("500x500")
    popup.lift()
    popup.focus_force()
    popup.grab_set()

    ctk.CTkLabel(popup, text="Paste one paint name per line:").pack(pady=10)

    paste_box = ctk.CTkTextbox(popup, width=460, height=250)
    paste_box.pack(padx=10)

    result_box = ctk.CTkTextbox(popup, width=460, height=120)
    result_box.pack(padx=10, pady=5)
    result_box.configure(state="disabled")

    export_var = ctk.BooleanVar(value=True)
    export_checkbox = ctk.CTkCheckBox(popup, text="Export missing paints to CSV", variable=export_var)
    export_checkbox.pack(pady=(5, 0))

    def run_check():
        pasted = paste_box.get("1.0", "end").strip().splitlines()
        pasted_normalized = [normalize(name) for name in pasted if name.strip()]

        found = []
        missing = []

        # Pull all existing paint names from the DB once
        all_names = [p["name"] for p in collection.find({}, {"name": 1})]

        for name in pasted_normalized:
            # Try exact match (case-insensitive)
            match = collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

            if match:
                found.append(name)
            else:
                # Fuzzy match fallback
                close = difflib.get_close_matches(name, all_names, n=1, cutoff=0.75)
                if close:
                    missing.append(f"{name}  →  ❓ Did you mean: {close[0]}?")
                else:
                    missing.append(name)

        result_box.configure(state="normal")
        result_box.delete("1.0", "end")
        result_box.insert("end", f"✅ Found ({len(found)}):\n" + "\n".join(found) + "\n\n")
        result_box.insert("end", f"❌ Missing ({len(missing)}):\n" + "\n".join(missing))
        result_box.configure(state="disabled")

        # Export if checkbox selected
        if export_var.get() and missing:
            with open("missing_paints.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Missing Paint Name", "Suggestion (if any)"])
                for entry in missing:
                    if "→" in entry:
                        original, suggestion = entry.split("→")
                        writer.writerow([original.strip(), suggestion.strip()])
                    else:
                        writer.writerow([entry, ""])
            messagebox.showinfo("Export Complete", "Missing paints saved to 'missing_paints.csv'.")

    ctk.CTkButton(popup, text="Check", command=run_check).pack(pady=10)

# --- GUI Setup ---
root = ctk.CTk()
root.title("🎨 Miniature Paint Manager")
root.geometry("740x540")
root.resizable(False, False)

# --- Form Section ---
form_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="gray20")
form_frame.pack(pady=15, padx=15, fill="x")

brand_var = ctk.StringVar()
name_var = ctk.StringVar()
type_options = ["Base", "Layer", "Shade", "Contrast", "Technical", "Dry", "Texture", "Airbrush"]
status_options = ["Owned", "Empty", "Wishlist"]
type_var = ctk.StringVar(value=type_options[0])
status_var = ctk.StringVar(value=status_options[0])
quantity_var = ctk.StringVar(value="1")

# --- Form Layout ---
ctk.CTkLabel(form_frame, text="Brand").grid(row=0, column=0, padx=10, pady=5, sticky="w")
ctk.CTkEntry(form_frame, textvariable=brand_var, width=200).grid(row=0, column=1, padx=10, pady=5)

ctk.CTkLabel(form_frame, text="Name").grid(row=0, column=2, padx=10, pady=5, sticky="w")
ctk.CTkEntry(form_frame, textvariable=name_var, width=200).grid(row=0, column=3, padx=10, pady=5)

ctk.CTkLabel(form_frame, text="Type").grid(row=1, column=0, padx=10, pady=5, sticky="w")
ctk.CTkOptionMenu(form_frame, values=type_options, variable=type_var, width=190).grid(row=1, column=1, padx=10, pady=5)

ctk.CTkLabel(form_frame, text="Status").grid(row=1, column=2, padx=10, pady=5, sticky="w")
ctk.CTkOptionMenu(form_frame, values=status_options, variable=status_var, width=190).grid(row=1, column=3, padx=10, pady=5)

ctk.CTkLabel(form_frame, text="Quantity").grid(row=2, column=0, padx=10, pady=5, sticky="w")
ctk.CTkEntry(form_frame, textvariable=quantity_var, width=80).grid(row=2, column=1, padx=10, pady=5, sticky="w")

ctk.CTkButton(form_frame, text="Add / Update Paint", command=add_paint).grid(row=3, column=0, columnspan=2, pady=10)
ctk.CTkButton(form_frame, text="Export to CSV", command=export_to_csv).grid(row=3, column=2, columnspan=2, pady=10)

ctk.CTkButton(form_frame, text="Check Paint List", command=check_paste_list_popup).grid(row=4, column=0, columnspan=4, pady=5)


# --- Filter Section ---
filter_frame = ctk.CTkFrame(root, corner_radius=10)
filter_frame.pack(padx=15, pady=(0, 5), fill="x")

filter_options = ["Brand", "Name", "Type", "Status"]
filter_by_var = ctk.StringVar(value="Name")
search_var = ctk.StringVar()

ctk.CTkLabel(filter_frame, text="Filter by").pack(side="left", padx=10)
ctk.CTkOptionMenu(filter_frame, values=filter_options, variable=filter_by_var, width=120).pack(side="left")
ctk.CTkEntry(filter_frame, textvariable=search_var, width=300, placeholder_text="Search...").pack(side="left", padx=10)

ctk.CTkButton(filter_frame, text="Search", command=lambda: refresh_table(True)).pack(side="left", padx=5)
ctk.CTkButton(filter_frame, text="Clear", command=lambda: [search_var.set(""), refresh_table(False)]).pack(side="left")

# --- Paint Table Section ---
table_container = ctk.CTkFrame(root, corner_radius=10)
table_container.pack(padx=15, pady=10, fill="both", expand=True)

columns = ("Brand", "Name", "Type", "Status", "Quantity")
tree = ttk.Treeview(table_container, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_by_column(_col, False))
    tree.column(col, anchor="center", width=130)

scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(fill="both", expand=True)

refresh_table()
root.mainloop()
