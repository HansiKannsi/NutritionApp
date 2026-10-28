import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
import json
import math
import os
import datetime
import requests

# Color palette
BG = "#f3f4f8"
CARD = "#ffffff"
PRIMARY = "#4f46e5"
PRIMARY_DARK = "#4338ca"
PRIMARY_DARKER = "#3730a3"
PRIMARY_LIGHT = "#eef2ff"
TEXT = "#111827"
MUTED = "#6b7280"
BORDER = "#e5e7eb"
HOVER = "#f3f4f6"
DANGER = "#dc2626"
AVG_LINE = "#f59e0b"
BURNED_COLOR = "#ef4444"
DEFICIT_COLOR = "#10b981"
WEIGHT_COLOR = "#0ea5e9"
MACRO_COLORS = {"protein": "#10b981", "fat": "#f59e0b", "carbs": "#3b82f6", "fiber": "#8b5cf6"}

MACROS = ("protein", "fat", "carbs", "fiber")
NUTRIENTS = ("calories",) + MACROS
NUTRIENT_LABELS = {
    "calories": "Calories (kcal / 100 g)",
    "protein": "Protein (g / 100 g)",
    "fat": "Fat (g / 100 g)",
    "carbs": "Carbs (g / 100 g)",
    "fiber": "Fiber (g / 100 g)",
}
COLUMNS = ("Food", "Grams", "Calories", "Protein", "Fat", "Carbs", "Fiber")
MEALS_DIR = "meals_data"
SAVED_DIR = "saved_meals"
FOODS_FILE = "foods.json"
BODY_FILE = "body_log.json"
KCAL_PER_KG_FAT = 7700


def pick_font_family(root):
    available = set(tkfont.families(root))
    for family in ("Inter", "Segoe UI", "SF Pro Text", "Ubuntu", "Cantarell", "Noto Sans", "DejaVu Sans"):
        if family in available:
            return family
    return "Helvetica"


class NutritionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nutrition Tracker")
        self.root.geometry("1280x820")
        self.root.minsize(1000, 640)
        self.font_family = pick_font_family(root)
        self.setup_styles()

        self.foods = self.load_foods(FOODS_FILE)
        self.index_foods()
        os.makedirs(SAVED_DIR, exist_ok=True)
        os.makedirs(MEALS_DIR, exist_ok=True)

        # Each meal: dict with name, items, frame, tree, widgets and sort state
        self.meals = []
        self.current_date = datetime.date.today()
        self.body_log = self.load_body_log()
        self.build_layout()

        today_file = self.day_file(self.current_date)
        if os.path.exists(today_file):
            self.import_meals(today_file, self.current_date)
        else:
            self.create_meal_ui("Meal 1", [])
        self.update_date_label()
        self.update_daily_totals()
        self.refresh_body_inputs()

    # ------------------------------------------------------------------ styling

    def setup_styles(self):
        fam = self.font_family
        self.fonts = {
            "small": (fam, 10),
            "small_bold": (fam, 10, "bold"),
            "base": (fam, 11),
            "bold": (fam, 11, "bold"),
            "h2": (fam, 14, "bold"),
            "h1": (fam, 18, "bold"),
            "big": (fam, 34, "bold"),
        }
        self.root.configure(bg=BG)
        self.root.option_add("*TCombobox*Listbox.font", self.fonts["base"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "white")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, font=self.fonts["base"], bordercolor=BORDER,
                        troughcolor=BG, focuscolor=PRIMARY, selectbackground=PRIMARY, selectforeground="white")

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Header.TFrame", background=PRIMARY)

        labels = {
            "TLabel": dict(background=BG),
            "Section.TLabel": dict(background=BG, font=self.fonts["h2"]),
            "Card.TLabel": dict(background=CARD),
            "CardBold.TLabel": dict(background=CARD, font=self.fonts["bold"]),
            "CardTitle.TLabel": dict(background=CARD, font=self.fonts["h2"]),
            "Muted.TLabel": dict(background=CARD, foreground=MUTED, font=self.fonts["small"]),
            "Big.TLabel": dict(background=CARD, foreground=PRIMARY, font=self.fonts["big"]),
            "Header.TLabel": dict(background=PRIMARY, foreground="white", font=self.fonts["h1"]),
            "HeaderSub.TLabel": dict(background=PRIMARY, foreground="#c7d2fe"),
            "Tile.TLabel": dict(background=BG, foreground=MUTED, font=self.fonts["small"]),
            "TileValue.TLabel": dict(background=BG, font=self.fonts["h2"]),
        }
        for name, opts in labels.items():
            style.configure(name, **opts)

        def button_style(name, bg, fg, hover, pressed, border=None, padding=(14, 8)):
            border = border or bg
            style.configure(name, background=bg, foreground=fg, bordercolor=border, lightcolor=bg, darkcolor=bg,
                            padding=padding, font=self.fonts["bold"], relief="solid", borderwidth=1, focuscolor=border)
            states = [("pressed", pressed), ("active", hover)]
            style.map(name, background=states, lightcolor=states, darkcolor=states)

        button_style("TButton", CARD, TEXT, HOVER, BORDER, border="#d1d5db")
        button_style("Small.TButton", CARD, TEXT, HOVER, BORDER, border="#d1d5db", padding=(10, 4))
        button_style("Accent.TButton", PRIMARY, "white", PRIMARY_DARK, PRIMARY_DARKER)
        button_style("Danger.TButton", CARD, DANGER, "#fef2f2", "#fee2e2", border="#fecaca")
        button_style("Header.TButton", PRIMARY_DARK, "white", PRIMARY_DARKER, "#312e81")

        for name in ("TEntry", "TCombobox", "TSpinbox"):
            style.configure(name, fieldbackground=CARD, background=CARD, foreground=TEXT, bordercolor=BORDER,
                            lightcolor=CARD, darkcolor=CARD, padding=6, arrowcolor=MUTED, insertcolor=TEXT)
            style.map(name, bordercolor=[("focus", PRIMARY)], lightcolor=[("focus", PRIMARY)],
                      fieldbackground=[("readonly", CARD)])

        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background=BG, foreground=MUTED, padding=(18, 8),
                        font=self.fonts["bold"], bordercolor=BG, lightcolor=BG)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD), ("active", "#e9ebf3")],
                  foreground=[("selected", PRIMARY)],
                  lightcolor=[("selected", CARD)],
                  bordercolor=[("selected", BORDER)])

        style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                        rowheight=34, borderwidth=0, font=self.fonts["base"])
        style.map("Treeview", background=[("selected", PRIMARY_LIGHT)], foreground=[("selected", PRIMARY)])
        style.configure("Treeview.Heading", background=CARD, foreground=MUTED, font=self.fonts["small_bold"],
                        relief="flat", padding=(8, 8), bordercolor=BORDER, lightcolor=CARD, darkcolor=CARD)
        style.map("Treeview.Heading", background=[("active", HOVER)])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        style.configure("Vertical.TScrollbar", background="#d1d5db", troughcolor=CARD, bordercolor=CARD,
                        lightcolor="#d1d5db", darkcolor="#d1d5db", arrowcolor=MUTED, gripcount=0)
        style.map("Vertical.TScrollbar", background=[("active", "#9ca3af")])
        style.configure("TSeparator", background=BORDER)

    def make_card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightcolor=BORDER,
                        highlightthickness=1, padx=18, pady=14)

    def make_dialog(self, title, geometry):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(geometry)
        dialog.configure(bg=CARD)
        dialog.transient(self.root)
        content = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        content.pack(fill="both", expand=True)
        return dialog, content

    def make_tree(self, parent, columns, widths):
        container = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tree = ttk.Treeview(container, columns=columns, show="headings")
        scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        for i, (col, width) in enumerate(zip(columns, widths)):
            anchor = "w" if i == 0 else "center"
            tree.heading(col, text=col, anchor=anchor)
            tree.column(col, width=width, anchor=anchor)
        return container, tree

    # ------------------------------------------------------------------ layout

    def build_layout(self):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(24, 14))
        header.pack(fill="x")
        titles = ttk.Frame(header, style="Header.TFrame")
        titles.pack(side="left")
        ttk.Label(titles, text="Nutrition Tracker", style="Header.TLabel").pack(anchor="w")
        self.date_label = ttk.Label(titles, style="HeaderSub.TLabel")
        self.date_label.pack(anchor="w")
        ttk.Button(header, text="Food Database", style="Header.TButton",
                   command=self.manage_database).pack(side="right")
        ttk.Button(header, text="Statistics", style="Header.TButton",
                   command=self.show_statistics).pack(side="right", padx=(0, 8))

        body = ttk.Frame(self.root, padding=20)
        body.pack(fill="both", expand=True)

        sidebar = ttk.Frame(body, width=290)
        sidebar.pack(side="right", fill="y", padx=(20, 0))
        sidebar.pack_propagate(False)
        main = ttk.Frame(body)
        main.pack(side="left", fill="both", expand=True)

        toolbar = ttk.Frame(main)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Label(toolbar, text="Meals", style="Section.TLabel").pack(side="left")
        ttk.Button(toolbar, text="Load Saved Meal", command=self.load_individual_meal).pack(side="right")
        ttk.Button(toolbar, text="+ New Meal", style="Accent.TButton",
                   command=self.add_meal).pack(side="right", padx=(0, 8))

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<Double-1>", self.handle_tab_double_click)

        totals = self.make_card(sidebar)
        totals.pack(fill="x")
        ttk.Label(totals, text="Daily Totals", style="CardTitle.TLabel").pack(anchor="w")
        self.calories_label = ttk.Label(totals, text="0", style="Big.TLabel")
        self.calories_label.pack(anchor="w", pady=(4, 0))
        ttk.Label(totals, text="kcal", style="Muted.TLabel").pack(anchor="w")
        ttk.Separator(totals).pack(fill="x", pady=10)
        self.macro_labels = {}
        for key in MACROS:
            row = ttk.Frame(totals, style="Card.TFrame")
            row.pack(fill="x", pady=2)
            tk.Label(row, text="\u25cf", fg=MACRO_COLORS[key], bg=CARD, font=self.fonts["base"]).pack(side="left")
            ttk.Label(row, text=key.capitalize(), style="Card.TLabel").pack(side="left", padx=(6, 0))
            value = ttk.Label(row, text="0.0 g", style="CardBold.TLabel")
            value.pack(side="right")
            self.macro_labels[key] = value

        actions = self.make_card(sidebar)
        actions.pack(fill="x", pady=(14, 0))
        ttk.Label(actions, text="Days", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Button(actions, text="Save Today's Meals", style="Accent.TButton",
                   command=self.export_meals).pack(fill="x", pady=4)
        ttk.Button(actions, text="Open Previous Day\u2026", command=self.load_from_date).pack(fill="x", pady=4)

        body = self.make_card(sidebar)
        body.pack(fill="x", pady=(14, 0))
        body.columnconfigure(1, weight=1)
        ttk.Label(body, text="Today's Body & Activity", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        self.body_inputs = {}
        for row, (key, label, unit) in enumerate((("burned", "Burned", "kcal"), ("weight", "Weight", "kg")), start=1):
            ttk.Label(body, text=label, style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(body, width=8, justify="right")
            entry.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
            entry.bind("<Return>", lambda e: self.save_today_body())
            ttk.Label(body, text=unit, style="Muted.TLabel").grid(row=row, column=2, sticky="w")
            self.body_inputs[key] = entry
        self.balance_label = ttk.Label(body, style="Muted.TLabel", wraplength=240)
        self.balance_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 8))
        body_buttons = ttk.Frame(body, style="Card.TFrame")
        body_buttons.grid(row=4, column=0, columnspan=3, sticky="ew")
        body_buttons.columnconfigure((0, 1), weight=1, uniform="btn")
        ttk.Button(body_buttons, text="Save", style="Accent.TButton",
                   command=self.save_today_body).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(body_buttons, text="Past Days\u2026",
                   command=self.show_body_log).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def update_date_label(self):
        today = datetime.date.today()
        if self.current_date == today:
            text = f"Today \u00b7 {today:%A, %d %B %Y}"
        else:
            text = f"Viewing {self.current_date:%A, %d %B %Y} \u00b7 saving stores it as today"
        self.date_label.config(text=text)

    # ------------------------------------------------------------------ food data

    def load_foods(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        messagebox.showerror("Error", f"Foods database {filename} not found.", parent=self.root)
        return []

    def index_foods(self):
        self.food_names = sorted(food["name"] for food in self.foods)
        self.food_dict = {food["name"].lower(): food for food in self.foods}

    def save_foods(self):
        with open(FOODS_FILE, "w") as f:
            json.dump(self.foods, f)

    def reload_foods(self):
        self.foods = self.load_foods(FOODS_FILE)
        self.index_foods()
        for meal in self.meals:
            meal["food_combo"]["values"] = self.food_names

    def item_nutrition(self, item):
        food = self.food_dict.get(item["food"].lower())
        factor = item["grams"] / 100.0
        return {key: (food[key] * factor if food else 0.0) for key in NUTRIENTS}

    def sum_items(self, items):
        totals = dict.fromkeys(NUTRIENTS, 0.0)
        for item in items:
            for key, value in self.item_nutrition(item).items():
                totals[key] += value
        totals["calories"] = round(totals["calories"])
        return totals

    @staticmethod
    def filter_combo(combo, values):
        typed = combo.get().lower()
        combo["values"] = [v for v in values if typed in v.lower()] if typed else values

    # ------------------------------------------------------------------ meals

    def create_meal_ui(self, meal_name, items):
        meal = {"name": meal_name, "items": items, "sort_column": None, "sort_direction": "asc"}
        self.meals.append(meal)

        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=18)
        self.notebook.add(frame, text=meal_name)
        meal["frame"] = frame

        toolbar = ttk.Frame(frame, style="Card.TFrame")
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Food", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(toolbar, text="Grams", style="Muted.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))

        food_combo = ttk.Combobox(toolbar, values=self.food_names, width=22)
        food_combo.grid(row=1, column=0, sticky="w")
        food_combo.bind("<KeyRelease>", lambda e: self.filter_combo(food_combo, self.food_names))
        grams_entry = ttk.Entry(toolbar, width=10)
        grams_entry.grid(row=1, column=1, padx=(8, 0))
        food_combo.bind("<Return>", lambda e: grams_entry.focus_set())
        grams_entry.bind("<Return>", lambda e: self.add_food_to_meal(meal))
        meal["food_combo"], meal["grams_entry"] = food_combo, grams_entry

        ttk.Button(toolbar, text="Add", style="Accent.TButton",
                   command=lambda: self.add_food_to_meal(meal)).grid(row=1, column=2, padx=8)
        ttk.Button(toolbar, text="Remove Selected",
                   command=lambda: self.remove_selected(meal)).grid(row=1, column=3)
        toolbar.columnconfigure(4, weight=1)
        ttk.Button(toolbar, text="Save Meal",
                   command=lambda: self.save_individual_meal(meal)).grid(row=1, column=5, padx=8)
        ttk.Button(toolbar, text="Remove Meal", style="Danger.TButton",
                   command=lambda: self.remove_meal(meal)).grid(row=1, column=6)

        container, tree = self.make_tree(frame, COLUMNS, (260, 100, 110, 100, 100, 100, 100))
        container.pack(fill="both", expand=True, pady=16)
        for col in COLUMNS:
            tree.heading(col, command=lambda c=col: self.sort_column(meal, c))
        tree.bind("<Delete>", lambda e: self.remove_selected(meal))
        tree.bind("<Double-1>", lambda e: self.edit_grams(e, meal))
        meal["tree"] = tree

        footer = ttk.Frame(frame, style="Card.TFrame")
        footer.pack(fill="x")
        ttk.Label(footer, text="Meal total", style="Muted.TLabel").pack(side="left")
        meal["calories_label"] = ttk.Label(footer, style="CardBold.TLabel")
        meal["calories_label"].pack(side="left", padx=8)
        meal["nutrients_label"] = ttk.Label(footer, style="Muted.TLabel")
        meal["nutrients_label"].pack(side="right")
        ttk.Label(frame, style="Muted.TLabel",
                  text="Tip: double-click grams to edit \u00b7 Del removes item \u00b7 double-click a tab to rename"
                  ).pack(anchor="w", pady=(10, 0))

        self.refresh_tree(meal)
        self.update_meal_totals(meal)
        return meal

    def add_meal(self):
        default_name = f"Meal {len(self.meals) + 1}"
        meal_name = simpledialog.askstring("New Meal", "Enter meal name:", initialvalue=default_name, parent=self.root)
        if meal_name is None:
            return
        meal = self.create_meal_ui(meal_name.strip() or default_name, [])
        self.notebook.select(meal["frame"])

    def create_meal_ui_from_data(self, meal_data):
        meal = self.create_meal_ui(meal_data.get("name") or f"Meal {len(self.meals) + 1}", meal_data.get("items", []))
        self.notebook.select(meal["frame"])

    def handle_tab_double_click(self, event):
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        if isinstance(index, int) and 0 <= index < len(self.meals):
            self.rename_meal(self.meals[index])

    def rename_meal(self, meal):
        new_name = simpledialog.askstring("Rename Meal", "Enter new meal name:", initialvalue=meal["name"], parent=self.root)
        if new_name:
            meal["name"] = new_name
            self.notebook.tab(meal["frame"], text=new_name)

    def remove_meal(self, meal):
        if len(self.meals) <= 1:
            messagebox.showerror("Error", "Cannot remove the last meal.", parent=self.root)
            return
        if not messagebox.askyesno("Confirm", f"Are you sure you want to remove {meal['name']}?", parent=self.root):
            return
        self.notebook.forget(meal["frame"])
        meal["frame"].destroy()
        self.meals.remove(meal)
        self.update_daily_totals()

    def sort_column(self, meal, column):
        if column == meal["sort_column"]:
            direction = "desc" if meal["sort_direction"] == "asc" else "asc"
        else:
            direction = "asc"
        meal["sort_column"], meal["sort_direction"] = column, direction

        def sort_key(item):
            if column == "Food":
                return item["food"].lower()
            if column == "Grams":
                return item["grams"]
            return self.item_nutrition(item)[column.lower()]

        meal["items"].sort(key=sort_key, reverse=(direction == "desc"))
        arrow = " \u25b2" if direction == "asc" else " \u25bc"
        for col in COLUMNS:
            meal["tree"].heading(col, text=col + (arrow if col == column else ""))
        self.refresh_tree(meal)

    def edit_grams(self, event, meal):
        tree = meal["tree"]
        row = tree.identify_row(event.y)
        if tree.identify_column(event.x) != "#2" or not row:
            return
        item = meal["items"][int(row)]
        new_grams = simpledialog.askfloat("Edit Grams", f"Enter new grams for {item['food']}:",
                                          initialvalue=item["grams"], minvalue=0.1, parent=self.root)
        if new_grams is None or new_grams <= 0:
            return
        item["grams"] = new_grams
        self.refresh_tree(meal)
        self.update_meal_totals(meal)
        self.update_daily_totals()

    def add_food_to_meal(self, meal):
        food_combo, grams_entry = meal["food_combo"], meal["grams_entry"]
        food_name = food_combo.get().strip()
        food = self.food_dict.get(food_name.lower())
        if not food:
            messagebox.showerror("Error", f"Food '{food_name}' not found. Please select a valid food from the dropdown.", parent=self.root)
            return
        try:
            grams = float(grams_entry.get().replace(",", "."))
            if grams <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid grams value.", parent=self.root)
            return

        meal["items"].append({"food": food["name"], "grams": grams})
        self.refresh_tree(meal)
        food_combo.set("")
        grams_entry.delete(0, tk.END)
        food_combo.focus_set()
        self.update_meal_totals(meal)
        self.update_daily_totals()

    def remove_selected(self, meal):
        tree = meal["tree"]
        selected = tree.selection()
        if not selected:
            return
        index = int(selected[0])
        del meal["items"][index]
        self.refresh_tree(meal)
        next_index = min(index, len(meal["items"]) - 1)
        if next_index >= 0:
            tree.selection_set(str(next_index))
            tree.focus(str(next_index))
        self.update_meal_totals(meal)
        self.update_daily_totals()

    def refresh_tree(self, meal):
        tree = meal["tree"]
        tree.delete(*tree.get_children())
        for i, item in enumerate(meal["items"]):
            n = self.item_nutrition(item)
            tree.insert("", "end", iid=str(i), values=(
                item["food"], f"{item['grams']:g} g", f"{round(n['calories'])} kcal",
                *(f"{n[key]:.1f} g" for key in MACROS)))

    def update_meal_totals(self, meal):
        totals = self.sum_items(meal["items"])
        meal["calories_label"].config(text=f"{totals['calories']} kcal")
        meal["nutrients_label"].config(
            text="   \u00b7   ".join(f"{key.capitalize()} {totals[key]:.1f} g" for key in MACROS))

    def get_daily_totals(self):
        return self.sum_items([item for meal in self.meals for item in meal["items"]])

    def update_daily_totals(self):
        totals = self.get_daily_totals()
        self.calories_label.config(text=str(totals["calories"]))
        for key in MACROS:
            self.macro_labels[key].config(text=f"{totals[key]:.1f} g")
        self.update_balance_label()

    # ------------------------------------------------------------------ body & activity

    def load_body_log(self):
        try:
            with open(BODY_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError) as err:
            messagebox.showerror("Error", f"Could not read {BODY_FILE}: {err}", parent=self.root)
            return {}
        return data if isinstance(data, dict) else {}

    def body_value(self, day, key):
        return self.body_log.get(day.isoformat(), {}).get(key)

    def parse_body_inputs(self, entries, parent):
        values = {}
        for key, entry in entries.items():
            text = entry.get().strip().replace(",", ".")
            if not text:
                values[key] = None
                continue
            try:
                value = float(text)
                if value <= 0:
                    raise ValueError
            except ValueError:
                name = "calories burned" if key == "burned" else "weight"
                messagebox.showerror("Error", f"Invalid value for {name}.", parent=parent)
                return None
            values[key] = round(value) if key == "burned" else round(value, 1)
        return values

    def set_body_values(self, day, values):
        entry = {key: value for key, value in values.items() if value is not None}
        if entry:
            self.body_log[day.isoformat()] = entry
        else:
            self.body_log.pop(day.isoformat(), None)
        with open(BODY_FILE, "w") as f:
            json.dump(self.body_log, f, indent=1, sort_keys=True)
        if day == datetime.date.today():
            self.refresh_body_inputs()

    def fill_body_entries(self, entries, day):
        for key, entry in entries.items():
            entry.delete(0, tk.END)
            value = self.body_value(day, key)
            if value is not None:
                entry.insert(0, f"{value:g}")

    def refresh_body_inputs(self):
        self.fill_body_entries(self.body_inputs, datetime.date.today())
        self.update_balance_label()

    def save_today_body(self):
        values = self.parse_body_inputs(self.body_inputs, self.root)
        if values is not None:
            self.set_body_values(datetime.date.today(), values)

    def eaten_on(self, day):
        if day == datetime.date.today() and self.current_date == day:
            # Include unsaved changes for today
            return self.get_daily_totals()["calories"] or None
        data = self.read_day(day)
        return self.day_calories(data) if data else None

    def update_balance_label(self):
        today = datetime.date.today()
        burned = self.body_value(today, "burned")
        if burned is None:
            text = "Enter today's total burned calories to see your deficit."
        else:
            eaten = self.eaten_on(today) or 0
            diff = burned - eaten
            text = (f"{abs(diff)} kcal {'deficit' if diff >= 0 else 'surplus'} "
                    f"(burned {burned} \u2212 eaten {eaten})")
        self.balance_label.config(text=text)

    def show_body_log(self):
        today = datetime.date.today()
        known = [today - datetime.timedelta(days=30)] + self.available_days()
        for iso in self.body_log:
            try:
                known.append(datetime.date.fromisoformat(iso))
            except ValueError:
                continue
        start = min(known)

        dialog, content = self.make_dialog("Body & Activity Log", "820x640")
        ttk.Label(content, text="Body & Activity Log", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(content, text="Select a day to add or correct calories burned and bodyweight. "
                  "Leave a field empty to remove its value.", style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        form = ttk.Frame(content, style="Card.TFrame")
        form.pack(side="bottom", fill="x")
        container, tree = self.make_tree(content, ("Date", "Weekday", "Eaten", "Burned", "Deficit", "Weight"),
                                         (120, 110, 110, 110, 150, 90))
        container.pack(fill="both", expand=True, pady=12)

        def row_values(day):
            eaten = self.eaten_on(day)
            burned = self.body_value(day, "burned")
            weight = self.body_value(day, "weight")
            if eaten is not None and burned is not None:
                diff = burned - eaten
                deficit = f"{abs(diff)} kcal {'deficit' if diff >= 0 else 'surplus'}"
            else:
                deficit = "\u2013"
            return (day.strftime("%d.%m.%Y"), day.strftime("%A"),
                    f"{eaten} kcal" if eaten is not None else "\u2013",
                    f"{burned} kcal" if burned is not None else "\u2013",
                    deficit,
                    f"{weight:.1f} kg" if weight is not None else "\u2013")

        for offset in range((today - start).days + 1):
            day = today - datetime.timedelta(days=offset)
            tree.insert("", "end", iid=day.isoformat(), values=row_values(day))

        form_title = ttk.Label(form, style="CardBold.TLabel")
        form_title.grid(row=0, column=0, columnspan=7, sticky="w", pady=(0, 6))
        entries = {}
        for i, (key, label, unit) in enumerate((("burned", "Calories burned", "kcal"), ("weight", "Weight", "kg"))):
            ttk.Label(form, text=label, style="Card.TLabel").grid(row=1, column=i * 3, sticky="w", padx=(0, 8))
            entry = ttk.Entry(form, width=10, justify="right")
            entry.grid(row=1, column=i * 3 + 1)
            ttk.Label(form, text=unit, style="Muted.TLabel").grid(row=1, column=i * 3 + 2, sticky="w", padx=(6, 24))
            entries[key] = entry
        form.columnconfigure(6, weight=1)

        def selected_day():
            selected = tree.selection()
            return datetime.date.fromisoformat(selected[0]) if selected else None

        def on_select(_event=None):
            day = selected_day()
            if day:
                form_title.config(text=f"{day:%A, %d %B %Y}")
                self.fill_body_entries(entries, day)

        def save(_event=None):
            day = selected_day()
            if not day:
                return
            values = self.parse_body_inputs(entries, dialog)
            if values is None:
                return
            self.set_body_values(day, values)
            tree.item(day.isoformat(), values=row_values(day))

        ttk.Button(form, text="Save Day", style="Accent.TButton", command=save).grid(row=1, column=6, sticky="e")
        for entry in entries.values():
            entry.bind("<Return>", save)
        tree.bind("<<TreeviewSelect>>", on_select)
        tree.selection_set(today.isoformat())
        tree.focus(today.isoformat())
        entries["burned"].focus_set()

    # ------------------------------------------------------------------ days

    @staticmethod
    def day_file(date):
        return os.path.join(MEALS_DIR, f"meals_{date.isoformat()}.json")

    def available_days(self):
        days = []
        for fname in os.listdir(MEALS_DIR):
            if fname.startswith("meals_") and fname.endswith(".json"):
                try:
                    days.append(datetime.date.fromisoformat(fname[len("meals_"):-len(".json")]))
                except ValueError:
                    continue
        return sorted(days, reverse=True)

    def read_day(self, date):
        try:
            with open(self.day_file(date), "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def day_calories(self, data):
        totals = data.get("daily_totals") or {}
        if "calories" in totals:
            return round(totals["calories"])
        return self.sum_items([item for meal in data.get("meals", []) for item in meal.get("items", [])])["calories"]

    def export_meals(self):
        today = datetime.date.today()
        file = self.day_file(today)
        data = {
            "meals": [{"name": meal["name"], "items": meal["items"]} for meal in self.meals],
            "daily_totals": self.get_daily_totals()
        }
        with open(file, "w") as f:
            json.dump(data, f)
        self.current_date = today
        self.update_date_label()
        messagebox.showinfo("Saved", f"Today's meals saved to {file}", parent=self.root)

    def import_meals(self, filename, date):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as err:
            messagebox.showerror("Error", f"Could not read {filename}: {err}", parent=self.root)
            return
        if "meals" not in data:
            messagebox.showerror("Error", "Invalid meal file format.", parent=self.root)
            return
        for meal in self.meals:
            self.notebook.forget(meal["frame"])
            meal["frame"].destroy()
        self.meals = []

        for meal_data in data["meals"]:
            items = [item for item in meal_data.get("items", []) if item.get("food", "").lower() in self.food_dict]
            self.create_meal_ui(meal_data.get("name") or f"Meal {len(self.meals) + 1}", items)
        if not self.meals:
            self.create_meal_ui("Meal 1", [])

        self.current_date = date
        self.update_date_label()
        self.update_daily_totals()

    def load_from_date(self):
        days = self.available_days()
        if not days:
            messagebox.showinfo("Open Day", "No saved days yet.", parent=self.root)
            return
        rows = []
        for day in days:
            data = self.read_day(day) or {}
            rows.append((day, day.strftime("%A"), len(data.get("meals", [])), self.day_calories(data)))

        dialog, content = self.make_dialog("Open Previous Day", "620x560")
        ttk.Label(content, text="Saved days", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(content, text="Filter by date or weekday, e.g. \"2025-08\" or \"friday\"",
                  style="Muted.TLabel").pack(anchor="w", pady=(4, 6))
        search = ttk.Entry(content)
        search.pack(fill="x")

        container, tree = self.make_tree(content, ("Date", "Weekday", "Meals", "Calories"), (140, 140, 80, 120))
        container.pack(fill="both", expand=True, pady=12)

        def populate(_event=None):
            query = search.get().strip().lower()
            tree.delete(*tree.get_children())
            for day, weekday, meal_count, kcal in rows:
                if query and query not in day.isoformat() and query not in weekday.lower():
                    continue
                tree.insert("", "end", iid=day.isoformat(),
                            values=(day.strftime("%d.%m.%Y"), weekday, meal_count, f"{kcal} kcal"))
            children = tree.get_children()
            if children:
                tree.selection_set(children[0])
                tree.focus(children[0])

        def open_selected(_event=None):
            selected = tree.selection()
            if not selected:
                return
            date = datetime.date.fromisoformat(selected[0])
            dialog.destroy()
            self.import_meals(self.day_file(date), date)

        def focus_tree(_event=None):
            tree.focus_set()
            return "break"

        search.bind("<KeyRelease>", lambda e: populate() if e.keysym not in ("Return", "Down", "Up") else None)
        search.bind("<Return>", open_selected)
        search.bind("<Down>", focus_tree)
        tree.bind("<Double-1>", open_selected)
        tree.bind("<Return>", open_selected)

        buttons = ttk.Frame(content, style="Card.TFrame")
        buttons.pack(fill="x", side="bottom", before=container)
        ttk.Button(buttons, text="Open", style="Accent.TButton", command=open_selected).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right", padx=8)

        populate()
        search.focus_set()

    # ------------------------------------------------------------------ statistics

    def history(self, num_days):
        today = datetime.date.today()
        rows = []
        for offset in range(num_days - 1, -1, -1):
            day = today - datetime.timedelta(days=offset)
            rows.append({"day": day, "eaten": self.eaten_on(day),
                         "burned": self.body_value(day, "burned"), "weight": self.body_value(day, "weight")})
        return rows

    @staticmethod
    def nice_step(raw):
        if raw <= 0:
            return 1
        magnitude = 10 ** math.floor(math.log10(raw))
        for factor in (1, 2, 2.5, 5, 10):
            if raw <= factor * magnitude:
                return factor * magnitude
        return 10 * magnitude

    def draw_chart(self, canvas, days, series, avg=None, avg_label=None, empty_text="No data in this range"):
        """series: dicts with name, kind ('bar'/'line'), values, color, fmt and optional neg_color, dash, dots."""
        canvas.delete("all")
        canvas.chart_info = None
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if not days or width < 100 or height < 100:
            return
        left, right, top, bottom = 64, 20, 58, 44
        plot_w, plot_h = width - left - right, height - top - bottom

        # Legend row, then hover tooltip row, both above the plot so they never cover data
        x = left
        legend = [(s["name"], s["kind"], s["color"], s.get("dash")) for s in series]
        if avg is not None:
            legend.append((avg_label, "line", AVG_LINE, (6, 4)))
        for name, kind, color, dash in legend:
            if kind == "bar":
                canvas.create_rectangle(x, 8, x + 12, 20, fill=color, outline="")
            else:
                canvas.create_line(x, 14, x + 18, 14, fill=color, width=2, **({"dash": dash} if dash else {}))
            label = canvas.create_text(x + 24, 14, text=name, anchor="w", fill=TEXT, font=self.fonts["small"])
            x = canvas.bbox(label)[2] + 20
        canvas.create_text(left, 38, text="", anchor="w", fill=TEXT, font=self.fonts["bold"], tags="tooltip")

        values = [v for s in series for v in s["values"] if v is not None]
        if not values:
            canvas.create_text(width / 2, height / 2, text=empty_text, fill=MUTED, font=self.fonts["base"])
            return
        has_bars = any(s["kind"] == "bar" for s in series)
        lo, hi = min(values), max(values)
        if avg is not None:
            lo, hi = min(lo, avg), max(hi, avg)
        if has_bars:
            lo, hi = min(lo, 0), max(hi, 0)
        else:
            pad = (hi - lo) * 0.15 or 1
            lo, hi = lo - pad, hi + pad
        if hi == lo:
            hi = lo + 1
        step = self.nice_step((hi - lo) / 5)
        lo, hi = math.floor(lo / step) * step, math.ceil(hi / step) * step

        def y_of(value):
            return top + plot_h * (hi - value) / (hi - lo)

        for k in range(round((hi - lo) / step) + 1):
            value = lo + k * step
            y = y_of(value)
            canvas.create_line(left, y, width - right, y, fill=BORDER, dash=(2, 4))
            canvas.create_text(left - 10, y, text=f"{round(value, 2):g}", anchor="e", fill=MUTED, font=self.fonts["small"])
        if has_bars:
            canvas.create_line(left, y_of(0), width - right, y_of(0), fill="#9ca3af")

        slot = plot_w / len(days)

        def x_of(i):
            return left + slot * (i + 0.5)

        bar_w = max(2, min(48, slot * 0.65))
        for s in series:
            if s["kind"] != "bar":
                continue
            for i, v in enumerate(s["values"]):
                if v is None:
                    continue
                color = s.get("neg_color", s["color"]) if v < 0 else s["color"]
                canvas.create_rectangle(x_of(i) - bar_w / 2, y_of(v), x_of(i) + bar_w / 2, y_of(0), fill=color, outline="")
                if slot >= 38:
                    canvas.create_text(x_of(i), y_of(v) + (10 if v < 0 else -10), text=str(round(v)),
                                       fill=TEXT, font=self.fonts["small"])

        for s in series:
            if s["kind"] != "line":
                continue
            points = [(x_of(i), y_of(v)) for i, v in enumerate(s["values"]) if v is not None]
            if len(points) >= 2:
                canvas.create_line(*[c for p in points for c in p], fill=s["color"], width=2,
                                   **({"dash": s["dash"]} if s.get("dash") else {}))
            if s.get("dots", True):
                for px, py in points:
                    canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill=CARD, outline=s["color"], width=2)

        if avg is not None:
            canvas.create_line(left, y_of(avg), width - right, y_of(avg), fill=AVG_LINE, width=2, dash=(6, 4))

        today = datetime.date.today()
        label_every = max(1, math.ceil(56 / slot))
        base = top + plot_h
        for i, day in enumerate(days):
            if (len(days) - 1 - i) % label_every == 0:
                text = f"{day:%a}\n{day:%d.%m}" if slot >= 44 else f"{day:%d.%m}"
                canvas.create_text(x_of(i), base + 8, text=text, anchor="n", justify="center",
                                   fill=PRIMARY if day == today else MUTED, font=self.fonts["small"])

        canvas.chart_info = {"left": left, "slot": slot, "top": top, "base": base, "days": days, "series": series}

    @staticmethod
    def chart_hover(canvas, event):
        canvas.delete("hover")
        info = getattr(canvas, "chart_info", None)
        index = math.floor((event.x - info["left"]) / info["slot"]) if info and event else -1
        if not info or not 0 <= index < len(info["days"]):
            canvas.itemconfig("tooltip", text="")
            return
        x0 = info["left"] + index * info["slot"]
        band = canvas.create_rectangle(x0, info["top"], x0 + info["slot"], info["base"],
                                       fill=HOVER, outline="", tags="hover")
        canvas.tag_lower(band)
        parts = [f"{info['days'][index]:%a, %d.%m.%Y}"]
        for s in info["series"]:
            value = s["values"][index]
            if value is not None:
                parts.append(f"{s['name']}: {s['fmt'](value)}")
        if len(parts) == 1:
            parts.append("no data")
        canvas.itemconfig("tooltip", text="   \u00b7   ".join(parts))

    def show_statistics(self):
        dialog, content = self.make_dialog("Statistics", "1060x720")
        days_var = tk.StringVar(value="14")
        state = {"days": [], "charts": {}}

        top = ttk.Frame(content, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Statistics", style="CardTitle.TLabel").pack(side="left")
        controls = ttk.Frame(top, style="Card.TFrame")
        controls.pack(side="right")
        ttk.Label(controls, text="Last", style="Card.TLabel").pack(side="left")
        spin = ttk.Spinbox(controls, from_=1, to=365, width=5, textvariable=days_var, command=lambda: reload())
        spin.pack(side="left", padx=6)
        spin.bind("<Return>", lambda e: reload())
        ttk.Label(controls, text="days", style="Card.TLabel").pack(side="left", padx=(0, 12))
        for n in (7, 14, 30, 90):
            ttk.Button(controls, text=str(n), style="Small.TButton",
                       command=lambda n=n: (days_var.set(str(n)), reload())).pack(side="left", padx=2)

        tiles = ttk.Frame(content, style="Card.TFrame")
        tiles.pack(fill="x", pady=16)
        tile_labels = {}
        tile_defs = (("eaten", "Avg. eaten"), ("burned", "Avg. burned"), ("deficit", "Total deficit"), ("weight", "Weight change"))
        for i, (key, title) in enumerate(tile_defs):
            tile = tk.Frame(tiles, bg=BG, padx=14, pady=10)
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))
            tiles.columnconfigure(i, weight=1, uniform="tile")
            ttk.Label(tile, text=title, style="Tile.TLabel").pack(anchor="w")
            value = ttk.Label(tile, text="\u2013", style="TileValue.TLabel")
            value.pack(anchor="w")
            sub = ttk.Label(tile, text="", style="Tile.TLabel")
            sub.pack(anchor="w")
            tile_labels[key] = (value, sub)

        notebook = ttk.Notebook(content)
        notebook.pack(fill="both", expand=True)
        canvases = {}
        for key, title in (("calories", "Calories"), ("deficit", "Daily Deficit"),
                           ("cumulative", "Cumulative Deficit"), ("weight", "Weight")):
            frame = ttk.Frame(notebook, style="Card.TFrame", padding=(8, 12))
            notebook.add(frame, text=title)
            canvas = tk.Canvas(frame, bg=CARD, highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.bind("<Configure>", lambda e, k=key: draw(k))
            canvas.bind("<Motion>", lambda e, c=canvas: self.chart_hover(c, e))
            canvas.bind("<Leave>", lambda e, c=canvas: self.chart_hover(c, None))
            canvases[key] = canvas

        def set_tile(key, value, sub=""):
            tile_labels[key][0].config(text=value)
            tile_labels[key][1].config(text=sub)

        def draw(key):
            if key in state["charts"]:
                self.draw_chart(canvases[key], state["days"], **state["charts"][key])

        def mean(values):
            return sum(values) / len(values) if values else None

        def kcal(v):
            return f"{round(v)} kcal"

        def deficit_text(v):
            return f"{abs(round(v))} kcal {'deficit' if v >= 0 else 'surplus'}"

        def reload():
            try:
                num_days = max(1, min(365, int(days_var.get())))
            except ValueError:
                return
            days_var.set(str(num_days))
            rows = self.history(num_days)
            days = [r["day"] for r in rows]
            eaten = [r["eaten"] for r in rows]
            burned = [r["burned"] for r in rows]
            weight = [r["weight"] for r in rows]
            deficit = [b - e if b is not None and e is not None else None for b, e in zip(burned, eaten)]
            cumulative, running = [], 0
            for d in deficit:
                running += d or 0
                cumulative.append(running if d is not None else None)
            trend = []
            for day in days:
                # Window reaches before the range so the first days get a real average too
                window = [self.body_value(day - datetime.timedelta(days=k), "weight") for k in range(7)]
                window = [w for w in window if w is not None]
                trend.append(round(mean(window), 2) if window else None)

            logged_eaten = [v for v in eaten if v is not None]
            logged_burned = [v for v in burned if v is not None]
            logged_deficit = [v for v in deficit if v is not None]
            logged_trend = [v for v in trend if v is not None]
            avg_eaten, avg_burned, avg_deficit = mean(logged_eaten), mean(logged_burned), mean(logged_deficit)

            set_tile("eaten", kcal(avg_eaten) if logged_eaten else "\u2013", f"{len(logged_eaten)} of {num_days} days logged")
            set_tile("burned", kcal(avg_burned) if logged_burned else "\u2013", f"{len(logged_burned)} of {num_days} days logged")
            if logged_deficit:
                total = round(sum(logged_deficit))
                set_tile("deficit", f"{total} kcal",
                         f"\u2248 {abs(total) / KCAL_PER_KG_FAT:.2f} kg fat {'lost' if total >= 0 else 'gained'}")
            else:
                set_tile("deficit", "\u2013", "needs eaten + burned on the same day")
            if logged_trend:
                first, last = logged_trend[0], logged_trend[-1]
                set_tile("weight", f"{last - first:+.1f} kg", f"7-day avg. {first:.1f} \u2192 {last:.1f} kg")
            else:
                set_tile("weight", "\u2013", "no weight logged")

            state["days"] = days
            state["charts"] = {
                "calories": dict(
                    series=[dict(name="Eaten", kind="bar", values=eaten, color=PRIMARY, fmt=kcal),
                            dict(name="Burned", kind="line", values=burned, color=BURNED_COLOR, fmt=kcal)],
                    avg=avg_eaten, avg_label=f"\u00d8 eaten {round(avg_eaten)} kcal" if logged_eaten else None),
                "deficit": dict(
                    series=[dict(name="Deficit (burned \u2212 eaten)", kind="bar", values=deficit,
                                 color=DEFICIT_COLOR, neg_color=BURNED_COLOR, fmt=deficit_text)],
                    avg=avg_deficit, avg_label=f"\u00d8 {round(avg_deficit)} kcal / day" if logged_deficit else None,
                    empty_text="Log calories burned to see your deficit"),
                "cumulative": dict(
                    series=[dict(name="Cumulative deficit", kind="line", values=cumulative, color=DEFICIT_COLOR,
                                 fmt=lambda v: f"{round(v)} kcal (\u2248 {v / KCAL_PER_KG_FAT:.2f} kg fat)")],
                    empty_text="Log calories burned to see your deficit"),
                "weight": dict(
                    series=[dict(name="Weight", kind="line", values=weight, color=WEIGHT_COLOR, fmt=lambda v: f"{v:.1f} kg"),
                            dict(name="7-day average", kind="line", values=trend, color=PRIMARY, dash=(6, 4),
                                 dots=False, fmt=lambda v: f"{v:.1f} kg")],
                    empty_text="Log your bodyweight to see the trend"),
            }
            for key in canvases:
                draw(key)

        reload()

    # ------------------------------------------------------------------ saved meals

    def save_individual_meal(self, meal):
        save_name = simpledialog.askstring("Save Meal As", "Enter name to save:", initialvalue=meal["name"], parent=self.root)
        if save_name:
            file = os.path.join(SAVED_DIR, f"{save_name}.json")
            with open(file, "w") as f:
                json.dump({"name": save_name, "items": meal["items"]}, f)
            messagebox.showinfo("Success", f"Meal saved as {save_name}", parent=self.root)

    def load_individual_meal(self):
        names = sorted(f[:-5] for f in os.listdir(SAVED_DIR) if f.endswith(".json"))
        if not names:
            messagebox.showerror("Error", "No saved meals found.", parent=self.root)
            return

        dialog, content = self.make_dialog("Load Saved Meal", "440x200")
        ttk.Label(content, text="Saved meal", style="CardTitle.TLabel").pack(anchor="w")
        combo = ttk.Combobox(content, values=names)
        combo.pack(fill="x", pady=12)
        combo.bind("<KeyRelease>", lambda e: self.filter_combo(combo, names))
        combo.focus_set()

        def ok(_event=None):
            name = combo.get()
            if name:
                file = os.path.join(SAVED_DIR, f"{name}.json")
                if not os.path.exists(file):
                    messagebox.showerror("Error", f"{file} not found.", parent=dialog)
                    return
                with open(file, "r") as f:
                    data = json.load(f)
                self.create_meal_ui_from_data(data)
                self.update_daily_totals()
            dialog.destroy()

        combo.bind("<Return>", ok)
        buttons = ttk.Frame(content, style="Card.TFrame")
        buttons.pack(fill="x", side="bottom")
        ttk.Button(buttons, text="Load", style="Accent.TButton", command=ok).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right", padx=8)

    # ------------------------------------------------------------------ food database

    def fetch_openfoodfacts(self, barcode, entries, parent):
        if not barcode.strip():
            messagebox.showerror("Error", "Please enter a product ID.", parent=parent)
            return
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode.strip()}.json"
        params = {"fields": "product_name,nutriments"}
        # OpenFoodFacts rejects requests without a descriptive User-Agent (403)
        headers = {"User-Agent": "TkMealTracker/1.0 (personal use)"}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 404:
                messagebox.showerror("Error", "Product not found.", parent=parent)
                return
            response.raise_for_status()
            product = response.json()["product"]
            nutriments = product.get("nutriments", {})
            values = {
                "name": product.get("product_name", ""),
                "calories": nutriments.get("energy-kcal_100g", 0.0),
                "protein": nutriments.get("proteins_100g", 0.0),
                "fat": nutriments.get("fat_100g", 0.0),
                "carbs": nutriments.get("carbohydrates_100g", 0.0),
                "fiber": nutriments.get("fiber_100g", 0.0),
            }
            if not values["name"]:
                messagebox.showerror("Error", "Product name not found in OpenFoodFacts data.", parent=parent)
                return
            for key, entry in entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(values[key] or 0.0))
        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("Error", f"HTTP error occurred: {http_err}", parent=parent)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Connection error. Please check your internet connection.", parent=parent)
        except requests.exceptions.Timeout:
            messagebox.showerror("Error", "Request timed out.", parent=parent)
        except requests.exceptions.RequestException as err:
            messagebox.showerror("Error", f"An error occurred: {err}", parent=parent)
        except KeyError:
            messagebox.showerror("Error", "Product not found.", parent=parent)

    def nutrient_entries(self, parent, start_row):
        entries = {}
        for i, key in enumerate(NUTRIENTS):
            ttk.Label(parent, text=NUTRIENT_LABELS[key], style="Card.TLabel").grid(
                row=start_row + i, column=0, sticky="w", pady=4)
            entry = ttk.Entry(parent)
            entry.grid(row=start_row + i, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)
            entries[key] = entry
        return entries

    def manage_database(self):
        dialog, content = self.make_dialog("Food Database", "900x520")
        content.columnconfigure((0, 1), weight=1, uniform="col")

        def clear(entries):
            for entry in entries.values():
                entry.delete(0, tk.END)

        def read_nutrients(entries):
            try:
                return {key: float(entries[key].get().replace(",", ".")) for key in NUTRIENTS}
            except ValueError:
                messagebox.showerror("Error", "All nutritional values must be numbers.", parent=dialog)
                return None

        # Add food
        add_card = ttk.Frame(content, style="Card.TFrame")
        add_card.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        add_card.columnconfigure(1, weight=1)
        ttk.Label(add_card, text="Add Food", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        ttk.Label(add_card, text="Barcode", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        barcode_entry = ttk.Entry(add_card)
        barcode_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(add_card, text="Fills in values from OpenFoodFacts", style="Muted.TLabel").grid(
            row=2, column=1, columnspan=2, sticky="w", padx=8)
        ttk.Separator(add_card).grid(row=3, column=0, columnspan=3, sticky="ew", pady=12)
        ttk.Label(add_card, text="Name", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=4)
        add_entries = {"name": ttk.Entry(add_card)}
        add_entries["name"].grid(row=4, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)
        add_entries.update(self.nutrient_entries(add_card, start_row=5))

        def fetch(_event=None):
            self.fetch_openfoodfacts(barcode_entry.get(), add_entries, dialog)

        ttk.Button(add_card, text="Fetch", command=fetch).grid(row=1, column=2, pady=4)
        barcode_entry.bind("<Return>", fetch)

        def add_food():
            name = add_entries["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required.", parent=dialog)
                return
            values = read_nutrients(add_entries)
            if values is None:
                return
            existing = self.food_dict.get(name.lower())
            if existing:
                if not messagebox.askyesno("Confirm", f"Food '{name}' already exists. Do you want to override it?", parent=dialog):
                    return
                existing.update(values)
            else:
                self.foods.append({"name": name, **values})
            self.save_foods()
            self.reload_foods()
            clear(add_entries)
            barcode_entry.delete(0, tk.END)
            edit_combo["values"] = self.food_names
            messagebox.showinfo("Success", f"Food {'updated' if existing else 'added'}.", parent=dialog)

        ttk.Button(add_card, text="Add Food", style="Accent.TButton", command=add_food).grid(
            row=10, column=0, columnspan=3, sticky="ew", pady=(16, 0))

        # Edit / remove food
        edit_card = ttk.Frame(content, style="Card.TFrame")
        edit_card.grid(row=0, column=1, sticky="nsew")
        edit_card.columnconfigure(1, weight=1)
        ttk.Label(edit_card, text="Edit Food", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        ttk.Label(edit_card, text="Food", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        edit_combo = ttk.Combobox(edit_card, values=self.food_names)
        edit_combo.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)
        edit_combo.bind("<KeyRelease>", lambda e: self.filter_combo(edit_combo, self.food_names))
        ttk.Separator(edit_card).grid(row=2, column=0, columnspan=3, sticky="ew", pady=12)
        edit_entries = self.nutrient_entries(edit_card, start_row=3)

        def load_food(_event=None):
            clear(edit_entries)
            food = self.food_dict.get(edit_combo.get().lower())
            if food:
                for key, entry in edit_entries.items():
                    entry.insert(0, food[key])

        edit_combo.bind("<<ComboboxSelected>>", load_food)
        edit_combo.bind("<Return>", load_food)

        def edit_food():
            name = edit_combo.get()
            food = self.food_dict.get(name.lower())
            if not food:
                messagebox.showerror("Error", "Food not found.", parent=dialog)
                return
            if not messagebox.askyesno("Confirm", f"Are you sure you want to edit {name}?", parent=dialog):
                return
            values = read_nutrients(edit_entries)
            if values is None:
                return
            food.update(values)
            self.save_foods()
            self.reload_foods()
            edit_combo["values"] = self.food_names
            messagebox.showinfo("Success", "Food updated.", parent=dialog)

        def remove_food():
            name = edit_combo.get()
            if name.lower() not in self.food_dict:
                messagebox.showerror("Error", "Food not found.", parent=dialog)
                return
            if not messagebox.askyesno("Confirm", f"Are you sure you want to remove {name}?", parent=dialog):
                return
            self.foods = [food for food in self.foods if food["name"].lower() != name.lower()]
            self.save_foods()
            self.reload_foods()
            edit_combo.set("")
            clear(edit_entries)
            edit_combo["values"] = self.food_names
            messagebox.showinfo("Success", "Food removed.", parent=dialog)

        buttons = ttk.Frame(edit_card, style="Card.TFrame")
        buttons.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(16, 0))
        buttons.columnconfigure((0, 1), weight=1, uniform="btn")
        ttk.Button(buttons, text="Delete", style="Danger.TButton", command=remove_food).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(buttons, text="Save Changes", style="Accent.TButton", command=edit_food).grid(row=0, column=1, sticky="ew", padx=(6, 0))


if __name__ == "__main__":
    root = tk.Tk()
    app = NutritionApp(root)
    root.mainloop()
