from email import errors
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import getpass
import json
from datetime import datetime, date
from pathlib import Path
import pandas as pd
import os

BASE_DIR = Path.home() / "Documents" / "Follow-Ups" / "v3"
DATA_FILE = BASE_DIR / "call_notes.json"
CONTACTS_FILE = BASE_DIR / "contacts.json"
QUICK_NOTES_FILE = BASE_DIR / "quick_notes.json"
GENERAL_NOTES_FILE = BASE_DIR / "general_notes.json"
AUDIT_ONEDRIVE_ORG = "OneDrive - Universidad Hispanoamericana"
AUDIT_FOLDER_NAME = "Folder"
AUDIT_CSV_DELIMITER = ";"
AUDIT_COLUMNS = (
    "date",
    "follow_up",
    "cm_ref",
    "phone",
    "payer",
    "agent",
    "call_ref",
    "network",
    "plan_type",
    "specialty",
    "pos",
    "online",
    "fax",
    "mail",
    "attn",
    "prev_verified",
    "cc_name",
    "effective_date",
    "contract_comment",
    "action_note",
    "generated_note",
    "comments",
    "follow_up_date",
    "edited",
    "em_verified",
    "em_change",
    "emer_verified",
    "emer_change",
    "drg_verified",
    "drg_change",
)


def ensure_directories_exist():
    BASE_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories_exist()
class CallDetailsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Follow Ups Tool - V4.0")
        self.notes = self.load_json(DATA_FILE)
        self.contacts = self.load_json(CONTACTS_FILE)
        self.quick_notes = self.load_json(QUICK_NOTES_FILE)
        self.style = ttk.Style()
        self.configure_app_styles()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)
        self.workspace_tab = ttk.Frame(self.notebook)
        self.notes_tab = ttk.Frame(self.notebook)
        self.general_notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.workspace_tab, text="Workspace")
        self.notebook.add(self.notes_tab, text="Note History")
        self.notebook.add(self.general_notes_tab, text="Client's Information")
        self.entry_tabs = []
        self.active_form = None
        self.create_workspace_tab()
        self.create_history_tab()
        self.create_clients_tab()
        self.apply_classic_widget_theme(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.set_initial_window_size()

    def configure_app_styles(self):
        """Apply a compact dark theme for the dense follow-up workspace."""
        style = self.style
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        base_bg = "#0d1117"
        panel_bg = "#161b22"
        header_bg = "#0f172a"
        surface_bg = "#21262d"
        field_bg = "#0d1117"
        focus_bg = "#111827"

        text = "#f0f6fc"
        muted = "#8b949e"

        accent = "#2f81f7"
        accent_active = "#58a6ff"

        border = "#30363d"
        subtle_border = "#21262d"

        selected = "#1f6feb"
        selected_surface = "#102a4c"

        missing_contact_bg = "#3b1d2a"
        missing_contact_text = "#ffb4c8"

        success = "#3fb950"
        warning = "#d29922"
        error = "#f85149"
        self.theme_colors = {
            "base_bg": base_bg,
            "panel_bg": panel_bg,
            "header_bg": header_bg,
            "surface_bg": surface_bg,
            "field_bg": field_bg,
            "focus_bg": focus_bg,
            "text": text,
            "muted": muted,
            "accent": accent,
            "accent_active": accent_active,
            "border": border,
            "subtle_border": subtle_border,
            "selected": selected,
            "selected_surface": selected_surface,
            "missing_contact_bg": missing_contact_bg,
            "missing_contact_text": missing_contact_text,
            "success": success,
            "warning": warning,
            "error": error,
        }

        self.root.configure(background=base_bg)
        self.root.option_add("*Background", base_bg)
        self.root.option_add("*Foreground", text)
        self.root.option_add("*selectBackground", selected)
        self.root.option_add("*selectForeground", "#ffffff")
        self.root.option_add("*insertBackground", text)
        self.root.option_add("*Listbox.Background", field_bg)
        self.root.option_add("*Listbox.Foreground", text)
        self.root.option_add("*Listbox.selectBackground", selected)
        self.root.option_add("*Listbox.selectForeground", "#ffffff")
        self.root.option_add("*Text.Background", field_bg)
        self.root.option_add("*Text.Foreground", text)
        self.root.option_add("*Text.insertBackground", text)
        app_font = ("Segoe UI Variable", 10)
        heading_font = ("Segoe UI Variable", 10, "bold")
        hero_font = ("Segoe UI Variable", 17, "bold")
        small_font = ("Segoe UI Variable", 9)

        style.configure(".", font=app_font)
        style.configure(".", background=base_bg, foreground=text, fieldbackground=field_bg)
        style.map(".", foreground=[("disabled", "#64748b")])
        style.configure("TFrame", background=base_bg)
        style.configure("App.TFrame", background=base_bg)
        style.configure("Header.TFrame", background=header_bg)
        style.configure("Workspace.TFrame", background=base_bg)
        style.configure("TLabel", background=base_bg, foreground=text)

        style.configure(
            "Heading.TLabel",
            background=base_bg,
            foreground=text,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Panel.TLabel",
            background=panel_bg,
            foreground=text,
        )

        style.configure(
            "PanelHeading.TLabel",
            background=panel_bg,
            foreground=text,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "PanelMuted.TLabel",
            background=panel_bg,
            foreground=muted,
        )

        style.configure(
            "Missing.TLabel",
            background=base_bg,
            foreground=missing_contact_text,
        )

        style.configure(
            "StatusOk.TLabel",
            background=base_bg,
            foreground=success,
        )

        style.configure(
            "StatusWarn.TLabel",
            background=base_bg,
            foreground=warning,
        )

        style.configure(
            "PanelHeader.TLabel",
            background=panel_bg,
            foreground=text,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TLabelframe",
            background=panel_bg,
            bordercolor=subtle_border,
            lightcolor=subtle_border,
            darkcolor=subtle_border,
            relief=tk.FLAT
        )
        style.configure("TLabelframe.Label", background=panel_bg, foreground=text, font=heading_font)
        style.configure("Panel.TLabelframe", background=panel_bg, bordercolor=border, lightcolor=border, darkcolor=border, relief=tk.FLAT)
        style.configure(
            "Panel.TLabelframe.Label",
            background=panel_bg,
            foreground=text,
            font=heading_font,
        )
        style.configure("Hero.TLabel", background=header_bg, foreground="#ffffff", font=hero_font)
        style.configure("HeroSub.TLabel", background=header_bg, foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure(
            "Muted.TLabel",
            background=base_bg,
            foreground=muted,
        )
        style.configure(
            "PanelMuted.TLabel",
            background=panel_bg,
            foreground=muted,
        )
        style.configure("ClientCard.TFrame", background=surface_bg, borderwidth=1, relief=tk.SOLID)
        style.configure("SelectedClientCard.TFrame", background=selected_surface, borderwidth=1, relief=tk.SOLID)
        style.configure("ClientCard.TLabel", background=surface_bg, foreground=text)
        style.configure("SelectedClientCard.TLabel", background=selected_surface, foreground=text)
        style.configure("ClientName.TLabel", background=surface_bg, foreground="#ffffff", font=heading_font)
        style.configure("SelectedClientName.TLabel", background=selected_surface, foreground="#ffffff", font=heading_font)
        style.configure("ClientMeta.TLabel", background=surface_bg, foreground=muted, font=("Segoe UI", 9))
        style.configure("SelectedClientMeta.TLabel", background=selected_surface, foreground="#bfdbfe", font=("Segoe UI", 9))
        style.configure("ClientEmpty.TLabel", background=field_bg, foreground=muted, font=("Segoe UI", 10))
        style.configure("TNotebook", background=base_bg, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=(10, 5),
            font=heading_font,
            background=surface_bg,
            foreground=muted,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", panel_bg), ("active", surface_bg)],
            foreground=[("selected", text), ("active", "#ffffff")],
        )
        style.configure(
            "TButton",
            background=surface_bg,
            foreground=text,
            bordercolor=border,
            lightcolor=subtle_border,
            darkcolor=subtle_border,
            padding=(7, 3),
            relief=tk.SOLID,
        )
        style.map(
            "TButton",
            background=[
                ("active", "#273449"),
                ("pressed", "#334155"),
                ("disabled", "#121821"),
            ],
            bordercolor=[
                ("focus", accent),
                ("active", accent),
                ("disabled", "#1f2937"),
            ],
            foreground=[
                ("disabled", "#64748b"),
                ("!disabled", text),
            ],
        )
        style.configure("Primary.TButton", font=heading_font, padding=(9, 5))
        style.map(
            "Primary.TButton",
            background=[
                ("active", accent_active),
                ("pressed", "#0ea5e9"),
                ("!disabled", accent),
            ],
            foreground=[
                ("disabled", "#64748b"),
                ("!disabled", "#06111f"),
            ],
        )
        style.configure("Secondary.TButton", padding=(8, 4))
        style.configure("TCheckbutton", background=panel_bg, foreground=text, padding=(2, 1))
        style.map(
            "TCheckbutton",
            background=[("active", panel_bg)],
            foreground=[("active", "#ffffff"), ("disabled", "#64748b")],
        )
        style.configure("TRadiobutton", background=panel_bg, foreground=text, padding=(2, 1))
        style.map(
            "TRadiobutton",
            background=[("active", panel_bg)],
            foreground=[("active", "#ffffff"), ("disabled", "#64748b")],
        )
        style.configure(
            "Invalid.TRadiobutton",
            background=panel_bg,
            foreground=error,
            padding=(2, 1),
        )

        style.map(
            "Invalid.TRadiobutton",
            background=[("active", panel_bg)],
            foreground=[("active", error), ("disabled", "#64748b")],
        )
        style.configure(
            "TEntry",
            fieldbackground=field_bg,
            foreground=text,
            insertcolor=text,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            padding=(5, 3),
            relief=tk.SOLID,
        )
        style.map(
            "TEntry",
            bordercolor=[("invalid", error), ("focus", accent_active), ("disabled", "#1f2937")],
            lightcolor=[("invalid", error), ("focus", accent_active), ("disabled", "#1f2937")],
            darkcolor=[("invalid", error), ("focus", accent_active), ("disabled", "#1f2937")],
            fieldbackground=[("focus", focus_bg), ("disabled", "#111827"), ("readonly", field_bg)],
            foreground=[("disabled", "#64748b"), ("!disabled", text)],
        )
        style.configure(
            "Placeholder.TEntry",
            fieldbackground=field_bg,
            foreground=muted,
            insertcolor=text,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            padding=(5, 3),
            relief=tk.SOLID,
        )
        style.map(
            "Placeholder.TEntry",
            bordercolor=[("focus", accent_active), ("disabled", "#1f2937")],
            lightcolor=[("focus", accent_active), ("disabled", "#1f2937")],
            darkcolor=[("focus", accent_active), ("disabled", "#1f2937")],
            fieldbackground=[("focus", focus_bg), ("disabled", "#111827")],
            foreground=[("disabled", "#64748b"), ("!disabled", muted)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=field_bg,
            background=surface_bg,
            foreground=text,
            arrowcolor=text,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            padding=(5, 3),
            relief=tk.SOLID,
        )
        style.map(
            "TCombobox",
            bordercolor=[("invalid", error), ("focus", accent_active), ("disabled", "#1f2937")],
            lightcolor=[("invalid", error), ("focus", accent_active), ("disabled", "#1f2937")],
            darkcolor=[("invalid", error), ("focus", accent_active), ("disabled", "#1f2937")],
            fieldbackground=[("focus", focus_bg), ("readonly", field_bg), ("disabled", "#111827")],
            foreground=[("readonly", text), ("disabled", "#64748b")],
            selectbackground=[("readonly", field_bg)],
            selectforeground=[("readonly", text)],
        )
        style.configure("TProgressbar", background=accent, troughcolor=field_bg, bordercolor=border)
        style.configure("TPanedwindow", background=base_bg)
        style.configure("Status.TLabel", background=surface_bg, foreground=text, padding=(6, 3))
        tree_options = {
            "background": field_bg,
            "fieldbackground": field_bg,
            "foreground": text,
            "rowheight": 24,
            "bordercolor": border,
            "lightcolor": border,
            "darkcolor": border,
            "borderwidth": 1,
            "relief": tk.SOLID,
        }
        heading_options = {
            "background": surface_bg,
            "foreground": "#e2e8f0",
            "font": ("Segoe UI Variable", 10, "bold"),
            "bordercolor": subtle_border,
            "lightcolor": subtle_border,
            "darkcolor": subtle_border,
            "borderwidth": 0,
            "relief": tk.FLAT,
            "padding": (8, 5),
        }
        style.configure("Treeview", **tree_options)
        style.configure("Treeview.Heading", **heading_options)
        style.map("Treeview", background=[("selected", selected)], foreground=[("selected", "#ffffff")])
        style.configure("Bordered.Treeview", **tree_options)
        style.configure("Bordered.Treeview.Heading", **heading_options)
        style.map("Bordered.Treeview", background=[("selected", selected)], foreground=[("selected", "#ffffff")])

    def bind_focus_highlight(self, widget, *, readonly=False):
        """Give classic Tk input widgets a visible accent focus ring."""

        colors = self.theme_colors
        normal_bg = colors["surface_bg"] if readonly else colors["field_bg"]
        focus_bg = colors["surface_bg"] if readonly else colors["focus_bg"]

        def on_focus_in(_event):
            widget.configure(
                background=focus_bg,
                highlightthickness=2,
                highlightbackground=colors["accent_active"],
                highlightcolor=colors["accent_active"],
            )

        def on_focus_out(_event):
            widget.configure(
                background=normal_bg,
                highlightthickness=1,
                highlightbackground=colors["border"],
                highlightcolor=colors["accent"],
            )

        widget.bind("<FocusIn>", on_focus_in, add="+")
        widget.bind("<FocusOut>", on_focus_out, add="+")

    def apply_text_widget_theme(self, widget, *, readonly=False):
        """Style classic Tk text-like widgets that do not inherit ttk colors."""

        colors = self.theme_colors
        widget.configure(
            background=colors["field_bg"] if not readonly else colors["surface_bg"],
            foreground=colors["text"],
            insertbackground=colors["text"],
            selectbackground=colors["selected"],
            selectforeground="#ffffff",
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=colors["border"],
            highlightcolor=colors["accent"],
        )
        self.bind_focus_highlight(widget, readonly=readonly)

    def apply_listbox_theme(self, widget):
        """Style classic Tk listboxes for the dark theme."""

        colors = self.theme_colors
        widget.configure(
            background=colors["field_bg"],
            foreground=colors["text"],
            selectbackground=colors["selected"],
            selectforeground="#ffffff",
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=colors["border"],
            highlightcolor=colors["accent"],
            activestyle="none",
        )
        self.bind_focus_highlight(widget)

    def apply_classic_widget_theme(self, widget):
        """Apply the dark theme to classic Tk widgets inside a container."""

        colors = self.theme_colors
        widget_class = widget.winfo_class()
        if widget_class == "Text":
            self.apply_text_widget_theme(
                widget,
                readonly=str(widget.cget("state")) == tk.DISABLED,
            )
        elif widget_class == "Listbox":
            self.apply_listbox_theme(widget)
        elif widget_class in {"Frame", "Toplevel", "Tk"}:
            widget.configure(background=colors["base_bg"])
        elif widget_class == "Label":
            widget.configure(
                background=colors["base_bg"],
                foreground=colors["text"],
                font=("Segoe UI", 10),
            )
        elif widget_class == "Entry":
            widget.configure(
                background=colors["field_bg"],
                foreground=colors["text"],
                insertbackground=colors["text"],
                selectbackground=colors["selected"],
                selectforeground="#ffffff",
                relief=tk.SOLID,
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=colors["border"],
                highlightcolor=colors["accent"],
            )
            self.bind_focus_highlight(widget)
        elif widget_class == "Button":
            widget.configure(
                background=colors["surface_bg"],
                foreground=colors["text"],
                activebackground="#273449",
                activeforeground="#ffffff",
                relief=tk.SOLID,
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=colors["border"],
            )

        for child in widget.winfo_children():
            self.apply_classic_widget_theme(child)

    def set_initial_window_size(self):
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        min_width = min(820, screen_width)
        min_height = min(500, screen_height)

        self.root.minsize(min_width, min_height)

        # Open using the full available screen size
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Maximize the window when supported, mainly Windows
        try:
            self.root.state("zoomed")
        except Exception:
            pass
    def load_json(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror(
                    "Error", "File {filename} corrupt. Using empty data."
                )
                return []
        return []
    def save_json(self, filename, data):
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            messagebox.showerror(
                "Error",
                f"File cannot be loaded: {filename}: {str(e)}",
                parent=self.root,
            )
            return False
    def get_audit_csv_path(self):
        username = getpass.getuser()
        invalid_chars = '<>:"/\\|?*'
        safe_username = "".join(
            "_" if char in invalid_chars or ord(char) < 32 else char
            for char in username
        ).strip(" .")
        if not safe_username:
            safe_username = "user"
        return Path.home() / AUDIT_ONEDRIVE_ORG / AUDIT_FOLDER_NAME / f"{safe_username}.csv"
    def flatten_audit_csv_value(self, value):
        if value is None:
            return ""
        return " ".join(str(value).splitlines())
    def build_audit_csv_rows(self):
        return [
            {
                column: self.flatten_audit_csv_value(note.get(column, ""))
                for column in AUDIT_COLUMNS
            }
            for note in self.notes
        ]
    def refresh_audit_csv(self):
        tmp_path = None
        try:
            onedrive_root = Path.home() / AUDIT_ONEDRIVE_ORG
            if not onedrive_root.is_dir():
                return
            audit_path = self.get_audit_csv_path()
            audit_path.parent.mkdir(exist_ok=True)
            tmp_path = audit_path.with_suffix(audit_path.suffix + ".tmp")
            with open(tmp_path, "w", newline="", encoding="utf-8-sig") as audit_file:
                writer = csv.DictWriter(
                    audit_file,
                    fieldnames=AUDIT_COLUMNS,
                    delimiter=AUDIT_CSV_DELIMITER,
                    extrasaction="ignore",
                    restval="",
                )
                writer.writeheader()
                writer.writerows(self.build_audit_csv_rows())
            tmp_path.replace(audit_path)
        except Exception:
            if tmp_path is not None:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass
    def format_name(self, widget):
        text = widget.get().strip()
        if text:
            formatted_name = " ".join(word.capitalize() for word in text.split())
            if text != formatted_name:
                widget.delete(0, tk.END)
                widget.insert(0, formatted_name)
    def format_text_upper(self, widget):
        text = widget.get().strip()
        if text:
            formatted_text = text.upper()
            if text != formatted_text:
                widget.delete(0, tk.END)
                widget.insert(0, formatted_text)
    def format_phone(self, widget):
        text = (
            widget.get()
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
            if isinstance(widget, ttk.Entry)
            else widget.get("1.0", tk.END).strip()
        )
        if not text.isdigit() and len(text) != 0:
            messagebox.showwarning(
                "Error", "Please enter numbers only in the phone field."
            )
            widget.delete(0, tk.END)
            widget.focus()
            return
        if len(text) <= 10:
            if len(text) > 6:
                formatted = f"({text[:3]}) {text[3:6]}-{text[6:]}"
            elif len(text) > 3:
                formatted = f"({text[:3]}) {text[3:]}"
            else:
                formatted = f"({text}"
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, formatted)
            else:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", formatted)
            if len(text) == 0:
                widget.delete(0, tk.END)

    def add_entry_placeholder(self, entry, placeholder):
        entry.placeholder_text = placeholder
        entry.placeholder_visible = False

        def on_focus_in(_event):
            if getattr(entry, "placeholder_visible", False):
                entry.delete(0, tk.END)
                entry.placeholder_visible = False
                entry.configure(style="TEntry")

        def on_focus_out(_event):
            if not entry.get().strip():
                self.show_entry_placeholder(entry)

        entry.bind("<FocusIn>", on_focus_in, add="+")
        entry.bind("<FocusOut>", on_focus_out, add="+")
        self.show_entry_placeholder(entry)

    def show_entry_placeholder(self, entry):
        placeholder = getattr(entry, "placeholder_text", "")
        if not placeholder:
            return
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.placeholder_visible = True
        entry.configure(style="Placeholder.TEntry")

    def set_placeholder_entry_value(self, entry, value=""):
        entry.placeholder_visible = False
        entry.configure(style="TEntry")
        entry.delete(0, tk.END)
        value = str(value or "").strip()
        if value:
            entry.insert(0, value)
        else:
            self.show_entry_placeholder(entry)

    def get_placeholder_entry_value(self, entry):
        if getattr(entry, "placeholder_visible", False):
            return ""
        return entry.get().strip()

    def sync_verified_from_downcode(self, form, entry_name, variable_name):
        if self.get_placeholder_entry_value(form[entry_name]):
            form[variable_name].set(True)

    def get_current_form(self):
        return self.active_form if self.active_form is not None else (
            self.entry_tabs[0] if self.entry_tabs else None
        )

    def set_status(self, message, kind="ok"):
        if hasattr(self, "workspace_status_var"):
            self.workspace_status_var.set(message)
        if hasattr(self, "workspace_status_label"):
            style = "StatusWarn.TLabel" if kind == "warn" else "StatusOk.TLabel"
            self.workspace_status_label.configure(style=style)

    def set_widget_invalid(self, widget, invalid):
        if widget is None:
            return
        if isinstance(widget, ttk.Entry):
            widget.state(["invalid"] if invalid else ["!invalid"])
        elif isinstance(widget, tk.Text):
            colors = self.theme_colors
            widget.configure(
                highlightbackground=colors.get("error", "#f87171") if invalid else colors["border"],
                highlightcolor=colors.get("error", "#f87171") if invalid else colors["accent"],
                highlightthickness=2 if invalid else 1,
            )

    def set_validation_state(self, form, errors):
        required_widgets = form.get("required_widgets", {})

        for field_name, widget in required_widgets.items():
            self.set_widget_invalid(widget, field_name in errors)

        network_invalid = "Network Status" in errors
        for radio in form.get("network_radios", []):
            radio.configure(
                style="Invalid.TRadiobutton" if network_invalid else "TRadiobutton"
            )

        if form.get("validation_var"):
            if errors:
                message = "Missing: " + ", ".join(errors)
                if len(message) > 58:
                    message = message[:55].rstrip() + "..."
                form["validation_var"].set(message)
            else:
                form["validation_var"].set("All required fields are ready.")

    def update_form_state(self, form=None):
        form = form or self.get_current_form()
        if not form:
            return
        errors = self.validate_mandatory_fields(form)
        self.set_validation_state(form, errors)
        if form.get("note_preview_text"):
            self.refresh_live_preview(form, errors)
        has_preview = bool(form["note_preview_text"].get("1.0", tk.END).strip())
        if form.get("submit_button"):
            form["submit_button"].config(state=tk.NORMAL if not errors and has_preview else tk.DISABLED)
        self.refresh_workspace_context()

    def clear_claim_fields_after_save(self, form):
        for entry_name in (
            "cm_ref_entry",
            "plan_type_entry",
            "specialty_entry",
            "pos_entry",
            "cc_name_entry",
            "effective_date_entry",
            "em_change_entry",
            "emer_change_entry",
            "drg_change_entry",
        ):
            form[entry_name].delete(0, tk.END)
        for text_name in (
            "contract_comment_entry",
            "action_note_text",
            "note_preview_text",
        ):
            form[text_name].delete("1.0", tk.END)
        form["network_var"].set("")
        form["em_verified_var"].set(False)
        form["emer_verified_var"].set(False)
        form["drg_verified_var"].set(False)
        for entry_name in ("em_change_entry", "emer_change_entry", "drg_change_entry"):
            self.set_placeholder_entry_value(form[entry_name])
        form["undo_stack"].clear()
        form["redo_stack"].clear()

    def add_new_call_tab(self):
        if self.active_form is None:
            self.create_workspace_tab()
        else:
            self.reset_fields(self.active_form)
        self.notebook.select(self.workspace_tab)
        self.set_status("Ready for a new follow-up.")
        self.refresh_workspace_context()
        return self.active_form
    def close_current_tab(self):
        if self.active_form is not None:
            self.reset_fields(self.active_form)
            self.notebook.select(self.workspace_tab)
            self.set_status("Current follow-up cleared.")
            self.refresh_workspace_context()

    def create_workspace_tab(self):
        workspace = ttk.Frame(self.workspace_tab, style="Workspace.TFrame")
        workspace.pack(fill="both", expand=True)
        RIGHT_PANEL_WIDTH = 250

        workspace.columnconfigure(0, weight=1, minsize=900)
        workspace.columnconfigure(1, weight=0, minsize=RIGHT_PANEL_WIDTH)
        workspace.rowconfigure(0, weight=1)

        form_host = ttk.Frame(workspace)
        form_host.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        context_host = ttk.Frame(workspace, width=RIGHT_PANEL_WIDTH)
        context_host.grid(row=0, column=1, sticky="ns", padx=(4, 0))
        context_host.grid_propagate(False)

        form = self.create_entry_form(form_host)
        self.active_form = form
        self.entry_tabs = [form]
        self.create_context_panel(context_host, form)

        def layout_workspace(event=None):
            width = event.width if event else workspace.winfo_width()
            if width < 920:
                workspace.columnconfigure(0, weight=1, minsize=0)
                workspace.columnconfigure(1, weight=0, minsize=0)
                workspace.rowconfigure(0, weight=3)
                workspace.rowconfigure(1, weight=2)
                form_host.grid_configure(row=0, column=0, sticky="nsew", padx=0)
                context_host.grid_configure(row=1, column=0, sticky="nsew", padx=0, pady=(4, 0))
            else:
                workspace.columnconfigure(0, weight=1, minsize=900)
                workspace.columnconfigure(1, weight=0, minsize=RIGHT_PANEL_WIDTH)
                context_host.configure(width=RIGHT_PANEL_WIDTH)
                context_host.grid_propagate(False)
                workspace.rowconfigure(0, weight=1)
                workspace.rowconfigure(1, weight=0)
                form_host.grid_configure(row=0, column=0, sticky="nsew", padx=(0, 4), pady=0)
                context_host.grid_configure(row=0, column=1, sticky="nsew", padx=(4, 0), pady=0)

        workspace.bind("<Configure>", layout_workspace)
        self.refresh_workspace_context()
        self.update_form_state(form)
        return form

    def create_context_panel(self, parent, form):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        contacts_frame = ttk.LabelFrame(parent, text="Contacts", padding=4)
        contacts_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        contacts_frame.columnconfigure(1, weight=1)
        ttk.Label(contacts_frame, text="Search:", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        self.contact_search_var = tk.StringVar()
        contact_search = ttk.Entry(contacts_frame, textvariable=self.contact_search_var)
        contact_search.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.contact_search_var.trace_add("write", lambda *_: self.refresh_contacts_panel())
        self.context_contacts = ttk.Treeview(
            contacts_frame,
            columns=("Phone", "Payer"),
            show="headings",
            height=4,
        )
        self.context_contacts.heading("Phone", text="Phone")
        self.context_contacts.heading("Payer", text="Payer")
        self.context_contacts.column("Phone", width=100, minwidth=80, stretch=False)
        self.context_contacts.column("Payer", width=100, minwidth=80, stretch=True)
        self.context_contacts.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=3)
        contacts_scrollbar = ttk.Scrollbar(
            contacts_frame, orient="vertical", command=self.context_contacts.yview
        )
        contacts_scrollbar.grid(row=1, column=2, sticky="ns", pady=4)
        self.context_contacts.configure(yscrollcommand=contacts_scrollbar.set)
        contact_buttons = ttk.Frame(contacts_frame)
        contact_buttons.grid(row=2, column=0, columnspan=2, sticky="ew")
        contact_buttons.columnconfigure(0, weight=1)
        contact_buttons.columnconfigure(1, weight=1)
        ttk.Button(contact_buttons, text="Use", command=self.use_context_contact).grid(
            row=0, column=0, sticky="ew", padx=(0, 3)
        )

        ttk.Button(contact_buttons, text="Save", command=lambda: self.save_contact(form)).grid(
            row=0, column=1, sticky="ew", padx=(3, 0)
        )

        quick_frame = ttk.LabelFrame(parent, text="Quick Notes", padding=4)
        quick_frame.grid(row=1, column=0, sticky="nsew")
        quick_frame.columnconfigure(1, weight=1)
        quick_frame.rowconfigure(1, weight=1)
        ttk.Label(quick_frame, text="Search:", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        self.quick_note_search_var = tk.StringVar()
        quick_search = ttk.Entry(quick_frame, textvariable=self.quick_note_search_var)
        quick_search.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.quick_note_search_var.trace_add("write", lambda *_: self.refresh_quick_notes_panel())
        self.context_quick_note_values = []
        self.context_quick_note_selected_index = None
        colors = self.theme_colors
        self.context_quick_notes = tk.Canvas(
            quick_frame,
            background=colors["field_bg"],
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=colors["border"],
        )
        self.context_quick_notes.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=3)
        quick_notes_scrollbar = ttk.Scrollbar(
            quick_frame, orient="vertical", command=self.context_quick_notes.yview
        )
        quick_notes_scrollbar.grid(row=1, column=2, sticky="ns", pady=4)
        self.context_quick_notes.configure(yscrollcommand=quick_notes_scrollbar.set)
        self.context_quick_notes_frame = ttk.Frame(self.context_quick_notes)
        self.context_quick_notes_window = self.context_quick_notes.create_window(
            (0, 0), window=self.context_quick_notes_frame, anchor="nw"
        )
        self.context_quick_notes_frame.bind(
            "<Configure>",
            lambda _event: self.context_quick_notes.configure(
                scrollregion=self.context_quick_notes.bbox("all")
            ),
        )
        self.context_quick_notes.bind(
            "<Configure>",
            lambda event: self.context_quick_notes.itemconfigure(
                self.context_quick_notes_window, width=event.width
            ),
        )
        self.context_quick_notes.bind(
            "<MouseWheel>",
            lambda event: self.context_quick_notes.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )
        quick_buttons = ttk.Frame(quick_frame)
        quick_buttons.grid(row=2, column=0, columnspan=2, sticky="ew")
        quick_buttons.columnconfigure(0, weight=1)
        quick_buttons.columnconfigure(1, weight=1)
        quick_buttons.columnconfigure(2, weight=1)
        ttk.Button(quick_buttons, text="Insert", command=self.use_context_quick_note).grid(
            row=0, column=0, sticky="ew", padx=(0, 2)
        )
        ttk.Button(quick_buttons, text="Save", command=lambda: self.add_quick_note(form)).grid(
            row=0, column=1, sticky="ew", padx=2
        )
        ttk.Button(quick_buttons, text="Del", command=self.delete_context_quick_note).grid(
            row=0, column=2, sticky="ew", padx=(2, 0)
        )

        self.apply_classic_widget_theme(parent)
        self.refresh_workspace_context()

    def refresh_workspace_context(self):
        if hasattr(self, "context_contacts"):
            self.refresh_contacts_panel()
        if hasattr(self, "context_quick_notes"):
            self.refresh_quick_notes_panel()

    def refresh_contacts_panel(self):
        search = getattr(self, "contact_search_var", tk.StringVar()).get().lower()
        for item in self.context_contacts.get_children():
            self.context_contacts.delete(item)
        for contact in self.contacts:
            haystack = f"{contact.get('phone', '')} {contact.get('payer', '')}".lower()
            if not search or search in haystack:
                self.context_contacts.insert("", "end", values=(contact.get("phone", ""), contact.get("payer", "")))

    def refresh_quick_notes_panel(self):
        search = getattr(self, "quick_note_search_var", tk.StringVar()).get().lower()
        for widget in self.context_quick_notes_frame.winfo_children():
            widget.destroy()
        self.context_quick_note_selected_index = None
        self.context_quick_note_values = [
            note for note in self.quick_notes if not search or search in str(note).lower()
        ]
        if not self.context_quick_note_values:
            ttk.Label(
                self.context_quick_notes_frame,
                text="No quick notes found.",
                style="ClientEmpty.TLabel",
                padding=8,
            ).grid(row=0, column=0, sticky="ew", padx=3, pady=3)
            return
        for index, note in enumerate(self.context_quick_note_values):
            self.create_quick_note_row(index, note)

    def create_quick_note_row(self, index, note):
        colors = self.theme_colors
        selected = index == self.context_quick_note_selected_index
        row = tk.Frame(
            self.context_quick_notes_frame,
            background=colors["selected"] if selected else colors["surface_bg"],
            highlightthickness=1,
            highlightbackground=colors["accent"] if selected else colors["border"],
            borderwidth=0,
        )
        row.grid(row=index, column=0, sticky="ew", padx=3, pady=2)
        self.context_quick_notes_frame.columnconfigure(0, weight=1)
        preview = self.format_quick_note_preview(note)
        label = tk.Label(
            row,
            text=preview,
            background=colors["selected"] if selected else colors["surface_bg"],
            foreground="#ffffff" if selected else colors["text"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            height=2,
            wraplength=170,
        )
        label.pack(fill="x", padx=6, pady=4)
        for widget in (row, label):
            widget.bind("<Button-1>", lambda _event, idx=index: self.select_context_quick_note(idx))
            widget.bind("<Double-Button-1>", lambda _event, idx=index: self.use_context_quick_note(idx))

    def format_quick_note_preview(self, note):
        lines = [line.strip() for line in str(note).splitlines() if line.strip()]
        if not lines:
            lines = [str(note).strip()]
        preview_lines = lines[:2]
        if len(lines) > 2:
            preview_lines[-1] = preview_lines[-1].rstrip() + "..."
        return "\n".join(preview_lines)

    def select_context_quick_note(self, index):
        self.context_quick_note_selected_index = index
        for row_index, row in enumerate(self.context_quick_notes_frame.winfo_children()):
            selected = row_index == index
            bg = self.theme_colors["selected"] if selected else self.theme_colors["surface_bg"]
            fg = "#ffffff" if selected else self.theme_colors["text"]
            row.configure(
                background=bg,
                highlightbackground=self.theme_colors["accent"] if selected else self.theme_colors["border"],
            )
            for child in row.winfo_children():
                child.configure(background=bg, foreground=fg)

    def use_context_contact(self):
        selected = self.context_contacts.selection()
        form = self.get_current_form()
        if selected and form:
            phone, payer = self.context_contacts.item(selected[0])["values"]
            form["phone_entry"].delete(0, tk.END)
            form["phone_entry"].insert(0, phone)
            form["payer_entry"].delete(0, tk.END)
            form["payer_entry"].insert(0, payer)
            self.update_form_state(form)
            self.set_status("Contact inserted.")

    def use_context_quick_note(self, index=None):
        selected_index = self.context_quick_note_selected_index if index is None else index
        if selected_index is not None and 0 <= selected_index < len(self.context_quick_note_values):
            self.insert_quick_note(self.context_quick_note_values[selected_index])
            self.update_form_state()
            self.set_status("Quick note inserted.")

    def delete_context_quick_note(self):
        selected_index = self.context_quick_note_selected_index
        if selected_index is not None and 0 <= selected_index < len(self.context_quick_note_values):
            note = self.context_quick_note_values[selected_index]
            self.quick_notes = [item for item in self.quick_notes if item != note]
            self.save_json(QUICK_NOTES_FILE, self.quick_notes)
            self.refresh_quick_notes_panel()
            self.set_status("Quick note deleted.")

    def create_entry_form(self, parent):
        def disable_enter(event):
            return "break"
        form = {"undo_stack": [], "redo_stack": []}
        form["validation_var"] = tk.StringVar(value="Complete the required fields to generate a preview.")
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)
        scroll_area = ttk.Frame(container)
        scroll_area.pack(side="top", fill="both", expand=True)
        canvas = tk.Canvas(
            scroll_area,
            background=self.theme_colors["base_bg"],
            highlightthickness=0,
            borderwidth=0,
        )
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        main_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_frame_width(event):
            canvas.itemconfigure(
                canvas_window,
                width=event.width,
                height=max(event.height, main_frame.winfo_reqheight()),
            )
            apply_layout = form.get("_apply_responsive_layout")
            if apply_layout:
                apply_layout(event.width)

        def scroll_with_mousewheel(event):
            widget = canvas.winfo_containing(event.x_root, event.y_root)
            while widget is not None:
                if widget == canvas:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    return
                widget = getattr(widget, "master", None)

        main_frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", fit_frame_width)
        canvas.bind_all("<MouseWheel>", scroll_with_mousewheel)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=0)
        main_frame.grid_rowconfigure(4, weight=1)
        call_frame = ttk.LabelFrame(
            main_frame,
            text="Contact and Call",
            padding=3,
        )
        call_frame.grid(row=0, column=0, padx=3, pady=2, sticky="nsew")
        for col in range(4):
            call_frame.columnconfigure(col, weight=1)
        form["follow_up_var"] = tk.StringVar(value="PH")
        ttk.Label(call_frame, text="Follow-up Type:", style="Panel.TLabel").grid(
            row=0, column=0, sticky="e"
        )
        ttk.Radiobutton(
            call_frame, text="PHONE", variable=form["follow_up_var"], value="PH",
        ).grid(row=0, column=1, sticky="e")
        ttk.Radiobutton(
            call_frame, text="CHAT", variable=form["follow_up_var"], value="CH"
        ).grid(row=0, column=2, sticky="we")
        ttk.Radiobutton(
            call_frame, text="APPEAL", variable=form["follow_up_var"], value="APP"
        ).grid(row=0, column=3, sticky="w")
        ttk.Label(call_frame, text="CM Reference #:", style="Panel.TLabel").grid(
            row=1, column=0, sticky="e"
        )
        form["cm_ref_entry"] = ttk.Entry(call_frame)
        form["cm_ref_entry"].grid(row=1, column=1, columnspan=3, sticky="ew")
        ttk.Label(call_frame, text="Phone Number:", style="Panel.TLabel").grid(
            row=2, column=0, sticky="e"
        )
        form["phone_entry"] = ttk.Entry(call_frame)
        form["phone_entry"].grid(row=2, column=1, columnspan=3, sticky="ew")
        form["phone_entry"].bind(
            "<KeyRelease>", lambda e: self.format_phone(form["phone_entry"])
        )
        ttk.Label(call_frame, text="Payer Name:", style="Panel.TLabel").grid(
            row=3, column=0, sticky="e"
        )
        form["payer_entry"] = ttk.Entry(call_frame)
        form["payer_entry"].grid(row=3, column=1, columnspan=3, sticky="ew")
        form["payer_entry"].bind(
            "<KeyRelease>", lambda e: self.format_text_upper(form["payer_entry"])
        )
        ttk.Label(call_frame, text="Agent Name:", style="Panel.TLabel").grid(
            row=4, column=0, sticky="e"
        )
        form["agent_entry"] = ttk.Entry(call_frame)
        form["agent_entry"].grid(row=4, column=1, columnspan=3, sticky="ew")
        form["agent_entry"].bind(
            "<KeyRelease>", lambda e: self.format_name(form["agent_entry"])
        )
        ttk.Label(call_frame, text="Call Reference #:", style="Panel.TLabel").grid(
            row=5, column=0, sticky="e"
        )
        form["call_ref_entry"] = ttk.Entry(call_frame)
        form["call_ref_entry"].grid(row=5, column=1, columnspan=3, sticky="ew")
        mandatory_frame = ttk.LabelFrame(
            main_frame, text="Mandatory Checklist", padding=3
        )
        mandatory_frame.grid(row=0, column=1, padx=3, pady=2, sticky="nsew")
        for col in range(4):
            mandatory_frame.columnconfigure(col, weight=1 if col in (1, 3) else 0)
        
        form["network_var"] = tk.StringVar(value="")

        ttk.Label(mandatory_frame, text="Network Status:", style="Panel.TLabel").grid(
            row=0, column=0, sticky="e", padx=(0, 3)
        )

        form["network_radios"] = []

        network_inn = ttk.Radiobutton(
            mandatory_frame,
            text="INN",
            variable=form["network_var"],
            value="INN",
        )
        network_inn.grid(row=0, column=1, sticky="w")
        form["network_radios"].append(network_inn)

        network_oon = ttk.Radiobutton(
            mandatory_frame,
            text="OON",
            variable=form["network_var"],
            value="OON",
        )
        network_oon.grid(row=0, column=2, sticky="e")
        form["network_radios"].append(network_oon)

        network_na = ttk.Radiobutton(
            mandatory_frame,
            text="N/A",
            variable=form["network_var"],
            value="N/A",
        )
        network_na.grid(row=0, column=3, sticky="w")
        form["network_radios"].append(network_na)


        ttk.Label(mandatory_frame, text="Member's Plan Type:", style="Panel.TLabel").grid(
            row=1, column=0, sticky="e", padx=(0, 3)
        )
        form["plan_type_entry"] = ttk.Entry(mandatory_frame)
        form["plan_type_entry"].grid(row=1, column=1, sticky="ew")
        form["plan_type_entry"].bind(
            "<KeyRelease>", lambda e: self.format_text_upper(form["plan_type_entry"])
        )
        ttk.Label(mandatory_frame, text="Provider Specialty:", style="Panel.TLabel").grid(
            row=2, column=0, sticky="e", padx=(0, 3)
        )
        form["specialty_entry"] = ttk.Entry(mandatory_frame)
        form["specialty_entry"].grid(row=2, column=1, sticky="ew")
        ttk.Label(mandatory_frame, text="Place Of Service:", style="Panel.TLabel").grid(
            row=3, column=0, sticky="e", padx=(0, 3)
        )
        form["pos_entry"] = ttk.Entry(mandatory_frame)
        form["pos_entry"].grid(row=3, column=1, sticky="ew")
        form["em_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            mandatory_frame, text="E&M verified", variable=form["em_verified_var"]
        ).grid(row=1, column=2, sticky="w", padx=(8, 3))
        ttk.Label(mandatory_frame, text="Downcoded to:", style="Panel.TLabel").grid(
            row=1, column=3, sticky="w", padx=(0, 3)
        )
        form["em_change_entry"] = ttk.Entry(mandatory_frame)
        form["em_change_entry"].grid(row=2, column=2, columnspan=2, sticky="ew", padx=(8, 0))
        self.add_entry_placeholder(form["em_change_entry"], "Optional downcoded E&M code")
        form["emer_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            mandatory_frame,
            text="Emergency verified",
            variable=form["emer_verified_var"],
        ).grid(row=3, column=2, sticky="w", padx=(8, 3))
        ttk.Label(mandatory_frame, text="Downcoded to:", style="Panel.TLabel").grid(
            row=3, column=3, sticky="w", padx=(0, 3)
        )
        form["emer_change_entry"] = ttk.Entry(mandatory_frame)
        form["emer_change_entry"].grid(row=4, column=2, columnspan=2, sticky="ew", padx=(8, 0))
        self.add_entry_placeholder(form["emer_change_entry"], "Optional downcoded emergency code")
        form["drg_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            mandatory_frame, text="DRG verified", variable=form["drg_verified_var"]
        ).grid(row=5, column=2, sticky="w", padx=(8, 3))
        ttk.Label(mandatory_frame, text="Downcoded to:", style="Panel.TLabel").grid(
            row=5, column=3, sticky="w", padx=(0, 3)
        )
        form["drg_change_entry"] = ttk.Entry(mandatory_frame)
        form["drg_change_entry"].grid(row=6, column=2, columnspan=2, sticky="ew", padx=(8, 0))
        self.add_entry_placeholder(form["drg_change_entry"], "Optional downcoded DRG code")
        appeal_frame = ttk.LabelFrame(main_frame, text="Appeal Methods", padding=3)
        appeal_frame.grid(row=1, column=0, padx=3, pady=2, sticky="nsew")
        for col in range(4):
            appeal_frame.columnconfigure(col, weight=1 if col in (1, 3) else 0)
        ttk.Label(appeal_frame, text="Online:", style="Panel.TLabel").grid(row=0, column=0, sticky="e", padx=(0, 3))
        form["online_entry"] = ttk.Entry(appeal_frame)
        form["online_entry"].grid(row=0, column=1, sticky="ew")
        ttk.Label(appeal_frame, text="Fax:", style="Panel.TLabel").grid(row=0, column=2, sticky="e", padx=(8, 3))
        form["fax_entry"] = ttk.Entry(appeal_frame)
        form["fax_entry"].grid(row=0, column=3, pady=2, sticky="ew")
        form["fax_entry"].bind(
            "<KeyRelease>", lambda e: self.format_phone(form["fax_entry"])
        )
        ttk.Label(appeal_frame, text="Attn to:", style="Panel.TLabel").grid(row=1, column=0, sticky="e", padx=(0, 3))
        form["attn_entry"] = ttk.Entry(appeal_frame)
        form["attn_entry"].grid(row=1, column=1, sticky="ew")
        form["prev_verified_var"] = tk.BooleanVar()
        ttk.Label(appeal_frame, text="Mail:", style="Panel.TLabel").grid(row=2, column=0, sticky="ne", padx=(0, 3))
        form["mail_entry"] = scrolledtext.ScrolledText(appeal_frame, height=1, width=24)
        form["mail_entry"].grid(row=2, column=1, columnspan=3, sticky="ew")
        form["mail_entry"].bind("<Return>", disable_enter)
        ttk.Checkbutton(
            appeal_frame, text="Previously Verified", variable=form["prev_verified_var"]
        ).grid(row=3, column=1, columnspan=3, sticky="w")
        contract_frame = ttk.LabelFrame(
            main_frame, text="Contract", padding=3
        )
        contract_frame.grid(row=1, column=1, padx=3, pady=2, sticky="nsew")
        for col in range(3):
            contract_frame.columnconfigure(col, weight=1)
        ttk.Label(contract_frame, text="CC Name:", style="Panel.TLabel").grid(row=0, column=0, sticky="e")
        form["cc_name_entry"] = ttk.Entry(contract_frame)
        form["cc_name_entry"].grid(row=0, column=1, columnspan=2, sticky="ew")
        ttk.Label(contract_frame, text="Effective Date:", style="Panel.TLabel").grid(
            row=1, column=0, sticky="e"
        )
        form["effective_date_entry"] = ttk.Entry(contract_frame)
        form["effective_date_entry"].grid(row=1, column=1, columnspan=2, sticky="ew")
        ttk.Label(contract_frame, text="Contract Comment:", style="Panel.TLabel").grid(
            row=2, column=0, sticky="e"
        )
        form["contract_comment_entry"] = scrolledtext.ScrolledText(
            contract_frame, height=1, width=24
        )
        form["contract_comment_entry"].grid(row=2, column=1, columnspan=2, sticky="ew")
        form["contract_comment_entry"].bind("<Return>", disable_enter)
        note_frame = ttk.LabelFrame(main_frame, text="Notes", padding=3)
        note_frame.grid(row=2, column=0, columnspan=2, padx=3, pady=2, sticky="nsew")
        note_frame.columnconfigure(0, weight=1)
        note_frame.columnconfigure(1, weight=2)
        note_frame.rowconfigure(0, weight=1)
        note_frame.rowconfigure(1, weight=1)
        action_frame = ttk.LabelFrame(note_frame, text="Action Note", padding=3)
        action_frame.grid(row=0, column=0, padx=3, pady=2, sticky="nsew")
        for col in range(3):
            action_frame.columnconfigure(col, weight=1)
        action_frame.rowconfigure(0, weight=1)
        form["action_note_text"] = scrolledtext.ScrolledText(
            action_frame, height=3, width=32
        )
        form["action_note_text"].grid(row=0, column=0, columnspan=3, sticky="nsew")
        form["action_note_text"].bind(
            "<KeyRelease>", lambda e: self.save_text_state(form, "action_note_text")
        )
        preview_frame = ttk.LabelFrame(note_frame, text="Final Note", padding=3)
        preview_frame.grid(row=1, column=0, padx=3, pady=2, sticky="nsew")
        for col in range(4):
            preview_frame.columnconfigure(col, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        form["note_preview_text"] = scrolledtext.ScrolledText(
            preview_frame, height=6, width=44
        )
        form["note_preview_text"].grid(row=0, column=0, columnspan=4, sticky="nsew")
        button_frame = ttk.Frame(container)
        button_frame.pack(side="bottom", fill="x", padx=3, pady=(0, 1))
        button_frame.columnconfigure(0, weight=0, minsize=260)
        button_frame.columnconfigure(1, weight=0, minsize=16)
        button_frame.columnconfigure(2, weight=1, minsize=360)
        button_frame.columnconfigure(3, weight=0, minsize=120)
        button_frame.columnconfigure(4, weight=0, minsize=120)
        self.workspace_status_var = tk.StringVar(value="Ready.")
        self.workspace_status_label = ttk.Label(
            button_frame,
            textvariable=self.workspace_status_var,
            style="StatusOk.TLabel",
            width=34,
            anchor="w",
        )
        self.workspace_status_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=3, pady=(0, 1))
        form["validation_label"] = ttk.Label(
            button_frame,
            textvariable=form["validation_var"],
            style="StatusWarn.TLabel",
            width=62,
            anchor="w",
        )
        form["validation_label"].grid(row=0, column=2, columnspan=3, sticky="w", padx=3, pady=(0, 1))
        form["submit_button"] = ttk.Button(
            button_frame,
            text="Save",
            command=lambda: self.submit_note(form),
            style="Primary.TButton",
        )
        action_buttons = [
            form["submit_button"],
            ttk.Button(button_frame, text="Clear Form", command=lambda: self.reset_fields(form)),
        ]

        def layout_action_buttons(is_narrow):
            for button in action_buttons:
                button.grid_forget()
            columns = 2 if is_narrow else len(action_buttons)
            if is_narrow:
                button_frame.columnconfigure(0, weight=1, minsize=0)
                button_frame.columnconfigure(1, weight=1, minsize=0)
                button_frame.columnconfigure(2, weight=1, minsize=0)
                button_frame.columnconfigure(3, weight=0, minsize=0)
                button_frame.columnconfigure(4, weight=0, minsize=0)
            else:
                button_frame.columnconfigure(0, weight=0, minsize=260)
                button_frame.columnconfigure(1, weight=0, minsize=16)
                button_frame.columnconfigure(2, weight=1, minsize=360)
                button_frame.columnconfigure(3, weight=0, minsize=120)
                button_frame.columnconfigure(4, weight=0, minsize=120)
            for index, button in enumerate(action_buttons):
                row = index // columns + 1
                column = index % columns
                columnspan = 2 if is_narrow and index == len(action_buttons) - 1 else 1
                button.grid(
                    row=row,
                    column=column,
                    columnspan=columnspan,
                    padx=3,
                    pady=1,
                    sticky="ew",
                )
        self.root.bind("<Control-z>", lambda e: self.undo(form))
        self.root.bind("<Control-y>", lambda e: self.redo(form))
        for frame in [
            call_frame,
            mandatory_frame,
            appeal_frame,
            contract_frame,
            action_frame,
            preview_frame,
        ]:
            frame.columnconfigure(1, weight=1)

        form["required_widgets"] = {
            "CM Ref#": form["cm_ref_entry"],
            "Phone Number": form["phone_entry"],
            "Payer Name": form["payer_entry"],
            "Agent Name": form["agent_entry"],
            "Call Reference #": form["call_ref_entry"],
            "Chat Reference #": form["call_ref_entry"],
            "Plan Type": form["plan_type_entry"],
            "Action Note": form["action_note_text"],
        }
        watched_entries = [
            "cm_ref_entry",
            "phone_entry",
            "payer_entry",
            "agent_entry",
            "call_ref_entry",
            "plan_type_entry",
            "specialty_entry",
            "pos_entry",
            "online_entry",
            "fax_entry",
            "attn_entry",
            "cc_name_entry",
            "effective_date_entry",
            "em_change_entry",
            "emer_change_entry",
            "drg_change_entry",
        ]
        for entry_name in watched_entries:
            form[entry_name].bind("<KeyRelease>", lambda e, f=form: self.update_form_state(f), add="+")
            form[entry_name].bind("<FocusOut>", lambda e, f=form: self.update_form_state(f), add="+")
        downcode_verified_map = {
            "em_change_entry": "em_verified_var",
            "emer_change_entry": "emer_verified_var",
            "drg_change_entry": "drg_verified_var",
        }
        for entry_name, variable_name in downcode_verified_map.items():
            form[entry_name].bind(
                "<KeyRelease>",
                lambda _event, f=form, e=entry_name, v=variable_name: self.sync_verified_from_downcode(f, e, v),
                add="+",
            )
            form[entry_name].bind(
                "<FocusOut>",
                lambda _event, f=form, e=entry_name, v=variable_name: self.sync_verified_from_downcode(f, e, v),
                add="+",
            )
        for text_name in [
            "mail_entry",
            "contract_comment_entry",
            "action_note_text",
        ]:
            form[text_name].bind("<KeyRelease>", lambda e, f=form: self.update_form_state(f), add="+")
        for variable_name in [
            "follow_up_var",
            "network_var",
            "em_verified_var",
            "emer_verified_var",
            "drg_verified_var",
        ]:
            form[variable_name].trace_add("write", lambda *_args, f=form: self.update_form_state(f))
        def apply_responsive_layout(width=None):
            width = width or canvas.winfo_width()
            is_narrow = width < 620
            current_mode = form.get("_responsive_mode")
            next_mode = "narrow" if is_narrow else "wide"
            if current_mode == next_mode:
                return
            form["_responsive_mode"] = next_mode

            if is_narrow:
                main_frame.grid_columnconfigure(0, weight=1)
                main_frame.grid_columnconfigure(1, weight=0)
                main_frame.grid_rowconfigure(0, weight=0)
                main_frame.grid_rowconfigure(1, weight=0)
                main_frame.grid_rowconfigure(2, weight=0)
                main_frame.grid_rowconfigure(3, weight=0)
                main_frame.grid_rowconfigure(4, weight=1)
                note_frame.columnconfigure(0, weight=1)
                note_frame.columnconfigure(1, weight=0)
                note_frame.rowconfigure(0, weight=1)
                note_frame.rowconfigure(1, weight=1)
                call_frame.grid_configure(row=0, column=0, columnspan=2)
                mandatory_frame.grid_configure(row=1, column=0, columnspan=2)
                appeal_frame.grid_configure(row=2, column=0, columnspan=2)
                contract_frame.grid_configure(row=3, column=0, columnspan=2)
                note_frame.grid_configure(row=4, column=0, columnspan=2)
                action_frame.grid_configure(row=0, column=0, columnspan=1)
                preview_frame.grid_configure(row=1, column=0, columnspan=1)
                layout_action_buttons(True)
            else:
                main_frame.grid_columnconfigure(0, weight=1)
                main_frame.grid_columnconfigure(1, weight=1)
                main_frame.grid_rowconfigure(0, weight=0)
                main_frame.grid_rowconfigure(1, weight=0)
                main_frame.grid_rowconfigure(2, weight=1)
                main_frame.grid_rowconfigure(3, weight=0)
                main_frame.grid_rowconfigure(4, weight=0)
                note_frame.columnconfigure(0, weight=1)
                note_frame.columnconfigure(1, weight=1)
                note_frame.rowconfigure(0, weight=1)
                note_frame.rowconfigure(1, weight=0)
                call_frame.grid_configure(row=0, column=0, columnspan=1)
                mandatory_frame.grid_configure(row=0, column=1, columnspan=1)
                appeal_frame.grid_configure(row=1, column=0, columnspan=1)
                contract_frame.grid_configure(row=1, column=1, columnspan=1)
                note_frame.grid_configure(row=2, column=0, columnspan=2)
                action_frame.grid_configure(row=0, column=0, columnspan=1)
                preview_frame.grid_configure(row=0, column=1, columnspan=1)
                layout_action_buttons(False)

            canvas.after_idle(update_scroll_region)
            canvas.after_idle(
                lambda: canvas.itemconfigure(
                    canvas_window,
                    height=max(canvas.winfo_height(), main_frame.winfo_reqheight()),
                )
            )

        form["_apply_responsive_layout"] = apply_responsive_layout
        apply_responsive_layout(canvas.winfo_width() or self.root.winfo_width())
        return form
    def save_text_state(self, form, widget_name):
        text = form[widget_name].get("1.0", tk.END).strip()
        if not form["undo_stack"] or form["undo_stack"][-1] != text:
            form["undo_stack"].append(text)
            form["redo_stack"].clear()
    def undo(self, form):
        if len(form["undo_stack"]) > 1:
            current = form["undo_stack"].pop()
            form["redo_stack"].append(current)
            for widget in ["action_note_text"]:
                form[widget].delete("1.0", tk.END)
                form[widget].insert(
                    "1.0", form["undo_stack"][-1] if form["undo_stack"] else ""
                )
    def redo(self, form):
        if form["redo_stack"]:
            text = form["redo_stack"].pop()
            form["undo_stack"].append(text)
            for widget in ["action_note_text"]:
                form[widget].delete("1.0", tk.END)
                form[widget].insert("1.0", text)
    def create_history_tab(self):
        self.create_notes_tab()

    def create_clients_tab(self):
        self.create_general_notes_tab()

    def create_notes_tab(self):
        notes_frame = ttk.Frame(self.notes_tab, padding=6)
        notes_frame.pack(fill="both", expand=True)
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(1, weight=1)

        filter_frame = ttk.LabelFrame(notes_frame, text="Find Notes", padding=4)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        filter_frame.columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Search:", style="Panel.TLabel").grid(row=0, column=0, sticky="w", padx=(2, 4), pady=1)
        self.notes_search_entry = ttk.Entry(filter_frame)
        self.notes_search_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=1)
        self.notes_today_var = tk.BooleanVar()
        ttk.Checkbutton(
            filter_frame,
            text="Today's Notes",
            variable=self.notes_today_var,
            command=self.update_notes_table,
        ).grid(row=0, column=2, sticky="w", padx=4, pady=1)

        history_action_frame = ttk.Frame(filter_frame)
        history_action_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Button(
            history_action_frame, text="Clear Filters", command=self.notes_clear_filters
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            history_action_frame, text="Export Notes", command=self.notes_export_to_excel
        ).pack(side="left", padx=5)

        table_frame = ttk.Frame(notes_frame)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=2)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.notes_tree = ttk.Treeview(
            table_frame,
            columns=(
                "Date",
                "Follow-up",
                "CM Ref#",
                "Payer",
                "Phone",
                "Agent",
                "Call Ref#",
                "Network",
                "Plan Type",
                "Specialty",
                "POS",
                "Online",
                "Fax",
                "Mail",
                "Attn",
                "Prev Verified",
                "CC Name",
                "Effective Date",
                "Contract Comment",
                "Action Note",
                "Generated Note",
                "Edited",
            ),
            show="headings",
            height=9,
        )
        for col in self.notes_tree["columns"]:
            self.notes_tree.heading(col, text=col)
            self.notes_tree.column(col, width=100)
        v_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.notes_tree.yview
        )
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.notes_tree.xview
        )
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.notes_tree.configure(
            yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set
        )
        self.notes_tree.grid(row=0, column=0, sticky="nsew")
        self.update_notes_table()

        edit_frame = ttk.LabelFrame(notes_frame, text="Selected Note", padding=5)
        edit_frame.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        edit_frame.columnconfigure(0, weight=1)

        selected_action_frame = ttk.Frame(edit_frame)
        selected_action_frame.grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.notes_edit_reference = ttk.Entry(edit_frame)
        self.notes_edit_reference.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        self.notes_edit_text = scrolledtext.ScrolledText(
            edit_frame, height=7, width=50
        )
        self.notes_edit_text.grid(row=2, column=0, sticky="ew")
        self.copy_button = ttk.Button(
            selected_action_frame,
            text="Copy Note",
            command=lambda: self.root.clipboard_append(
                self.notes_edit_text.get("1.0", tk.END)
            ),
            state=tk.DISABLED,                                 
        )
        self.copy_button.pack(side="left", padx=(0, 5))
        self.update_button = ttk.Button(
            selected_action_frame,
            text="Save Changes",
            command=self.update_note,
            state=tk.DISABLED,                                 
        )
        self.update_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(
            selected_action_frame,
            text="Delete Note",
            command=self.delete_note,
            state=tk.DISABLED,                                 
        )
        self.delete_button.pack(side="left", padx=5)
        self.replicate_button = ttk.Button(
            selected_action_frame,
            text="Use as Template",
            command=self.open_note_in_new_tab,
            state=tk.DISABLED,                                 
        )
        self.replicate_button.pack(side="left", padx=5)

        def combined_handler(event):
            self.notes_show_selected_note(event)
            self.update_buttons_state(self.notes_tree)
        self.notes_tree.bind("<<TreeviewSelect>>", combined_handler)
        self.notes_search_entry.bind(
            "<KeyRelease>", lambda e: self.update_notes_table()
        )
    def update_buttons_state(self, tree):
        selected = tree.selection()
        if selected:
            self.enable_buttons()
        else:
            self.disable_buttons()
    def enable_buttons(self):
        self.copy_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.replicate_button.config(state=tk.NORMAL)
    def disable_buttons(self):
        self.copy_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.replicate_button.config(state=tk.DISABLED)
    def create_general_notes_tab(self):
        general_frame = ttk.Frame(self.general_notes_tab, padding=6)
        general_frame.pack(fill="both", expand=True)
        general_frame.columnconfigure(0, weight=1)
        general_frame.rowconfigure(1, weight=1)

        header_frame = ttk.Frame(general_frame, style="Header.TFrame", padding=(10, 8))
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header_frame.columnconfigure(0, weight=1)
        ttk.Label(header_frame, text="Client Directory", style="Hero.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.client_count_var = tk.StringVar(value="0 clients")
        ttk.Label(header_frame, textvariable=self.client_count_var, style="HeroSub.TLabel").grid(
            row=1, column=0, sticky="w", pady=(3, 0)
        )

        directory_frame = ttk.Frame(general_frame)
        directory_frame.grid(row=1, column=0, sticky="nsew")
        directory_frame.columnconfigure(0, weight=3)
        directory_frame.columnconfigure(1, weight=1)
        directory_frame.rowconfigure(0, weight=1)

        browser_frame = ttk.LabelFrame(directory_frame, text="Directory", padding=5)
        browser_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        browser_frame.columnconfigure(0, weight=1)
        browser_frame.rowconfigure(1, weight=1)

        search_frame = ttk.Frame(browser_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search:", style="Panel.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.client_search_var = tk.StringVar()
        self.client_search_entry = ttk.Entry(search_frame, textvariable=self.client_search_var)
        self.client_search_entry.grid(row=0, column=1, sticky="ew")
        self.client_search_var.trace_add("write", lambda *_: self.render_client_directory())

        canvas_host = ttk.Frame(browser_frame)
        canvas_host.grid(row=1, column=0, sticky="nsew")
        canvas_host.columnconfigure(0, weight=1)
        canvas_host.rowconfigure(0, weight=1)

        colors = self.theme_colors
        self.client_card_canvas = tk.Canvas(
            canvas_host,
            background=colors["field_bg"],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=colors["border"],
        )
        self.client_card_canvas.grid(row=0, column=0, sticky="nsew")
        client_scrollbar = ttk.Scrollbar(
            canvas_host, orient="vertical", command=self.client_card_canvas.yview
        )
        client_scrollbar.grid(row=0, column=1, sticky="ns")
        self.client_card_canvas.configure(yscrollcommand=client_scrollbar.set)
        self.client_card_frame = ttk.Frame(self.client_card_canvas)
        self.client_card_window = self.client_card_canvas.create_window(
            (0, 0), window=self.client_card_frame, anchor="nw"
        )
        self.client_card_frame.bind(
            "<Configure>",
            lambda _event: self.client_card_canvas.configure(
                scrollregion=self.client_card_canvas.bbox("all")
            ),
        )
        self.client_card_canvas.bind("<Configure>", self.on_client_canvas_configure)
        self.client_card_canvas.bind(
            "<MouseWheel>",
            lambda event: self.client_card_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )

        entry_frame = ttk.LabelFrame(directory_frame, text="Client Details", padding=6)
        entry_frame.grid(row=0, column=1, sticky="nsew")
        entry_frame.columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="Client:", style="Panel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.client_entry = ttk.Entry(entry_frame)
        self.client_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        ttk.Label(entry_frame, text="NPI:", style="Panel.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.npi_entry = ttk.Entry(entry_frame)
        self.npi_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6))
        ttk.Label(entry_frame, text="Tax ID:", style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.tax_id_entry = ttk.Entry(entry_frame)
        self.tax_id_entry.grid(row=2, column=1, sticky="ew", pady=(0, 6))
        ttk.Label(entry_frame, text="Address:", style="Panel.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 6))
        self.address_entry = ttk.Entry(entry_frame)
        self.address_entry.grid(row=3, column=1, sticky="ew", pady=(0, 6))

        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        ttk.Button(button_frame, text="Add Client", command=self.add_client, style="Primary.TButton").grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_client).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

        self.general_notes = []
        self.selected_client_index = None
        self.client_card_columns = 1
        self.load_general_notes()

    def load_general_notes(self):
        self.general_notes = self.load_json(GENERAL_NOTES_FILE)
        self.render_client_directory()

    def on_client_canvas_configure(self, event):
        self.client_card_canvas.itemconfigure(self.client_card_window, width=event.width)
        columns = 2 if event.width >= 760 else 1
        if columns != self.client_card_columns:
            self.client_card_columns = columns
            self.render_client_directory()

    def get_filtered_clients(self):
        query = self.client_search_var.get().strip().lower()
        if not query:
            return list(enumerate(self.general_notes))
        return [
            (index, note)
            for index, note in enumerate(self.general_notes)
            if query
            in " ".join(
                [
                    note.get("client", ""),
                    note.get("npi", ""),
                    note.get("tax_id", ""),
                    note.get("address", ""),
                ]
            ).lower()
        ]

    def render_client_directory(self):
        if not hasattr(self, "client_card_frame"):
            return

        for widget in self.client_card_frame.winfo_children():
            widget.destroy()

        filtered_clients = self.get_filtered_clients()
        total_clients = len(self.general_notes)
        visible_clients = len(filtered_clients)
        if visible_clients == total_clients:
            count_text = f"{total_clients} client{'s' if total_clients != 1 else ''}"
        else:
            count_text = f"{visible_clients} of {total_clients} clients"
        self.client_count_var.set(count_text)

        for column in range(max(self.client_card_columns, 1)):
            self.client_card_frame.columnconfigure(column, weight=1, uniform="client_cards")

        if not filtered_clients:
            ttk.Label(
                self.client_card_frame,
                text="No clients found.",
                style="ClientEmpty.TLabel",
                padding=10,
            ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            return

        for position, (index, note) in enumerate(filtered_clients):
            row = position // self.client_card_columns
            column = position % self.client_card_columns
            self.create_client_card(index, note).grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=5,
                pady=5,
            )

    def create_client_card(self, index, note):
        selected = index == self.selected_client_index
        frame_style = "SelectedClientCard.TFrame" if selected else "ClientCard.TFrame"
        label_style = "SelectedClientCard.TLabel" if selected else "ClientCard.TLabel"
        name_style = "SelectedClientName.TLabel" if selected else "ClientName.TLabel"
        meta_style = "SelectedClientMeta.TLabel" if selected else "ClientMeta.TLabel"

        card = ttk.Frame(self.client_card_frame, style=frame_style, padding=8)
        card.columnconfigure(0, weight=1)
        ttk.Label(
            card,
            text=note.get("client", ""),
            style=name_style,
            wraplength=420,
        ).grid(row=0, column=0, sticky="ew")
        ttk.Label(
            card,
            text=f"NPI {note.get('npi', '')}    Tax ID {note.get('tax_id', '')}",
            style=meta_style,
        ).grid(row=1, column=0, sticky="ew", pady=(3, 0))
        ttk.Label(
            card,
            text=note.get("address", ""),
            style=label_style,
            wraplength=420,
        ).grid(row=2, column=0, sticky="ew", pady=(4, 0))

        for widget in [card, *card.winfo_children()]:
            widget.bind("<Button-1>", lambda _event, client_index=index: self.select_client(client_index))
        return card

    def select_client(self, index):
        self.selected_client_index = index
        note = self.general_notes[index]
        self.clear_client_entries()
        self.client_entry.insert(0, note.get("client", ""))
        self.npi_entry.insert(0, note.get("npi", ""))
        self.tax_id_entry.insert(0, note.get("tax_id", ""))
        self.address_entry.insert(0, note.get("address", ""))
        self.render_client_directory()

    def add_client(self):
        client = self.client_entry.get().strip()
        npi = self.npi_entry.get().strip()
        tax_id = self.tax_id_entry.get().strip()
        address = self.address_entry.get().strip()
        if client and npi and tax_id and address:
            self.general_notes.append(
                {"client": client, "npi": npi, "tax_id": tax_id, "address": address}
            )
            self.save_json(GENERAL_NOTES_FILE, self.general_notes)
            self.selected_client_index = len(self.general_notes) - 1
            self.clear_client_entries()
            self.render_client_directory()
        else:
            messagebox.showwarning("Error", "All fields are required!")
    def delete_client(self):
        if self.selected_client_index is None:
            messagebox.showwarning("Error", "Select a client to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete this client?"):
            del self.general_notes[self.selected_client_index]
            self.save_json(GENERAL_NOTES_FILE, self.general_notes)
            self.selected_client_index = None
            self.clear_client_entries()
            self.render_client_directory()
    def clear_client_entries(self):
        self.client_entry.delete(0, tk.END)
        self.npi_entry.delete(0, tk.END)
        self.tax_id_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
    def validate_mandatory_fields(self, form):
        errors = []
        if not form["follow_up_var"].get():
            errors.append("Follow-up Type")
        if not form["cm_ref_entry"].get().strip():
            errors.append("CM Ref#")
        if (
            form["follow_up_var"].get() in ["PH", "APP"]
            and not form["phone_entry"].get().strip()
        ):
            errors.append("Phone Number")
        if not form["payer_entry"].get().strip():
            errors.append("Payer Name")
        if not form["agent_entry"].get().strip():
            errors.append("Agent Name")
        if not form["call_ref_entry"].get().strip():
            errors.append(
                f"{'Call' if form['follow_up_var'].get() in ['PH', 'APP'] else 'Chat'} Reference #"
            )
        if not form["network_var"].get():
            errors.append("Network Status")
        if not form["network_var"].get().strip():
            errors.append("Network Status")
        if not form["plan_type_entry"].get().strip():
            errors.append("Plan Type")
        if not form["action_note_text"].get("1.0").strip():
            errors.append("Action Note")
        return errors
    def save_contact(self, form):
        phone = form["phone_entry"].get().strip()
        payer = form["payer_entry"].get().strip()
        if phone and payer:
            if any(
                contact
                for contact in self.contacts
                if contact["phone"] == phone and contact["payer"] == payer
            ):
                messagebox.showwarning(
                    "Duplicate Contact", "This contact already exists."
                )
                return
            try:
                self.contacts.append({"phone": phone, "payer": payer})
                self.save_json(CONTACTS_FILE, self.contacts)
                self.refresh_workspace_context()
                self.set_status("Payer contact saved.")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred while saving the contact: {e}"
                )
        else:
            messagebox.showwarning("Error", "Phone and Payer are required!")
    def delete_contact(self, tree, window):
        self.delete_contact_button.config(state=tk.DISABLED)
        selected = tree.selection()
        if not selected:
            self.delete_contact_button.config(
                state=tk.NORMAL
            )                             
            return
        else:
            contact = tree.item(selected[0])["values"]
            self.contacts = [
                c
                for c in self.contacts
                if not (c["phone"] == contact[0] and c["payer"] == contact[1])
            ]
            self.save_json(CONTACTS_FILE, self.contacts)
            tree.delete(selected[0])
            self.refresh_workspace_context()
            window.lift()
            window.focus_force()
            self.delete_contact_button.config(state=tk.NORMAL)
    def view_contacts(self):
        if hasattr(self, "view_contact_button"):
            self.view_contact_button.config(state=tk.DISABLED)
        contacts_window = tk.Toplevel(self.root)
        contacts_window.title("Saved Contacts")
        contacts_window.transient(self.root)               
        contacts_window.grab_set()              
        contacts_window.bind(
            "<Destroy>",
            lambda event: self.view_contact_button.config(state=tk.NORMAL)
            if hasattr(self, "view_contact_button")
            else None,
        )
        frame = tk.Frame(contacts_window)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        tree = ttk.Treeview(frame, columns=("Phone", "Payer"), show="headings")
        tree.heading("Phone", text="Phone")
        tree.heading("Payer", text="Payer")
        for contact in self.contacts:
            tree.insert("", "end", values=(contact["phone"], contact["payer"]))
        tree.pack(side="left", expand=True, fill="both")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(contacts_window, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        ttk.Button(
            contacts_window,
            text="Use Contact",
            command=lambda: self.use_contact(tree, contacts_window),
        ).pack(pady=5)
        self.delete_contact_button = ttk.Button(
            contacts_window,
            text="Delete Contact",
            command=lambda: self.delete_contact(tree, contacts_window),
        )
        self.delete_contact_button.pack(pady=5)
    def use_contact(self, tree, window):
        selected = tree.selection()
        current_tab = self.get_current_form()
        if selected and current_tab:
            contact = tree.item(selected[0])["values"]
            current_tab["phone_entry"].delete(0, tk.END)
            current_tab["phone_entry"].insert(0, contact[0])
            current_tab["payer_entry"].delete(0, tk.END)
            current_tab["payer_entry"].insert(0, contact[1])
            self.update_form_state(current_tab)
            window.destroy()
        elif not current_tab:
            messagebox.showwarning("Error", "No active New Follow-Up tab!")
    def add_quick_note(self, form):
        note = form["action_note_text"].get("1.0", tk.END).strip()
        if note:
            if note in self.quick_notes:
                messagebox.showwarning(
                    "Duplicate Note", "This quick note already exists."
                )
                return
            self.quick_notes.append(note)
            self.save_json(QUICK_NOTES_FILE, self.quick_notes)
            self.refresh_workspace_context()
            self.set_status("Quick note saved.")
        else:
            messagebox.showwarning("Error", "Action note is empty!")
    def view_quick_notes(self):
        if hasattr(self, "view_quick_notes_button"):
            self.view_quick_notes_button.config(state=tk.DISABLED)
        quick_window = tk.Toplevel(self.root)
        quick_window.title("Quick Notes")
        quick_window.transient(self.root)               
        quick_window.grab_set()              
        quick_window.bind(
            "<Destroy>",
            lambda event: self.view_quick_notes_button.config(state=tk.NORMAL)
            if hasattr(self, "view_quick_notes_button")
            else None,
        )
        frame = tk.Frame(quick_window)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        listbox = tk.Listbox(frame, height=20, width=80)
        for note in self.quick_notes:
            listbox.insert(tk.END, note)
        listbox.pack(side="left", expand=True, fill="both")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        vsb.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=vsb.set)
        ttk.Button(
            quick_window,
            text="Insert Quick Note",
            command=lambda: self.use_quick_note(listbox, quick_window),
        ).pack(pady=5)
        self.delete_quick_note_button = ttk.Button(
            quick_window,
            text="Delete Quick Note",
            command=lambda: self.delete_quick_note(listbox, quick_window),
        )
        self.delete_quick_note_button.pack(pady=5)
    def delete_quick_note(self, listbox, window):
        self.delete_quick_note_button.config(state=tk.DISABLED)
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            self.quick_notes.pop(index)                                
            listbox.delete(index)                       
            self.save_json(QUICK_NOTES_FILE, self.quick_notes)                          
            window.lift()
            window.focus_force()
        self.delete_quick_note_button.config(state=tk.NORMAL)
    def use_quick_note(self, listbox, window):
        selected = listbox.curselection()
        if selected:
            note = listbox.get(selected[0])
            self.insert_quick_note(note)
            window.lift()
            window.focus_force()
    def insert_quick_note(self, note):
        current_tab = self.get_current_form()
        if not current_tab:
            return
        existing_text = current_tab["action_note_text"].get("1.0", tk.END).strip()
        new_text = f"({existing_text})\n\n{note}" if existing_text else note
        current_tab["action_note_text"].delete("1.0", tk.END)
        current_tab["action_note_text"].insert("1.0", new_text)
        self.update_form_state(current_tab)
    def set_note_preview(self, form, text):
        preview = form["note_preview_text"]
        preview.delete("1.0", tk.END)
        if text:
            preview.insert("1.0", text)

    def refresh_live_preview(self, form, errors=None):
        errors = errors if errors is not None else self.validate_mandatory_fields(form)
        if errors:
            self.set_note_preview(form, "")
            return ""
        note = self.build_generated_note(form)
        self.set_note_preview(form, note)
        return note

    def generate_note(self, form):
        errors = self.validate_mandatory_fields(form)
        if errors:
            self.set_validation_state(form, errors)
            self.set_status("Complete the highlighted fields before generating a preview.", "warn")
            self.set_note_preview(form, "")
            return ""
        note = self.build_generated_note(form)
        self.set_note_preview(form, note)
        self.set_status("Preview updated.")
        return note

    def build_generated_note(self, form):
        note = []
        follow_up = form["follow_up_var"].get()
        payer = form["payer_entry"].get().strip()
        phone = form["phone_entry"].get().strip()
        agent = form["agent_entry"].get().strip()
        call_ref = form["call_ref_entry"].get().strip()
        network = form["network_var"].get()
        plan_type = form["plan_type_entry"].get().strip()
        specialty = form["specialty_entry"].get().strip()
        pos = form["pos_entry"].get().strip()
        cc_name = form["cc_name_entry"].get().strip()
        effective_date = form["effective_date_entry"].get().strip()
        contract_comment = form["contract_comment_entry"].get("1.0", tk.END).strip()
        online = form["online_entry"].get().strip()
        fax = form["fax_entry"].get().strip()
        mail = form["mail_entry"].get("1.0", tk.END).strip()
        attn = form["attn_entry"].get().strip()
        prev_verified = (
            " (previously verified)" if form["prev_verified_var"].get() else ""
        )
        action_note = form["action_note_text"].get("1.0", tk.END).strip()
        if follow_up == "APP":
            note.append("Telephone Appeal:")
        else:
            note.append(f"Follow up via {'Phone' if follow_up == 'PH' else 'Chat'}:")
        if follow_up == "PH" or follow_up == "APP":
            note.append(
                f"Called {payer} at {phone} and spoke with {agent} (Call Reference # {call_ref})."
            )
        else:
            note.append(
                f"Chatted with with {agent} at {payer} (Chat Reference # {call_ref})."
            )
        info = []
        if network.upper() != "N/A":
            info.append(f"The claim was processed as {network}")
        if plan_type.upper() != "N/A":
            info.append(f"the member's plan type is {plan_type}")
        if specialty and specialty.upper() != "N/A":
            info.append(f"the provider's specialty is {specialty}")
        if pos and pos.upper() != "N/A":
            info.append(f"the Place of Service on the claim is {pos}")
        if info:
            note.append("The following information was obtained:")
            note.append(", ".join(info) + ".")
        contract_info = []
        if cc_name and cc_name.upper() != "N/A":
            contract_info.append(f'the contract used is "{cc_name}"')
        if effective_date and effective_date.upper() != "N/A":
            contract_info.append(f"effective {effective_date}")
        if contract_comment and contract_comment.upper() != "N/A":
            contract_info.append(f"Additionally, {contract_comment}")
        if contract_info:
            note.append(f"According to the representative, {', '.join(contract_info)}.")
        appeal_info = []
        online_normalized = online.upper() if online else ""
        fax_normalized = fax.upper() if fax else ""
        mail_normalized = mail.upper() if mail else ""
        attn_normalized = attn.upper() if attn else ""
        if online_normalized != "N/A" and online:
            appeal_info.append(f"online through {online}")
        if fax_normalized != "N/A" and fax:
            appeal_info.append(f"by fax at {fax}")
        if mail_normalized != "N/A" and mail:
            appeal_info.append(f"by mail to {mail}")
        if attn_normalized != "N/A" and attn:
            appeal_info.append(f"attn to: {attn}")
        if appeal_info:
            note.append(
                f"The appeal process was confirmed. It can be submitted: {', '.join(appeal_info)}"
                + (
                    ". This was previously verified."
                    if prev_verified and appeal_info
                    else "."
                )
            )
        em_change = self.get_placeholder_entry_value(form["em_change_entry"])
        if form["em_verified_var"].get():
            if em_change:
                note.append(
                    f"The E&M code was verified and has been downcoded to: {em_change}."
                )
            else:
                note.append("The E&M code was verified; no changes were made.")
        emer_change = self.get_placeholder_entry_value(form["emer_change_entry"])
        if form["emer_verified_var"].get():
            if emer_change:
                note.append(
                    f"The Emergency code was verified and has been downcoded to: {emer_change}."
                )
            else:
                note.append("The Emergency code was verified; no changes were made.")
        drg_change = self.get_placeholder_entry_value(form["drg_change_entry"])
        if form["drg_verified_var"].get():
            if drg_change:
                note.append(
                    f"The DRG code was verified and has been downcoded to: {drg_change}."
                )
            else:
                note.append("The DRG code was verified; no changes were made.")
        if action_note and action_note.upper() != "N/A":
            note.append(f"Comment: {action_note}")
        return "\n".join(note)
    def submit_note(self, form):
        form["submit_button"].config(state=tk.DISABLED)
        errors = self.validate_mandatory_fields(form)
        if errors:
            self.set_validation_state(form, errors)
            self.set_status("Complete the highlighted fields before saving.", "warn")
            self.update_form_state(form)
            return
        note = form["note_preview_text"].get("1.0", tk.END).strip()
        if not note:
            note = self.refresh_live_preview(form, errors).strip()
        if not note:
            self.set_status("Complete the highlighted fields before saving.", "warn")
            self.update_form_state(form)
            return
        em_change = self.get_placeholder_entry_value(form["em_change_entry"])
        emer_change = self.get_placeholder_entry_value(form["emer_change_entry"])
        drg_change = self.get_placeholder_entry_value(form["drg_change_entry"])
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "follow_up": form["follow_up_var"].get(),
            "cm_ref": form["cm_ref_entry"].get().strip(),
            "phone": form["phone_entry"].get().strip(),
            "payer": form["payer_entry"].get().strip(),
            "agent": form["agent_entry"].get().strip(),
            "call_ref": form["call_ref_entry"].get().strip(),
            "network": form["network_var"].get(),
            "plan_type": form["plan_type_entry"].get().strip(),
            "specialty": form["specialty_entry"].get().strip(),
            "pos": form["pos_entry"].get().strip(),
            "online": form["online_entry"].get().strip(),
            "fax": form["fax_entry"].get().strip(),
            "mail": form["mail_entry"].get("1.0", tk.END).strip(),
            "attn": form["attn_entry"].get().strip(),
            "prev_verified": form["prev_verified_var"].get(),
            "cc_name": form["cc_name_entry"].get().strip(),
            "effective_date": form["effective_date_entry"].get().strip(),
            "contract_comment": form["contract_comment_entry"]
            .get("1.0", tk.END)
            .strip(),
            "action_note": form["action_note_text"].get("1.0", tk.END).strip(),
            "generated_note": note,
            "comments": "",
            "follow_up_date": "",
            "edited": "",
            "em_verified": form["em_verified_var"].get(),
            "em_change": em_change,
            "emer_verified": form["emer_verified_var"].get(),
            "emer_change": emer_change,
            "drg_verified": form["drg_verified_var"].get(),
            "drg_change": drg_change,
        }
        self.notes.append(entry)
        if self.save_json(DATA_FILE, self.notes):
            self.refresh_audit_csv()
        self.update_notes_table()
        self.refresh_workspace_context()
        self.clear_claim_fields_after_save(form)
        self.update_form_state(form)
        self.set_status("Follow-up saved. Reusable details were kept.")
    def reset_fields(self, form):
        form["follow_up_var"].set("")
        form["cm_ref_entry"].delete(0, tk.END)
        form["phone_entry"].delete(0, tk.END)
        form["payer_entry"].delete(0, tk.END)
        form["agent_entry"].delete(0, tk.END)
        form["call_ref_entry"].delete(0, tk.END)
        form["network_var"].set("")
        form["plan_type_entry"].delete(0, tk.END)
        form["specialty_entry"].delete(0, tk.END)
        form["pos_entry"].delete(0, tk.END)
        form["online_entry"].delete(0, tk.END)
        form["fax_entry"].delete(0, tk.END)
        form["mail_entry"].delete("1.0", tk.END)
        form["attn_entry"].delete(0, tk.END)
        form["prev_verified_var"].set(False)
        form["cc_name_entry"].delete(0, tk.END)
        form["effective_date_entry"].delete(0, tk.END)
        form["contract_comment_entry"].delete("1.0", tk.END)
        form["action_note_text"].delete("1.0", tk.END)
        form["note_preview_text"].delete("1.0", tk.END)
        form["em_verified_var"].set(False)
        form["emer_verified_var"].set(False)
        form["drg_verified_var"].set(False)
        for entry_name in ("em_change_entry", "emer_change_entry", "drg_change_entry"):
            self.set_placeholder_entry_value(form[entry_name])
        form["undo_stack"].clear()
        form["redo_stack"].clear()
        self.update_form_state(form)
    def update_notes_table(self, event=None):
        self.notes = sorted(
            self.notes,
            key=lambda note: (
                datetime.strptime(note["date"], "%Y-%m-%d %H:%M:%S")
                if note["date"]
                else datetime.min
            ),
        )
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        today = date.today().strftime("%Y-%m-%d")
        search_term = self.notes_search_entry.get().lower()
        for note in self.notes:
            if (
                (not self.notes_today_var.get() or note["date"].startswith(today))
                and (
                    not search_term
                    or any(search_term in str(v).lower() for v in note.values())
                )
            ):
                self.notes_tree.insert(
                    "",
                    "end",
                    values=(
                        note["date"],
                        note["follow_up"],
                        note["cm_ref"],
                        note["payer"],
                        note["phone"],
                        note["agent"],
                        note["call_ref"],
                        note["network"],
                        note["plan_type"],
                        note["specialty"],
                        note["pos"],
                        note["online"],
                        note["fax"],
                        note["mail"],
                        note.get("attn", ""),
                        str(note["prev_verified"]),
                        note["cc_name"],
                        note["effective_date"],
                        note["contract_comment"],
                        note["action_note"],
                        note["generated_note"],
                        note.get("edited", ""),
                    ),
                )
        if (
            not hasattr(self, "notes_edit_text")
            or not hasattr(self, "notes_edit_reference")
        ):
            return
        self.notes_edit_text.delete("1.0", tk.END)
        self.notes_edit_reference.delete(0, tk.END)
    def notes_show_selected_note(self, event):
        selected = self.notes_tree.selection()
        if selected:
            item = self.notes_tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    self.notes_edit_text.delete("1.0", tk.END)
                    self.notes_edit_text.insert("1.0", note["generated_note"])
                    self.notes_edit_reference.delete(0, tk.END)
                    self.notes_edit_reference.insert(0, note.get("cm_ref", ""))
                    break
    def update_note(self):
        selected = self.notes_tree.selection()
        if selected:
            selected_item_id = selected[0]
            item = self.notes_tree.item(selected_item_id)["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    note["generated_note"] = self.notes_edit_text.get(
                        "1.0", tk.END
                    ).strip()
                    note["edited"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if self.save_json(DATA_FILE, self.notes):
                        self.refresh_audit_csv()
                    self.update_notes_table()
                    for child in self.notes_tree.get_children():
                        child_item = self.notes_tree.item(child)["values"]
                        if str(child_item[0]) == str(item[0]) and str(
                            child_item[2]
                        ) == str(item[2]):
                            self.notes_tree.selection_set(child)
                            self.notes_tree.see(child)
                            break
                    break
    def delete_note(self):
        selected = self.notes_tree.selection()
        if selected and messagebox.askyesno("Confirm", "Delete this note?"):
            item = self.notes_tree.item(selected[0])["values"]
            self.notes = [
                note
                for note in self.notes
                if not (
                    str(note["date"]) == str(item[0])
                    and str(note["cm_ref"]) == str(item[2])
                )
            ]
            if self.save_json(DATA_FILE, self.notes):
                self.refresh_audit_csv()
            self.notes_tree.delete(selected[0])
            self.notes_edit_text.delete("1.0", tk.END)
            self.notes_edit_reference.delete(0, tk.END)
    def open_note_in_new_tab(self):
        selected = self.notes_tree.selection()
        if selected:
            item = self.notes_tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    new_form = self.add_new_call_tab()
                    self.fill_form(new_form, note)
                    break
    def notes_export_to_excel(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = [
            list(self.notes_tree.item(item)["values"])
            for item in self.notes_tree.get_children()
        ]
        df = pd.DataFrame(
            data,
            columns=[
                "Date",
                "Follow-up",
                "CM Ref#",
                "Payer",
                "Phone",
                "Agent",
                "Call Ref#",
                "Network",
                "Plan Type",
                "Specialty",
                "POS",
                "Online",
                "Fax",
                "Mail",
                "Attn",
                "Prev Verified",
                "CC Name",
                "Effective Date",
                "Contract Comment",
                "Action Note",
                "Generated Note",
                "Edited",
            ],
        )
        export_path = os.path.join(
            os.path.expanduser("~/Downloads"), f"all_notes_export_{timestamp}.xlsx"
        )
        df.to_excel(export_path, index=False)
        messagebox.showinfo("Success", f"Exported to {export_path}")
    def notes_clear_filters(self):
        self.notes_search_entry.delete(0, tk.END)
        self.notes_today_var.set(False)
        self.notes_edit_text.delete("1.0", tk.END)
        self.notes_edit_reference.delete(0, tk.END)
        self.update_notes_table()
    def fill_form(self, form, note):
        if not form:
            return
        self.reset_fields(form)
        form["follow_up_var"].set(note["follow_up"])
        form["phone_entry"].insert(0, note["phone"])
        form["payer_entry"].insert(0, note["payer"])
        form["online_entry"].insert(0, note["online"])
        form["fax_entry"].insert(0, note["fax"])
        form["mail_entry"].insert("1.0", note["mail"])
        form["attn_entry"].insert(0, note.get("attn", ""))
        form["prev_verified_var"].set(note["prev_verified"])
        form["cc_name_entry"].insert(0, note["cc_name"])
        form["effective_date_entry"].insert(0, note["effective_date"])
        form["contract_comment_entry"].insert("1.0", note["contract_comment"])
        form["action_note_text"].insert("1.0", note["action_note"])
        form["em_verified_var"].set(note.get("em_verified", False))
        self.set_placeholder_entry_value(form["em_change_entry"], note.get("em_change", ""))
        form["emer_verified_var"].set(note.get("emer_verified", False))
        self.set_placeholder_entry_value(form["emer_change_entry"], note.get("emer_change", ""))
        form["drg_verified_var"].set(note.get("drg_verified", False))
        self.set_placeholder_entry_value(form["drg_change_entry"], note.get("drg_change", ""))
        self.notebook.select(self.workspace_tab)
        self.update_form_state(form)
        self.set_status("Template loaded.")
    def on_closing(self):
        result = messagebox.askyesno("Exit", "Do you really want to exit?")
        if result:
            if self.save_json(DATA_FILE, self.notes):
                self.refresh_audit_csv()
            self.root.quit()
if __name__ == "__main__":
    root = tk.Tk()
    app = CallDetailsApp(root)
    root.mainloop()
