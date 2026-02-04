import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import threading
import time
import AI  # Ensure AI.py is in the same folder

# --- 1. INITIALIZE ROOT WINDOW ---
root = tk.Tk()
root.title("BANK| AI Sign-In Security Monitor")
root.state('zoomed') # Full screen mode

# --- BRANDING COLORS ---
MASHREQ_ORANGE = "#FF5E00"
MASHREQ_DARK = "#1D252D"
MASHREQ_BG = "#FFFFFF" 
MASHREQ_WHITE = "#FFFFFF"
MASHREQ_STRIPE = "#F2F4F4"
HIGH_RISK_RED = "#FFD1D1"

# --- 2. CONFIGURE STYLES ---
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background=MASHREQ_WHITE, fieldbackground=MASHREQ_WHITE,foreground="black", rowheight=35, font=("Segoe UI", 10))
style.configure("Treeview.Heading", background=MASHREQ_DARK, foreground="white",font=("Segoe UI", 10, "bold"))
style.map("Treeview", background=[('selected', MASHREQ_ORANGE)])

root.configure(bg=MASHREQ_BG)

# --- GLOBAL VARIABLES ---
current_page = 0
PAGE_SIZE = 50
search_query = "" # NEW: Stores the current search text

# --- FUNCTIONS ---

def run_in_background():
    """Runs the AI data generator in a separate thread."""
    while True:
        try:
            AI.main()
            time.sleep(10)
        except Exception as e:
            print(f"Background Update Waiting: {e}")
            time.sleep(5)

def perform_search():
    """Updates the global search query and reloads data."""
    global search_query, current_page
    search_query = search_entry.get().strip().lower()
    current_page = 0 # Reset to first page of results
    load_excel()

def clear_search():
    """Clears the search bar and resets the view."""
    global search_query, current_page
    search_entry.delete(0, tk.END)
    search_query = ""
    current_page = 0
    load_excel()

def load_excel():
    """Reads Excel, filters by search, sorts, and populates table."""
    global current_page
    file_path = "D://Python//28.py//Mashreq//Mashreq_SignIn_Data.xlsx"
    
    df = None
    for i in range(5):
        try:
            df = pd.read_excel(file_path)
            break
        except:
            time.sleep(0.5)

    if df is None: return

    try:
        # 1. APPLY SEARCH FILTER (New Logic)
        if search_query:
            # Filter looks in User_ID, IP, or Location
            # We convert everything to string (.astype(str)) so we don't crash on numbers
            mask = (
                df['User_ID'].astype(str).str.lower().str.contains(search_query) |
                df['IP_Address'].astype(str).str.lower().str.contains(search_query) |
                df['Location'].astype(str).str.lower().str.contains(search_query)
            )
            df = df[mask]

        # 2. Sorting
        if 'Risk_Level' in df.columns:
            df['Risk_Level'] = pd.Categorical(df['Risk_Level'], categories=["High", "Low"], ordered=True)
            df = df.sort_values(by=['Risk_Level', 'Contacted_User'], ascending=[True, True])

        # 3. Pagination
        start_idx = current_page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        df_page = df.iloc[start_idx:end_idx]

        # 4. Update Status Bar
        if len(df) == 0:
            status_label.config(text="No records found.")
        else:
            status_label.config(text=f"Viewing {start_idx + 1} - {min(end_idx, len(df))} of {len(df)} records")

        # 5. Refresh Columns & Insert Data
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center") 

        tree.delete(*tree.get_children())
        for i, (_, row) in enumerate(df_page.iterrows()):
            if row['Risk_Level'] == "High":
                tag = "danger"
            elif i % 2 == 0:
                tag = "even"
            else:
                tag = "odd"
            tree.insert("", "end", values=list(row), tags=(tag,))

        tree.tag_configure("danger", background=HIGH_RISK_RED, foreground="black")
        tree.tag_configure("even", background=MASHREQ_STRIPE)
        tree.tag_configure("odd", background=MASHREQ_WHITE)

    except Exception as e:
        messagebox.showerror("Error", f"Load Failed: {e}")

def mark_as_contacted():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Required", "Please select a high-risk user to update.")
        return
    item_values = tree.item(selected_item)['values']
    user_id = item_values[0]
    file_path = "D://Python//28.py//Mashreq//Mashreq_SignIn_Data.xlsx"
    try:
        df = pd.read_excel(file_path)
        df.loc[df['User_ID'] == user_id, 'Contacted_User'] = 'Yes'
        df.to_excel(file_path, index=False)
        load_excel()
    except Exception as e:
        messagebox.showerror("Error", f"Update Failed: {e}")

# --- UI LAYOUT ---

# 1. Header Section
header_frame = tk.Frame(root, bg=MASHREQ_DARK, height=80)
header_frame.pack(fill="x")

# Title (Left)
title_label = tk.Label(header_frame, text="MASHREQ SECURITY DASHBOARD",font=("Arial Black", 18), fg=MASHREQ_ORANGE, bg=MASHREQ_DARK)
title_label.pack(pady=20, padx=30, side="left")

# --- NEW: SEARCH BAR (Right) ---
# We use a sub-frame to group the Entry and Buttons together
search_frame = tk.Frame(header_frame, bg=MASHREQ_DARK)
search_frame.pack(side="right", padx=20, pady=20)

tk.Label(search_frame, text="Search User:", fg="white", bg=MASHREQ_DARK, font=("Segoe UI", 10)).pack(side="left", padx=5)

search_entry = tk.Entry(search_frame, width=25, font=("Segoe UI", 10))
search_entry.pack(side="left", padx=5)
# Bind the "Enter" key to perform search
search_entry.bind('<Return>', lambda event: perform_search())

btn_search = tk.Button(search_frame, text="🔍 Search", command=perform_search,bg=MASHREQ_ORANGE, fg="white", relief="flat", font=("Segoe UI", 9, "bold"))
btn_search.pack(side="left", padx=5)

btn_clear = tk.Button(search_frame, text="✖", command=clear_search,bg="#7F8C8D", fg="white", relief="flat", font=("Segoe UI", 9, "bold"))
btn_clear.pack(side="left", padx=2)

# Status Label (Now next to search)
status_label = tk.Label(header_frame, text="Initializing...",font=("Segoe UI", 10, "italic"), fg="#AAAAAA", bg=MASHREQ_DARK)
status_label.pack(side="right", padx=10)


# 2. Main Table Section
content_frame = tk.Frame(root, bg=MASHREQ_BG)
content_frame.pack(fill="both", expand=True, padx=30, pady=20)

tree_frame = tk.Frame(content_frame)
tree_frame.pack(fill="both", expand=True)

tree = ttk.Treeview(tree_frame, selectmode="browse")
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# 3. Footer / Button Section
button_frame = tk.Frame(root, bg=MASHREQ_BG)
button_frame.pack(fill="x", pady=20)

btn_style = {"font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 20, "pady": 8}

tk.Button(button_frame, text="Previous",command=lambda: [globals().update(current_page=max(0, current_page-1)), load_excel()], bg=MASHREQ_DARK, fg="white", **btn_style).pack(side="left", padx=30)

tk.Button(button_frame, text="Next Page",command=lambda: [globals().update(current_page=current_page+1), load_excel()],bg=MASHREQ_DARK, fg="white", **btn_style).pack(side="left")

tk.Button(button_frame, text="✅ MARK AS CONTACTED", command=mark_as_contacted, bg=MASHREQ_ORANGE, fg="white", **btn_style).pack(side="right", padx=30)

tk.Button(button_frame, text="Refresh Data", command=load_excel,bg="#7F8C8D", fg="white", **btn_style).pack(side="right")

# --- START APPLICATION ---
threading.Thread(target=run_in_background, daemon=True).start()
load_excel()


root.mainloop()
