import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import tkinter.simpledialog as simpledialog
import json
from datetime import datetime, date, timedelta
import pandas as pd
import os
DATA_FILE = os.path.join(
    os.path.join(os.environ["USERPROFILE"]), r"Documents\Follow-Ups\v3\call_notes.json"
)
CONTACTS_FILE = os.path.join(
    os.path.join(os.environ["USERPROFILE"]), r"Documents\Follow-Ups\v3\contacts.json"
)
QUICK_NOTES_FILE = os.path.join(
    os.path.join(os.environ["USERPROFILE"]), r"Documents\Follow-Ups\v3\quick_notes.json"
)
GENERAL_NOTES_FILE = os.path.join(
    os.path.join(os.environ["USERPROFILE"]),
    r"Documents\Follow-Ups\v3\general_notes.json",
)
TAGS_FILE = os.path.join(
    os.path.join(os.environ["USERPROFILE"]), r"Documents\Follow-Ups\v3\tags.json"
)
def ensure_directories_exist():
    directory = os.path.dirname(DATA_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file_path in [CONTACTS_FILE, QUICK_NOTES_FILE, GENERAL_NOTES_FILE, TAGS_FILE]:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
ensure_directories_exist()
class CallDetailsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Follow Ups Tool - V3.1")
        self.root.geometry("990x925+0+0")
        self.notes = self.load_json(DATA_FILE)
        self.contacts = self.load_json(CONTACTS_FILE)
        self.quick_notes = self.load_json(QUICK_NOTES_FILE)
        self.tags = self.load_json(TAGS_FILE) or [
            "Sent Back",
            "To Escalate",
            "Reappeal",
            "Other",
            "Fax Requested",
        ]
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Segoe UI", 8, "bold"), padding=5)
        self.style.configure("TButton", font=("Segoe UI", 8, "bold"), padding=3)
        self.style.configure("TFrame", padding=10)
        self.style.configure("Heading.TLabel", font=("Segoe UI", 8, "bold"))
        self.style.configure("TButton", background="#B0C4DE")
        self.style.configure("TFrame", background="gray46", relief="flat", padding=20)
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#4682B4"), ("!selected", "#B0C4DE")],
            foreground=[("selected", "white"), ("!selected", "black")],
        )
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        self.notes_tab = ttk.Frame(self.notebook)
        self.follow_ups_tab = ttk.Frame(self.notebook)
        self.general_notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.notes_tab, text="All Notes Entered")
        self.notebook.add(self.follow_ups_tab, text="Pending Follow-Ups")
        self.notebook.add(self.general_notes_tab, text="Client's Info")
        self.entry_tabs = []
        self.add_new_call_tab()
        self.create_notes_tab()
        self.create_follow_ups_tab()
        self.create_general_notes_tab()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
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
            success_message = messagebox.showinfo(
                "Success",
                "Operation saved successfully!\n\nDisregard this if no action/change was made",
                parent=self.root,
            )
        except IOError as e:
            error_message = messagebox.showerror(
                "Error",
                f"File cannot be loaded: {filename}: {str(e)}",
                parent=self.root,
            )
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
    def add_new_call_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.insert("end", tab, text=f"New Call {len(self.entry_tabs) + 1}")
        form = self.create_call_form(tab)
        self.entry_tabs.append(form)
        self.notebook.select(tab)
        return form
    def close_current_tab(self):
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index >= 3:
            if current_tab_index != 3:
                self.notebook.forget(current_tab_index)
                adjusted_index = (
                    current_tab_index - 3
                )                                                                      
                if 0 <= adjusted_index < len(self.entry_tabs):
                    self.entry_tabs.pop(adjusted_index)
                if not self.entry_tabs:                                   
                    self.add_new_call_tab()
    def create_call_form(self, parent):
        def disable_enter(event):
            return "break"
        form = {"undo_stack": [], "redo_stack": []}
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, side="left")
        call_frame = ttk.LabelFrame(
            main_frame,
            text="📞 Call Details           Phone Number: (800) 930-6387  | Fax Number: (888) 437-7288",
            padding=10,
        )
        call_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        form["follow_up_var"] = tk.StringVar(value="")
        ttk.Label(call_frame, text="Follow-up Type:", foreground="red").grid(
            row=0, column=0, sticky="e"
        )
        ttk.Radiobutton(
            call_frame, text="PHONE", variable=form["follow_up_var"], value="PH"
        ).grid(row=0, column=1, sticky="e")
        ttk.Radiobutton(
            call_frame, text="CHAT", variable=form["follow_up_var"], value="CH"
        ).grid(row=0, column=2, sticky="we")
        ttk.Radiobutton(
            call_frame, text="APPEAL", variable=form["follow_up_var"], value="APP"
        ).grid(row=0, column=3, sticky="w")
        ttk.Label(call_frame, text="CM Reference #:", foreground="red").grid(
            row=1, column=0, sticky="e"
        )
        form["cm_ref_entry"] = ttk.Entry(call_frame)
        form["cm_ref_entry"].grid(row=1, column=1, columnspan=3, sticky="ew")
        ttk.Button(
            call_frame,
            text="🔎 Check Previous Follow-Up Notes",
            command=lambda: self.check_previous_cm_ref(
                form["cm_ref_entry"].get().strip()
            ),
        ).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(call_frame, text="📞Phone Number:", foreground="red").grid(
            row=3, column=0, sticky="e"
        )
        form["phone_entry"] = ttk.Entry(call_frame)
        form["phone_entry"].grid(row=3, column=1, columnspan=3, sticky="ew")
        form["phone_entry"].bind(
            "<KeyRelease>", lambda e: self.format_phone(form["phone_entry"])
        )
        ttk.Label(call_frame, text="Payer Name:", foreground="red").grid(
            row=4, column=0, sticky="e"
        )
        form["payer_entry"] = ttk.Entry(call_frame)
        form["payer_entry"].grid(row=4, column=1, columnspan=3, sticky="ew")
        form["payer_entry"].bind(
            "<KeyRelease>", lambda e: self.format_text_upper(form["payer_entry"])
        )
        ttk.Label(call_frame, text="Agent Name:", foreground="red").grid(
            row=5, column=0, sticky="e"
        )
        form["agent_entry"] = ttk.Entry(call_frame)
        form["agent_entry"].grid(row=5, column=1, columnspan=3, sticky="ew")
        form["agent_entry"].bind(
            "<KeyRelease>", lambda e: self.format_name(form["agent_entry"])
        )
        ttk.Label(call_frame, text="Call Reference #:", foreground="red").grid(
            row=6, column=0, sticky="e"
        )
        form["call_ref_entry"] = ttk.Entry(call_frame)
        form["call_ref_entry"].grid(row=6, column=1, columnspan=3, sticky="ew")
        ttk.Button(
            call_frame, text="💾 Save Contact", command=lambda: self.save_contact(form)
        ).grid(row=7, column=1, padx=1)
        self.view_contact_button = ttk.Button(
            call_frame, text="🔎 View Contact", command=self.view_contacts
        )
        self.view_contact_button.grid(row=7, column=2, padx=1)
        mandatory_frame = ttk.LabelFrame(
            main_frame, text="📌 Mandatory Questions", padding=10
        )
        mandatory_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        form["network_var"] = tk.StringVar(value="")
        ttk.Label(mandatory_frame, text="Network Status:", foreground="red").grid(
            row=0, column=0, sticky="e"
        )
        ttk.Radiobutton(
            mandatory_frame, text="INN", variable=form["network_var"], value="INN"
        ).grid(row=0, column=1, sticky="e")
        ttk.Radiobutton(
            mandatory_frame, text="OON", variable=form["network_var"], value="OON"
        ).grid(row=0, column=2, sticky="e")
        ttk.Radiobutton(
            mandatory_frame, text="N/A", variable=form["network_var"], value="N/A"
        ).grid(row=0, column=3, sticky="e")
        ttk.Label(mandatory_frame, text="Member's Plan Type:", foreground="red").grid(
            row=1, column=0, sticky="e"
        )
        form["plan_type_entry"] = ttk.Entry(mandatory_frame)
        form["plan_type_entry"].grid(row=1, column=1, columnspan=3, sticky="ew")
        form["plan_type_entry"].bind(
            "<KeyRelease>", lambda e: self.format_text_upper(form["plan_type_entry"])
        )
        ttk.Label(mandatory_frame, text="Provider Specialty:").grid(
            row=2, column=0, sticky="e"
        )
        form["specialty_entry"] = ttk.Entry(mandatory_frame)
        form["specialty_entry"].grid(row=2, column=1, columnspan=3, sticky="ew")
        ttk.Label(mandatory_frame, text="Place Of Service:").grid(
            row=3, column=0, sticky="e"
        )
        form["pos_entry"] = ttk.Entry(mandatory_frame)
        form["pos_entry"].grid(row=3, column=1, columnspan=3, sticky="ew")
        form["em_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            mandatory_frame, text="E&M Code verified", variable=form["em_verified_var"]
        ).grid(row=4, column=0, sticky="e")
        ttk.Label(mandatory_frame, text="Downcoded to:").grid(
            row=4, column=1, sticky="e"
        )
        form["em_change_entry"] = ttk.Entry(mandatory_frame)
        form["em_change_entry"].grid(row=4, column=2, columnspan=2, sticky="ew")
        form["emer_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            mandatory_frame,
            text="Emergency Code verified",
            variable=form["emer_verified_var"],
        ).grid(row=5, column=0, sticky="e")
        ttk.Label(mandatory_frame, text="Downcoded to:").grid(
            row=5, column=1, sticky="e"
        )
        form["emer_change_entry"] = ttk.Entry(mandatory_frame)
        form["emer_change_entry"].grid(row=5, column=2, columnspan=2, sticky="ew")
        form["drg_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            mandatory_frame, text="DRG Code verified", variable=form["drg_verified_var"]
        ).grid(row=6, column=0, sticky="e")
        ttk.Label(mandatory_frame, text="Downcoded to:").grid(
            row=6, column=1, sticky="e"
        )
        form["drg_change_entry"] = ttk.Entry(mandatory_frame)
        form["drg_change_entry"].grid(row=6, column=2, columnspan=2, sticky="ew")
        ttk.Label(
            mandatory_frame,
            text="    ** Leave blank if verified, but no downcoding occurred ↑↑↑↑",
        ).grid(row=7, column=0, columnspan=3, sticky="e")
        appeal_frame = ttk.LabelFrame(main_frame, text="📄 Appeal Process", padding=10)
        appeal_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Label(appeal_frame, text="💻 Online:").grid(row=0, column=0, sticky="e")
        form["online_entry"] = ttk.Entry(appeal_frame)
        form["online_entry"].grid(row=0, column=1, columnspan=2, sticky="ew")
        ttk.Label(appeal_frame, text="📠 Fax:").grid(row=1, column=0, sticky="e")
        form["fax_entry"] = ttk.Entry(appeal_frame)
        form["fax_entry"].grid(row=1, column=1, columnspan=2, pady=5, sticky="ew")
        form["fax_entry"].bind(
            "<KeyRelease>", lambda e: self.format_phone(form["fax_entry"])
        )
        ttk.Label(appeal_frame, text="📬 Mail:").grid(row=2, column=0, sticky="e")
        form["mail_entry"] = scrolledtext.ScrolledText(appeal_frame, height=2, width=30)
        form["mail_entry"].grid(row=2, column=1, columnspan=2, sticky="ew")
        form["mail_entry"].bind("<Return>", disable_enter)
        ttk.Label(appeal_frame, text="Attn to:").grid(row=3, column=0, sticky="e")
        form["attn_entry"] = ttk.Entry(appeal_frame)
        form["attn_entry"].grid(row=3, column=1, columnspan=2, sticky="ew")
        form["prev_verified_var"] = tk.BooleanVar()
        ttk.Checkbutton(
            appeal_frame, text="Previously Verified", variable=form["prev_verified_var"]
        ).grid(row=4, column=1, sticky="e")
        contract_frame = ttk.LabelFrame(
            main_frame, text="📑 Contract Details", padding=10
        )
        contract_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Label(contract_frame, text="CC Name:").grid(row=0, column=0, sticky="e")
        form["cc_name_entry"] = ttk.Entry(contract_frame)
        form["cc_name_entry"].grid(row=0, column=1, columnspan=2, sticky="ew")
        ttk.Label(contract_frame, text="Effective Date:").grid(
            row=1, column=0, sticky="e"
        )
        form["effective_date_entry"] = ttk.Entry(contract_frame)
        form["effective_date_entry"].grid(row=1, column=1, columnspan=2, sticky="ew")
        ttk.Label(contract_frame, text="Contract Comment:").grid(
            row=2, column=0, sticky="e"
        )
        form["contract_comment_entry"] = scrolledtext.ScrolledText(
            contract_frame, height=3, width=30
        )
        form["contract_comment_entry"].grid(row=2, column=1, columnspan=2, sticky="ew")
        form["contract_comment_entry"].bind("<Return>", disable_enter)
        note_frame = ttk.LabelFrame(main_frame, text="Note Section", padding=10)
        note_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        action_frame = ttk.LabelFrame(note_frame, text="Action Note", padding=10)
        action_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        form["action_note_text"] = scrolledtext.ScrolledText(
            action_frame, height=12, width=50
        )
        form["action_note_text"].grid(row=0, column=0, columnspan=3)
        form["action_note_text"].bind(
            "<KeyRelease>", lambda e: self.save_text_state(form, "action_note_text")
        )
        ttk.Button(
            action_frame,
            text="💾 Add to Quick Notes",
            command=lambda: self.add_quick_note(form),
        ).grid(row=1, column=0, pady=5, sticky="w")
        self.view_quick_notes_button = ttk.Button(
            action_frame, text="🔎 View Quick Notes", command=self.view_quick_notes
        )
        self.view_quick_notes_button.grid(row=1, column=1, pady=5, sticky="w")
        preview_frame = ttk.LabelFrame(note_frame, text="Note Preview", padding=10)
        preview_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        form["note_preview_text"] = scrolledtext.ScrolledText(
            preview_frame, height=10, width=50
        )
        form["note_preview_text"].grid(row=0, column=0, columnspan=3)
        ttk.Label(preview_frame, text="Follow-Up in (days):").grid(
            row=1, column=0, sticky="e"
        )
        form["reminder_days"] = ttk.Entry(preview_frame, width=5)
        form["reminder_days"].grid(row=1, column=1, sticky="ew")
        form["reminder_days"].insert(0, "0")
        ttk.Button(
            preview_frame,
            text="⚡Generate Note",
            command=lambda: self.generate_note(form),
        ).grid(row=2, column=0, columnspan=2, pady=5, sticky="w")
        form["submit_button"] = ttk.Button(
            preview_frame, text="💾 Submit Note", command=lambda: self.submit_note(form)
        )
        form["submit_button"].grid(row=2, column=1, columnspan=2, pady=5, sticky="ew")
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")
        ttk.Button(
            button_frame, text="Reset Form", command=lambda: self.reset_fields(form)
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="New Call Tab", command=self.add_new_call_tab
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Replicate Call Tab",
            command=lambda: self.copy_call(form),
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Close Tab", command=lambda: self.close_current_tab()
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="EXIT", command=lambda: self.on_closing()).pack(
            side="left", padx=5, anchor="center"
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
        return form
    def check_previous_cm_ref(self, cm_ref):
        matches = [note for note in self.notes if cm_ref in note["cm_ref"]]
        if matches:
            popup = tk.Toplevel(self.root)
            popup.title(f"Previous Notes for CM Ref# {cm_ref}")
            popup.geometry("400x300")
            popup.transient(self.root)               
            popup.grab_set()              
            text = scrolledtext.ScrolledText(popup, height=15, width=50)
            text.pack(padx=10, pady=10)
            for note in matches:
                text.insert(
                    tk.END,
                    f"Date: {note['date']}\nNote: {note['generated_note']}\n------------------------------------------\n\n",
                )
            text.config(state="disabled")
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
        else:
            messagebox.showinfo(
                "No Matches",
                f"No previous calls found for CM Reference # {cm_ref} within the tool.",
            )
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
    def copy_call(self, form):
        new_form = self.add_new_call_tab()
        new_form["follow_up_var"].set(form["follow_up_var"].get())
        new_form["phone_entry"].insert(0, form["phone_entry"].get())
        new_form["payer_entry"].insert(0, form["payer_entry"].get())
        new_form["agent_entry"].insert(0, form["agent_entry"].get())
        new_form["call_ref_entry"].insert(0, form["call_ref_entry"].get())
        new_form["online_entry"].insert(0, form["online_entry"].get())
        new_form["fax_entry"].insert(0, form["fax_entry"].get())
        new_form["mail_entry"].insert("1.0", form["mail_entry"].get("1.0", tk.END))
        new_form["attn_entry"].insert(0, form["attn_entry"].get())
        new_form["prev_verified_var"].set(1)
    def create_notes_tab(self):
        notes_frame = ttk.Frame(self.notes_tab, padding=10)
        notes_frame.pack(fill="both", expand=True)
        filter_frame = ttk.Frame(notes_frame)
        filter_frame.pack(fill="x")
        ttk.Label(filter_frame, text="Search:").pack(side="left", padx=5)
        self.notes_search_entry = ttk.Entry(filter_frame)
        self.notes_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.notes_today_var = tk.BooleanVar()
        ttk.Checkbutton(
            filter_frame,
            text="Today's Notes",
            variable=self.notes_today_var,
            command=self.update_notes_table,
        ).pack(side="left", padx=5)
        ttk.Label(filter_frame, text="FilterTags:").pack(side="left", padx=5)
        self.notes_tag_filter = ttk.Combobox(
            filter_frame, values=self.tags, state="readonly"
        )
        self.notes_tag_filter.pack(side="left", padx=5)
        self.notes_tag_filter.bind(
            "<<ComboboxSelected>>", lambda e: self.update_notes_table()
        )
        self.edit_tags_button = ttk.Button(
            filter_frame, text="Edit Tags", command=self.edit_tags
        )
        self.edit_tags_button.pack(side="left", padx=5)
        ttk.Button(
            filter_frame, text="ClearFilters", command=self.notes_clear_filters
        ).pack(side="left", padx=5)
        ttk.Button(
            filter_frame, text="InternalNotes", command=self.show_commented_notes
        ).pack(side="left", padx=5)
        ttk.Button(
            filter_frame, text="Export2XL", command=self.notes_export_to_excel
        ).pack(side="left", padx=5)
        table_frame = ttk.Frame(notes_frame)
        table_frame.pack(fill="both", expand=True, padx=5)
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
                "Tags",
                "Comments",
                "Follow-Up Date",
                "Edited",
            ),
            show="headings",
            height=8,
        )
        for col in self.notes_tree["columns"]:
            self.notes_tree.heading(col, text=col)
            self.notes_tree.column(col, width=100)
        v_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.notes_tree.yview
        )
        v_scroll.pack(side="right", fill="y")
        h_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.notes_tree.xview
        )
        h_scroll.pack(side="bottom", fill="x")
        self.notes_tree.configure(
            yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set
        )
        self.notes_tree.pack(side="left", fill="both", expand=True)
        self.update_notes_table()
        edit_frame = ttk.LabelFrame(notes_frame, text="    Selected Note", padding=10)
        edit_frame.pack(fill="x", pady=5)
        self.notes_edit_reference = ttk.Entry(edit_frame)
        self.notes_edit_reference.pack(side="top", fill="x", expand=True)
        self.notes_edit_text = scrolledtext.ScrolledText(
            edit_frame, height=15, width=50
        )
        self.notes_edit_text.pack(fill="x")
        self.copy_button = ttk.Button(
            edit_frame,
            text="Copy",
            command=lambda: self.root.clipboard_append(
                self.notes_edit_text.get("1.0", tk.END)
            ),
            state=tk.DISABLED,                                 
        )
        self.copy_button.pack(side="left", padx=5, pady=5)
        self.update_button = ttk.Button(
            edit_frame,
            text="Update",
            command=self.update_note,
            state=tk.DISABLED,                                 
        )
        self.update_button.pack(side="left", padx=5, pady=5)
        self.delete_button = ttk.Button(
            edit_frame,
            text="Delete",
            command=self.delete_note,
            state=tk.DISABLED,                                 
        )
        self.delete_button.pack(side="left", padx=5, pady=5)
        self.remove_reminder_button = ttk.Button(
            edit_frame,
            text="Remove Follow Up Reminder",
            command=self.remove_reminder,
            state=tk.DISABLED,                                 
        )
        self.remove_reminder_button.pack(side="left", padx=5, pady=5)
        self.add_tags_button = ttk.Button(
            edit_frame,
            text="Add Tags",
            command=self.add_tags_to_note,
            state=tk.DISABLED,                                 
        )
        self.add_tags_button.pack(side="left", padx=5, pady=5)
        self.remove_tags_button = ttk.Button(
            edit_frame,
            text="Remove Tags",
            command=self.remove_tags_from_note,
            state=tk.DISABLED,                                 
        )
        self.remove_tags_button.pack(side="left", padx=5, pady=5)
        self.replicate_button = ttk.Button(
            edit_frame,
            text="Replicate (Display on a New Tab)",
            command=self.open_note_in_new_tab,
            state=tk.DISABLED,                                 
        )
        self.replicate_button.pack(side="left", padx=5, pady=5)
        comment_frame = ttk.LabelFrame(
            notes_frame, text="    Internal Comments", padding=10
        )
        comment_frame.pack(fill="x", pady=5)
        self.notes_comment_text = scrolledtext.ScrolledText(
            comment_frame, height=2, width=50
        )
        self.notes_comment_text.pack(fill="x")
        self.save_comment_button = ttk.Button(
            comment_frame,
            text="Save Comment",
            command=self.save_comment,
            state=tk.DISABLED,                                 
        )
        self.save_comment_button.pack(pady=5)
        self.import_old_csv_button = ttk.Button(
            comment_frame,
            text="Import notes from Old F/U Tool (CSV)",
            command=self.import_csv,
        )
        self.import_old_csv_button.pack(pady=5)
        def combined_handler(event):
            self.notes_show_selected_note(event)
            self.update_buttons_state(self.notes_tree)
        self.notes_tree.bind("<<TreeviewSelect>>", combined_handler)
        self.notes_search_entry.bind(
            "<KeyRelease>", lambda e: self.update_notes_table()
        )
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")], title="Select a CSV file"
        )
        if not file_path:
            return
        try:
            df = pd.read_csv(file_path, encoding="ISO-8859-1")
            new_notes = []
            for _, row in df.iterrows():
                new_note = {
                    "date": (
                        datetime.strptime(str(row["Date"]), "%m/%d/%Y").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if pd.notna(row["Date"])
                        else ""
                    ),
                    "follow_up": (
                        row["Follow Up Type"] if pd.notna(row["Follow Up Type"]) else ""
                    ),
                    "cm_ref": (
                        row["CM Reference"] if pd.notna(row["CM Reference"]) else ""
                    ),
                    "payer": row["Payer"] if pd.notna(row["Payer"]) else "",
                    "phone": row["Phone"] if pd.notna(row["Phone"]) else "",
                    "agent": row["Agent"] if pd.notna(row["Agent"]) else "",
                    "call_ref": (
                        row["Call/Chat Reference"]
                        if pd.notna(row["Call/Chat Reference"])
                        else ""
                    ),
                    "network": row["Network"] if pd.notna(row["Network"]) else "",
                    "plan_type": row["Plan Type"] if pd.notna(row["Plan Type"]) else "",
                    "specialty": (
                        row["Provider Specialty"]
                        if pd.notna(row["Provider Specialty"])
                        else ""
                    ),
                    "pos": row["POS"] if pd.notna(row["POS"]) else "",
                    "online": row["Online"] if pd.notna(row["Online"]) else "",
                    "fax": row["Fax"] if pd.notna(row["Fax"]) else "",
                    "mail": row["Mail"] if pd.notna(row["Mail"]) else "",
                    "attn": "",
                    "prev_verified": (
                        True
                        if pd.notna(row["P. Verified"])
                        and row["P. Verified"] == "Previously Verified"
                        else False
                    ),
                    "cc_name": (
                        row["Contract Name"] if pd.notna(row["Contract Name"]) else ""
                    ),
                    "effective_date": (
                        row["Effective"] if pd.notna(row["Effective"]) else ""
                    ),
                    "contract_comment": "",
                    "action_note": (
                        row["Action Note"] if pd.notna(row["Action Note"]) else ""
                    ),
                    "generated_note": (
                        row["CM Note"] if pd.notna(row["CM Note"]) else ""
                    ),
                    "tags": "",
                    "comments": "",
                    "follow_up_date": "",
                    "edited": "",
                }
                new_notes.append(new_note)
            self.notes.extend(new_notes)
            self.save_json(DATA_FILE, self.notes)
            self.update_notes_table()
            messagebox.showinfo("Success", "CSV data imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")
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
        self.remove_reminder_button.config(state=tk.NORMAL)
        self.add_tags_button.config(state=tk.NORMAL)
        self.remove_tags_button.config(state=tk.NORMAL)
        self.replicate_button.config(state=tk.NORMAL)
        self.save_comment_button.config(state=tk.NORMAL)
    def disable_buttons(self):
        self.copy_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.remove_reminder_button.config(state=tk.DISABLED)
        self.add_tags_button.config(state=tk.DISABLED)
        self.remove_tags_button.config(state=tk.DISABLED)
        self.replicate_button.config(state=tk.DISABLED)
        self.save_comment_button.config(state=tk.DISABLED)
    def create_follow_ups_tab(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, borderwidth=1, relief="solid")
        style.map(
            "Treeview",
            background=[("selected", "green")],
            foreground=[("selected", "white")],
        )
        follow_ups_frame = ttk.Frame(self.follow_ups_tab, padding=10)
        follow_ups_frame.pack(fill="both", expand=True)
        filter_frame = ttk.Frame(follow_ups_frame)
        filter_frame.pack(fill="x")
        ttk.Label(filter_frame, text="Search:").pack(side="left", padx=5)
        self.follow_ups_search_entry = ttk.Entry(filter_frame)
        self.follow_ups_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(
            filter_frame,
            text="Export2XL",
            command=self.follow_ups_export_to_excel,
        ).pack(side="left", padx=5)
        ttk.Button(
            filter_frame, text="ClearSearch", command=self.follow_ups_clear_filters
        ).pack(side="left", padx=5)
        table_frame = ttk.Frame(follow_ups_frame)
        table_frame.pack(fill="both", expand=True)
        self.follow_up_tree = ttk.Treeview(
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
                "Tags",
                "Comments",
                "Follow-Up Date",
                "Edited",
            ),
            show="headings",
            height=10,
            style="Treeview",
        )
        for col in self.follow_up_tree["columns"]:
            self.follow_up_tree.heading(col, text=col)
            self.follow_up_tree.column(col, width=150)
        v_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.follow_up_tree.yview
        )
        v_scroll.pack(side="right", fill="y")
        h_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.follow_up_tree.xview
        )
        h_scroll.pack(side="bottom", fill="x")
        self.follow_up_tree.configure(
            yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set
        )
        self.follow_up_tree.pack(side="left", fill="both", expand=True)
        button_frame = ttk.Frame(follow_ups_frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(
            button_frame, text="Mark Complete", command=self.complete_follow_up
        ).pack(side="left", padx=5)
        self.edit_date_button = ttk.Button(
            button_frame, text="Edit Date", command=self.edit_follow_up_date
        )
        self.edit_date_button.pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Open in New Tab", command=self.open_in_new_tab
        ).pack(side="left", padx=5)
        self.follow_ups_note_text = scrolledtext.ScrolledText(
            follow_ups_frame, height=10, width=50
        )
        self.follow_ups_note_text.pack(fill="x", pady=5)
        self.update_follow_ups_table()
        self.follow_up_tree.bind(
            "<<TreeviewSelect>>", self.follow_ups_show_selected_note
        )
        self.follow_ups_search_entry.bind(
            "<KeyRelease>", lambda e: self.update_follow_ups_table()
        )
    def create_general_notes_tab(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, borderwidth=1, relief="solid")
        style.map(
            "Treeview",
            background=[("selected", "green")],
            foreground=[("selected", "white")],
        )
        general_frame = ttk.Frame(self.general_notes_tab, padding=10)
        general_frame.pack(fill="both", expand=True)
        client_frame = ttk.LabelFrame(
            general_frame, text="Client Information", padding=10
        )
        client_frame.pack(fill="both", expand=True)
        self.client_tree = ttk.Treeview(
            client_frame,
            columns=("Client", "NPI", "Tax ID", "Address"),
            show="headings",
            style="Treeview",
        )
        self.client_tree.heading("Client", text="Client Name")
        self.client_tree.heading("NPI", text="NPI")
        self.client_tree.heading("Tax ID", text="Tax ID")
        self.client_tree.heading("Address", text="Address")
        self.client_tree.pack(fill="both", expand=True)
        self.load_general_notes()
        entry_frame = ttk.Frame(client_frame)
        entry_frame.pack(fill="x", pady=5)
        ttk.Label(entry_frame, text="Client:").pack(side="left", padx=5)
        self.client_entry = ttk.Entry(entry_frame)
        self.client_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(entry_frame, text="NPI:").pack(side="left", padx=5)
        self.npi_entry = ttk.Entry(entry_frame)
        self.npi_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(entry_frame, text="Tax ID:").pack(side="left", padx=5)
        self.tax_id_entry = ttk.Entry(entry_frame)
        self.tax_id_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(entry_frame, text="Address:").pack(side="left", padx=5)
        self.address_entry = ttk.Entry(entry_frame)
        self.address_entry.pack(side="left", fill="x", expand=True, padx=5)
        button_frame = ttk.Frame(client_frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Add Client", command=self.add_client).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Delete Client", command=self.delete_client).pack(
            side="left", padx=5
        )
    def load_general_notes(self):
        general_notes = self.load_json(GENERAL_NOTES_FILE)
        for note in general_notes:
            self.client_tree.insert(
                "",
                "end",
                values=(note["client"], note["npi"], note["tax_id"], note["address"]),
            )
    def add_client(self):
        client = self.client_entry.get().strip()
        npi = self.npi_entry.get().strip()
        tax_id = self.tax_id_entry.get().strip()
        address = self.address_entry.get().strip()
        if client and npi and tax_id and address:
            self.client_tree.insert("", "end", values=(client, npi, tax_id, address))
            general_notes = self.load_json(GENERAL_NOTES_FILE)
            general_notes.append(
                {"client": client, "npi": npi, "tax_id": tax_id, "address": address}
            )
            self.save_json(GENERAL_NOTES_FILE, general_notes)
            self.clear_client_entries()
        else:
            messagebox.showwarning("Error", "All fields are required!")
    def delete_client(self):
        selected = self.client_tree.selection()
        if selected and messagebox.askyesno("Confirm", "Delete this client?"):
            item = self.client_tree.item(selected[0])["values"]
            self.client_tree.delete(selected[0])
            general_notes = [
                note
                for note in self.load_json(GENERAL_NOTES_FILE)
                if note["client"] != item[0] or note["npi"] != item[1]
            ]
            self.save_json(GENERAL_NOTES_FILE, general_notes)
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
            window.lift()
            window.focus_force()
            self.delete_contact_button.config(state=tk.NORMAL)
    def view_contacts(self):
        self.view_contact_button.config(state=tk.DISABLED)
        contacts_window = tk.Toplevel(self.root)
        contacts_window.title("Saved Contacts")
        contacts_window.transient(self.root)               
        contacts_window.grab_set()              
        contacts_window.bind(
            "<Destroy>", lambda event: self.view_contact_button.config(state=tk.NORMAL)
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
        if selected and self.entry_tabs:
            contact = tree.item(selected[0])["values"]
            current_tab = self.entry_tabs[
                self.notebook.index(self.notebook.select()) - 3
            ]
            current_tab["phone_entry"].delete(0, tk.END)
            current_tab["phone_entry"].insert(0, contact[0])
            current_tab["payer_entry"].delete(0, tk.END)
            current_tab["payer_entry"].insert(0, contact[1])
            window.destroy()
        elif not self.entry_tabs:
            messagebox.showwarning("Error", "No active New Call tab!")
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
        else:
            messagebox.showwarning("Error", "Action note is empty!")
    def view_quick_notes(self):
        self.view_quick_notes_button.config(state=tk.DISABLED)
        quick_window = tk.Toplevel(self.root)
        quick_window.title("Quick Notes")
        quick_window.transient(self.root)               
        quick_window.grab_set()              
        quick_window.bind(
            "<Destroy>",
            lambda event: self.view_quick_notes_button.config(state=tk.NORMAL),
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
            text="Use Quick Note",
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
        current_tab = self.entry_tabs[self.notebook.index(self.notebook.select()) - 3]
        existing_text = current_tab["action_note_text"].get("1.0", tk.END).strip()
        new_text = f"({existing_text})\n\n{note}" if existing_text else note
        current_tab["action_note_text"].delete("1.0", tk.END)
        current_tab["action_note_text"].insert("1.0", new_text)
    def generate_note(self, form):
        errors = self.validate_mandatory_fields(form)
        if errors:
            messagebox.showwarning(
                "Validation Error",
                "Missing mandatory fields:\n- " + "\n- ".join(errors),
            )
            return
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
        if form["em_verified_var"].get():
            em_change = form["em_change_entry"].get().strip()
            if em_change:
                note.append(
                    f"The E&M code was verified and has been downcoded to: {em_change}."
                )
            else:
                note.append("The E&M code was verified; no changes were made.")
        if form["emer_verified_var"].get():
            emer_change = form["emer_change_entry"].get().strip()
            if emer_change:
                note.append(
                    f"The Emergency code was verified and has been downcoded to: {emer_change}."
                )
            else:
                note.append("The EEmergency code was verified; no changes were made.")
        if form["drg_verified_var"].get():
            drg_change = form["drg_change_entry"].get().strip()
            if drg_change:
                note.append(
                    f"The DRG code was verified and has been downcoded to: {drg_change}."
                )
            else:
                note.append("The DRG code was verified; no changes were made.")
        if action_note and action_note.upper() != "N/A":
            note.append(f"Comment: {action_note}")
        form["note_preview_text"].delete("1.0", tk.END)
        form["note_preview_text"].insert("1.0", "\n".join(note))
    def submit_note(self, form):
        form["submit_button"].config(state=tk.DISABLED)
        def add_business_days(start_date, days):
            current_date = start_date
            while days > 0:
                current_date += timedelta(days=1)
                if current_date.weekday() < 5:                            
                    days -= 1
            return current_date
        errors = self.validate_mandatory_fields(form)
        if errors:
            messagebox.showwarning(
                "Validation Error",
                "Missing mandatory fields:\n- " + "\n- ".join(errors),
            )
            form["submit_button"].config(state=tk.NORMAL)
            return
        note = form["note_preview_text"].get("1.0", tk.END).strip()
        if not note:
            messagebox.showwarning("Error", "Generate a note first!")
            form["submit_button"].config(state=tk.NORMAL)
            return
        reminder_days = form["reminder_days"].get().strip()
        if reminder_days.isdigit() and int(reminder_days) > 0:
            day_type = messagebox.askquestion(
                "Day Type", "Are the number of days entered Calendar Days?"
            )
            follow_up_date = (
                (datetime.now() + timedelta(days=int(reminder_days))).strftime(
                    "%Y-%m-%d"
                )
                if day_type == "yes"
                else add_business_days(datetime.now(), int(reminder_days)).strftime(
                    "%Y-%m-%d"
                )
            )
        else:
            follow_up_date = ""
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
            "tags": self.get_tags(form),
            "comments": "",
            "follow_up_date": follow_up_date,
            "edited": "",
            "em_verified": form["em_verified_var"].get(),
            "em_change": form["em_change_entry"].get().strip(),
            "emer_verified": form["emer_verified_var"].get(),
            "emer_change": form["emer_change_entry"].get().strip(),
            "drg_verified": form["drg_verified_var"].get(),
            "drg_change": form["drg_change_entry"].get().strip(),
        }
        self.notes.append(entry)
        self.save_json(DATA_FILE, self.notes)
        result = messagebox.askyesno(
            "Keep information entered?",
            "Would you like to keep the entered information for another claim?",
        )
        if result:
            form["submit_button"].config(state=tk.NORMAL)
            follow_up_var = form["follow_up_var"].get()
            phone_entry = form["phone_entry"].get()
            payer_entry = form["payer_entry"].get()
            agent_entry = form["agent_entry"].get()
            call_ref_entry = form["call_ref_entry"].get()
            online_entry = form["online_entry"].get()
            fax_entry = form["fax_entry"].get()
            mail_entry = form["mail_entry"].get("1.0", tk.END)
            attn_entry = form["attn_entry"].get()
            nprev_verified_var = 1
            self.reset_fields(form)
            form["follow_up_var"].set(follow_up_var)
            form["phone_entry"].insert(0, phone_entry)
            form["payer_entry"].insert(0, payer_entry)
            form["agent_entry"].insert(0, agent_entry)
            form["call_ref_entry"].insert(0, call_ref_entry)
            form["online_entry"].insert(0, online_entry)
            form["fax_entry"].insert(0, fax_entry)
            form["mail_entry"].insert("1.0", mail_entry)
            form["attn_entry"].insert(0, attn_entry)
            form["prev_verified_var"].set(nprev_verified_var)
        else:
            form["submit_button"].config(state=tk.NORMAL)
            tab_index = self.notebook.index(self.notebook.select())
            self.notebook.forget(tab_index)
            adjusted_index = tab_index - 3
            if 0 <= adjusted_index < len(self.entry_tabs):
                self.entry_tabs.pop(adjusted_index)
            self.update_notes_table()
            self.update_follow_ups_table()
            if not self.entry_tabs:
                self.add_new_call_tab()
    def get_tags(self, form=None):
        if form:
            form["submit_button"].config(state=tk.DISABLED)
        tags_window = tk.Toplevel(self.root)
        tags_window.title("Select Tags")
        tags_window.geometry("300x500")
        tags_window.attributes("-topmost", True)                                 
        tags_window.grab_set()                         
        selected_tags = []
        for tag in self.tags:
            var = tk.BooleanVar()
            ttk.Checkbutton(
                tags_window,
                text=tag,
                variable=var,
                command=lambda v=var, t=tag: (
                    selected_tags.append(t)
                    if v.get()
                    else selected_tags.remove(t) if t in selected_tags else None
                ),
            ).pack(anchor="w", padx=10, pady=5)
        ttk.Button(tags_window, text="OK", command=tags_window.destroy).pack(pady=10)
        tags_window.wait_window()
        if form:
            form["submit_button"].config(state=tk.NORMAL)
        return selected_tags
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
        form["reminder_days"].delete(0, tk.END)
        form["reminder_days"].insert(0, "0")
        form["em_verified_var"].set(False)
        form["em_change_entry"].delete(0, tk.END)
        form["emer_verified_var"].set(False)
        form["emer_change_entry"].delete(0, tk.END)
        form["drg_verified_var"].set(False)
        form["drg_change_entry"].delete(0, tk.END)
        form["undo_stack"].clear()
        form["redo_stack"].clear()
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
        tag_filter = self.notes_tag_filter.get()
        for note in self.notes:
            if (
                (not self.notes_today_var.get() or note["date"].startswith(today))
                and (
                    not search_term
                    or any(search_term in str(v).lower() for v in note.values())
                )
                and (not tag_filter or tag_filter in note.get("tags", []))
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
                        ", ".join(note.get("tags", [])),
                        note.get("comments", ""),
                        note.get("follow_up_date", ""),
                        note.get("edited", ""),
                    ),
                )
        if (
            not hasattr(self, "notes_edit_text")
            or not hasattr(self, "notes_comment_text")
            or not hasattr(self, "notes_edit_reference")
        ):
            return
        self.notes_edit_text.delete("1.0", tk.END)
        self.notes_comment_text.delete("1.0", tk.END)
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
                    self.notes_comment_text.delete("1.0", tk.END)
                    self.notes_comment_text.insert("1.0", note.get("comments", ""))
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
                    self.save_json(DATA_FILE, self.notes)
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
    def save_comment(self):
        selected = self.notes_tree.selection()
        if selected:
            selected_item_id = selected[0]
            item = self.notes_tree.item(selected_item_id)["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    note["comments"] = self.notes_comment_text.get(
                        "1.0", tk.END
                    ).strip()
                    self.save_json(DATA_FILE, self.notes)
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
    def remove_reminder(self):
        selected = self.notes_tree.selection()
        if selected:
            selected_item_id = selected[0]
            item = self.notes_tree.item(selected_item_id)["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    note["follow_up_date"] = ""
                    self.save_json(DATA_FILE, self.notes)
                    self.update_notes_table()
                    self.update_follow_ups_table()
                    self.notes_edit_text.delete("1.0", tk.END)
                    self.notes_comment_text.delete("1.0", tk.END)
                    self.notes_edit_reference.delete(0, tk.END)
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
            self.save_json(DATA_FILE, self.notes)
            self.notes_tree.delete(selected[0])
            self.notes_edit_text.delete("1.0", tk.END)
            self.notes_comment_text.delete("1.0", tk.END)
            self.notes_edit_reference.delete(0, tk.END)
            self.update_follow_ups_table()
    def add_tags_to_note(self):
        self.add_tags_button.config(state=tk.DISABLED)
        selected = self.notes_tree.selection()
        if selected:
            selected_item_id = selected[0]
            item = self.notes_tree.item(selected_item_id)["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    new_tags = self.get_tags()
                    note["tags"] = list(set(note.get("tags", []) + new_tags))
                    self.save_json(DATA_FILE, self.notes)
                    self.notes_edit_text.delete("1.0", tk.END)
                    self.notes_comment_text.delete("1.0", tk.END)
                    self.notes_edit_reference.delete(0, tk.END)
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
        self.add_tags_button.config(state=tk.NORMAL)
    def remove_tags_from_note(self):
        self.remove_tags_button.config(state=tk.DISABLED)
        selected = self.notes_tree.selection()
        if selected:
            selected_item_id = selected[0]
            item = self.notes_tree.item(selected_item_id)["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    tags_window = tk.Toplevel(self.root)
                    tags_window.title("Remove Tags")
                    tags_window.geometry("300x500")
                    tags_window.attributes(
                        "-topmost", True
                    )                                 
                    tags_window.grab_set()                        
                    tags_window.bind(
                        "<Destroy>",
                        lambda event: self.remove_tags_button.config(state=tk.NORMAL),
                    )
                    current_tags = note.get("tags", [])
                    tags_to_remove = []
                    for tag in current_tags:
                        var = tk.BooleanVar()
                        ttk.Checkbutton(
                            tags_window,
                            text=tag,
                            variable=var,
                            command=lambda v=var, t=tag: (
                                tags_to_remove.append(t)
                                if v.get()
                                else (
                                    tags_to_remove.remove(t)
                                    if t in tags_to_remove
                                    else None
                                )
                            ),
                        ).pack(anchor="w", padx=10, pady=5)
                    ttk.Button(
                        tags_window, text="OK", command=tags_window.destroy
                    ).pack(pady=10)
                    tags_window.wait_window()
                    note["tags"] = [t for t in current_tags if t not in tags_to_remove]
                    self.save_json(DATA_FILE, self.notes)
                    self.notes_edit_text.delete("1.0", tk.END)
                    self.notes_comment_text.delete("1.0", tk.END)
                    self.notes_edit_reference.delete(0, tk.END)
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
                "Tags",
                "Comments",
                "Follow-Up Date",
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
        self.notes_tag_filter.set("")
        self.notes_edit_text.delete("1.0", tk.END)
        self.notes_comment_text.delete("1.0", tk.END)
        self.notes_edit_reference.delete(0, tk.END)
        self.update_notes_table()
    def edit_tags(self):
        self.edit_tags_button.config(state=tk.DISABLED)
        tags_window = tk.Toplevel(self.root)
        tags_window.title("Edit Tags")
        tags_window.geometry("300x500")
        tags_window.attributes("-topmost", True)                                 
        tags_window.grab_set()                         
        tags_window.bind(
            "<Destroy>", lambda event: self.edit_tags_button.config(state=tk.NORMAL)
        )
        listbox = tk.Listbox(tags_window, height=15)
        for tag in self.tags:
            listbox.insert(tk.END, tag)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.add_tag_button = ttk.Button(
            tags_window, text="Add Tag", command=lambda: self.add_tag(listbox)
        )
        self.add_tag_button.pack(pady=5)
        ttk.Button(
            tags_window, text="Remove Tag", command=lambda: self.remove_tag(listbox)
        ).pack(pady=5)
        ttk.Button(
            tags_window,
            text="Save",
            command=lambda: self.save_tags(listbox, tags_window),
        ).pack(pady=5)
    def add_tag(self, listbox):
        self.add_tag_button.config(state=tk.DISABLED)
        dialog_window = tk.Toplevel(self.root)
        dialog_window.title("Add Tag")
        dialog_window.geometry("300x150")
        dialog_window.attributes("-topmost", True)                                 
        dialog_window.grab_set()                         
        dialog_window.bind(
            "<Destroy>", lambda event: self.add_tag_button.config(state=tk.NORMAL)
        )
        tk.Label(dialog_window, text="Enter new tag:").pack(pady=10)
        new_tag_entry = tk.Entry(dialog_window)
        new_tag_entry.pack(pady=5)
        def on_ok():
            new_tag = new_tag_entry.get().strip()
            if new_tag and new_tag not in self.tags:
                listbox.insert(tk.END, new_tag)
                self.tags.append(new_tag)
            dialog_window.destroy()
        tk.Button(dialog_window, text="OK", command=on_ok).pack(pady=10)
        dialog_window.wait_window()
    def remove_tag(self, listbox):
        selected = listbox.curselection()
        if selected:
            tag = listbox.get(selected[0])
            listbox.delete(selected[0])
            self.tags.remove(tag)
    def save_tags(self, listbox, window):
        self.tags = list(listbox.get(0, tk.END))
        self.save_json(TAGS_FILE, self.tags)
        self.notes_tag_filter["values"] = self.tags
        window.destroy()
        self.edit_tags_button.config(state=tk.NORMAL)
    def show_commented_notes(self):
        comments_window = tk.Toplevel(self.root)
        comments_window.title("Notes with Ineternal Comments")
        comments_window.geometry("800x600")
        comments_window.transient(self.root)               
        comments_window.grab_set()              
        filter_frame = ttk.Frame(comments_window)
        filter_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(filter_frame, text="Search:").pack(side="left", padx=5)
        self.comments_search_entry = ttk.Entry(filter_frame)
        self.comments_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(
            filter_frame, text="Export2XL", command=self.comments_export_to_excel
        ).pack(side="left", padx=5)
        ttk.Button(
            filter_frame, text="Clear Search", command=self.comments_clear_filters
        ).pack(side="left", padx=5)
        tree_frame = ttk.Frame(comments_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.comments_tree = ttk.Treeview(
            tree_frame,
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
                "Tags",
                "Comments",
                "Follow-Up Date",
                "Edited",
            ),
            show="headings",
        )
        for col in self.comments_tree["columns"]:
            self.comments_tree.heading(col, text=col)
            self.comments_tree.column(col, width=100)
        self.comments_tree.pack(side="left", fill="both", expand=True)
        v_scroll = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.comments_tree.yview
        )
        v_scroll.pack(side="right", fill="y")
        h_scroll = ttk.Scrollbar(
            comments_window, orient="horizontal", command=self.comments_tree.xview
        )
        h_scroll.pack(fill="x")
        self.comments_tree.configure(
            yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set
        )
        self.comments_note_text = scrolledtext.ScrolledText(
            comments_window, height=10, width=50
        )
        self.comments_note_text.pack(fill="x", pady=5)
        button_frame = ttk.Frame(comments_window)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(
            button_frame,
            text="Edit Comment",
            command=lambda: self.edit_comment(self.comments_tree, comments_window),
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Delete Comment",
            command=lambda: self.delete_comment(self.comments_tree, comments_window),
        ).pack(side="left", padx=5)
        self.update_comments_table()
        self.comments_tree.bind("<<TreeviewSelect>>", self.comments_show_selected_note)
        self.comments_search_entry.bind(
            "<KeyRelease>", lambda e: self.update_comments_table()
        )
    def update_comments_table(self, event=None):
        self.comments_note_text.delete("1.0", tk.END)
        for item in self.comments_tree.get_children():
            self.comments_tree.delete(item)
        search_term = self.comments_search_entry.get().lower()
        for note in self.notes:
            if note.get("comments", "") and (
                not search_term
                or any(search_term in str(v).lower() for v in note.values())
            ):
                self.comments_tree.insert(
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
                        ", ".join(note.get("tags", [])),
                        note.get("comments", ""),
                        note.get("follow_up_date", ""),
                        note.get("edited", ""),
                    ),
                )
    def comments_show_selected_note(self, event):
        selected = self.comments_tree.selection()
        if selected:
            item = self.comments_tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    self.comments_note_text.delete("1.0", tk.END)
                    self.comments_note_text.insert("1.0", note["comments"])
                    break
    def edit_comment(self, tree, window):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])["values"]
            new_comment = simpledialog.askstring(
                "Edit Comment", "Enter new comment:", initialvalue=item[22]
            )
            if new_comment is not None:
                self.comments_note_text.delete("1.0", tk.END)
                for note in self.notes:
                    if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                        item[2]
                    ):
                        note["comments"] = new_comment
                        self.save_json(DATA_FILE, self.notes)
                        tree.item(
                            selected[0],
                            values=(
                                item[0],
                                item[1],
                                item[2],
                                item[3],
                                item[4],
                                item[5],
                                item[6],
                                item[7],
                                item[8],
                                item[9],
                                item[10],
                                item[11],
                                item[12],
                                item[13],
                                item[14],
                                item[15],
                                item[16],
                                item[17],
                                item[18],
                                item[19],
                                item[20],
                                item[21],
                                new_comment,
                                item[23],
                                item[24],
                            ),
                        )
                        self.update_notes_table()
                        window.lift()
                        window.focus_force()
                        window.transient(self.root)               
                        window.grab_set()              
                        break
    def delete_comment(self, tree, window):
        selected = tree.selection()
        if selected and messagebox.askyesno("Confirm", "Delete this comment?"):
            item = tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    note["comments"] = ""
                    self.save_json(DATA_FILE, self.notes)
                    tree.delete(selected[0])
                    self.update_notes_table()
                    self.comments_note_text.delete("1.0", tk.END)
                    window.lift()
                    window.focus_force()
                    break
    def comments_export_to_excel(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = [
            list(self.comments_tree.item(item)["values"])
            for item in self.comments_tree.get_children()
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
                "Tags",
                "Comments",
                "Follow-Up Date",
                "Edited",
            ],
        )
        export_path = os.path.join(
            os.path.expanduser("~/Downloads"), f"internal_notes_export_{timestamp}.xlsx"
        )
        df.to_excel(export_path, index=False)
        messagebox.showinfo("Success", f"Exported to {export_path}")
    def comments_clear_filters(self):
        self.comments_search_entry.delete(0, tk.END)
        self.update_comments_table()
    def update_follow_ups_table(self, event=None):
        self.follow_ups_note_text.delete("1.0", tk.END)
        for item in self.follow_up_tree.get_children():
            self.follow_up_tree.delete(item)
        today = date.today().strftime("%Y-%m-%d")
        search_term = self.follow_ups_search_entry.get().lower()
        for note in self.notes:
            if note.get("follow_up_date", "") and (
                not search_term
                or any(search_term in str(v).lower() for v in note.values())
            ):
                self.follow_up_tree.insert(
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
                        ", ".join(note.get("tags", [])),
                        note.get("comments", ""),
                        note.get("follow_up_date", ""),
                        note.get("edited", ""),
                    ),
                )
                if note["follow_up_date"] < today:
                    self.follow_up_tree.item(
                        self.follow_up_tree.get_children()[-1], tags=("overdue",)
                    )
        self.follow_up_tree.tag_configure("overdue", background="light coral")
    def follow_ups_show_selected_note(self, event):
        selected = self.follow_up_tree.selection()
        if selected:
            item = self.follow_up_tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    self.follow_ups_note_text.delete("1.0", tk.END)
                    self.follow_ups_note_text.insert("1.0", note["generated_note"])
                    break
    def complete_follow_up(self):
        selected = self.follow_up_tree.selection()
        if selected:
            item = self.follow_up_tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    note["follow_up_date"] = ""
                    self.save_json(DATA_FILE, self.notes)
                    self.update_follow_ups_table()
                    self.update_notes_table()
                    break
    def edit_follow_up_date(self):
        self.edit_date_button.config(state=tk.DISABLED)
        selected = self.follow_up_tree.selection()
        if selected:
            item = self.follow_up_tree.item(selected[0])["values"]
            date_window = tk.Toplevel(self.root)
            date_window.title("Edit Follow-Up Date")
            date_window.transient(self.root)               
            date_window.grab_set()              
            date_window.bind(
                "<Destroy>", lambda event: self.edit_date_button.config(state=tk.NORMAL)
            )
            ttk.Label(date_window, text="New Follow-Up Date (YYYY-MM-DD):").pack(
                padx=10, pady=5
            )
            new_date = ttk.Entry(date_window)
            new_date.pack(padx=10, pady=5)
            ttk.Button(
                date_window,
                text="Save",
                command=lambda: self.save_new_date(item, new_date.get(), date_window),
            ).pack(pady=5)
        else:
            self.edit_date_button.config(state=tk.NORMAL)
    def save_new_date(self, item, new_date, window):
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    note["follow_up_date"] = new_date
                    self.save_json(DATA_FILE, self.notes)
                    self.update_follow_ups_table()
                    self.update_notes_table()
                    break
            window.destroy()
        except ValueError:
            messagebox.showwarning("Error", "Invalid date format (use YYYY-MM-DD)")
    def open_in_new_tab(self):
        selected = self.follow_up_tree.selection()
        if selected:
            item = self.follow_up_tree.item(selected[0])["values"]
            for note in self.notes:
                if str(note["date"]) == str(item[0]) and str(note["cm_ref"]) == str(
                    item[2]
                ):
                    new_form = self.add_new_call_tab()
                    self.fill_form(new_form, note)
                    break
    def follow_ups_export_to_excel(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = [
            list(self.follow_up_tree.item(item)["values"])
            for item in self.follow_up_tree.get_children()
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
                "Tags",
                "Comments",
                "Follow-Up Date",
                "Edited",
            ],
        )
        export_path = os.path.join(
            os.path.expanduser("~/Downloads"),
            f"pending_follow_ups_export_{timestamp}.xlsx",
        )
        df.to_excel(export_path, index=False)
        messagebox.showinfo("Success", f"Exported to {export_path}")
    def follow_ups_clear_filters(self):
        self.follow_ups_search_entry.delete(0, tk.END)
        self.update_follow_ups_table()
    def fill_form(self, form, note):
        form["follow_up_var"].set(note["follow_up"])
        form["cm_ref_entry"].insert(0, note["cm_ref"])
        form["phone_entry"].insert(0, note["phone"])
        form["payer_entry"].insert(0, note["payer"])
        form["agent_entry"].insert(0, note["agent"])
        form["call_ref_entry"].insert(0, note["call_ref"])
        form["network_var"].set(note["network"])
        form["plan_type_entry"].insert(0, note["plan_type"])
        form["specialty_entry"].insert(0, note["specialty"])
        form["pos_entry"].insert(0, note["pos"])
        form["online_entry"].insert(0, note["online"])
        form["fax_entry"].insert(0, note["fax"])
        form["mail_entry"].insert("1.0", note["mail"])
        form["attn_entry"].insert(0, note.get("attn", ""))
        form["prev_verified_var"].set(note["prev_verified"])
        form["cc_name_entry"].insert(0, note["cc_name"])
        form["effective_date_entry"].insert(0, note["effective_date"])
        form["contract_comment_entry"].insert("1.0", note["contract_comment"])
        form["action_note_text"].insert("1.0", note["action_note"])
        form["reminder_days"].delete(0, tk.END)
        form["reminder_days"].insert(0, "0")
        form["em_verified_var"].set(note.get("em_verified", False))
        form["em_change_entry"].insert(0, note.get("em_change", ""))
        form["emer_verified_var"].set(note.get("emer_verified", False))
        form["emer_change_entry"].insert(0, note.get("emer_change", ""))
        form["drg_verified_var"].set(note.get("drg_verified", False))
        form["drg_change_entry"].insert(0, note.get("drg_change", ""))
    def show_follow_up_details(self, event):
        self.follow_ups_show_selected_note(event)
    def on_closing(self):
        result = messagebox.askyesno("Exit", "Do you really want to exit?")
        if result:
            self.save_json(DATA_FILE, self.notes)
            self.root.quit()
if __name__ == "__main__":
    root = tk.Tk()
    app = CallDetailsApp(root)
    root.mainloop()
