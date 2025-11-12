#!/usr/bin/env python3
"""
ExamGoal Explorer - Modern CTk GUI
Uses data_manager.Filter.get_possible_filter_values to populate dropdown filters.
Dropdown selection updates the visible question set; filters are cumulative and can be reset.
Clusters can be generated and exported via pdfy.
Note: requires `customtkinter` (pip install customtkinter). Combobox and Treeview remain ttk widgets.
"""

import json
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox



from core import DataBase, Filter,pdfy
#import pdfy

APP_TITLE = "ExamGoal Explorer"
SCHEMA_VERSION = "v004"

# Modern appearance
ctk.set_appearance_mode("Dark")   # "System", "Dark", "Light"
ctk.set_default_color_theme("blue") # built-in: "blue", "dark-blue", "green"


class App(ctk.CTk):
    def __init__(self):
                # ...existi
        super().__init__()

        # Make ttk Treeview match CTk dark theme
        style = ttk.Style()
        try:
            style.theme_use("clam")   # clam is easiest to style reliably
        except Exception:
            pass

        style.configure(
            "Treeview",
            background="#1e1e1e",       # row background
            fieldbackground="#1e1e1e",  # area behind rows
            foreground="#dcdcdc",       # row text color
            rowheight=28,
            font=("Segoe UI", 10)
        )
        style.map(
            "Treeview",
            background=[("selected", "#2a6bdc"), ("!selected", "#1e1e1e")],
            foreground=[("selected", "#ffffff"), ("!selected", "#dcdcdc")]
        )
        style.configure(
            "Treeview.Heading",
            background="#2b2b2b",
            foreground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        style.configure("Vertical.TScrollbar", troughcolor="#2b2b2b", background="#2a2a2a", arrowcolor="#dcdcdc")

        self.title(APP_TITLE)
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Data
        self.db = None
        self.filter = None
        self._clusters = None

        # UI vars
        self._busy = tk.BooleanVar(value=False)
        self._status = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self):
        # Top toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkButton(toolbar, text="Load DB", command=self.load_db, width=100).pack(side="left", padx=6)
        ctk.CTkButton(toolbar, text="Cluster", command=self.run_cluster, width=100).pack(side="left", padx=6)
        ctk.CTkButton(toolbar, text="Export HTML", command=self.export_html, width=120).pack(side="left", padx=6)

        # ...existing code...
        # Status label (right aligned)

        status_label = ctk.CTkLabel(toolbar, text=self._status.get(), anchor="e")
        status_label.pack(side="right", padx=6)
        self._status_label = status_label
        # Ensure CTkLabel updates when the StringVar changes (some CTk versions don't auto-update textvariable)
        try:
            self._status.trace_add("write", lambda *a: self._status_label.configure(text=self._status.get()))
        except Exception:
            # fallback: if trace_add unavailable, try binding textvariable (best-effort)
            try:
                status_label.configure(textvariable=self._status)
            except Exception:
                pass
# ...existing code...
        # Filter panel
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(filter_frame, text="Field:").pack(side="left", padx=(8, 4))
        self.param_cb = ttk.Combobox(filter_frame, state="readonly", width=28)
        self.param_cb.pack(side="left", padx=4)
        self.param_cb.bind("<<ComboboxSelected>>", lambda e: self.on_param_selected())

        ctk.CTkLabel(filter_frame, text="Value:").pack(side="left", padx=(12, 4))
        self.value_cb = ttk.Combobox(filter_frame, state="readonly", width=48)
        self.value_cb.pack(side="left", padx=4)

        ctk.CTkButton(filter_frame, text="Apply", command=self.apply_selected_filter, width=90).pack(side="left", padx=8)
        ctk.CTkButton(filter_frame, text="Reset", command=self.reset_filters, width=90).pack(side="left", padx=4)

        # Main area: Treeview (no long 'text' column)
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        cols = ("id", "exam", "year", "subject", "chapter")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=140, anchor="w")
        self.tree.pack(fill="both", expand=True, side="left")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # Progress bar (ttk indeterminate for simplicity)
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", side="bottom", padx=12, pady=8)

    # --------------------------
    # Database / Filter actions
    # --------------------------
    def load_db(self):
        self._set_busy(True, "Loading database...")
        def _load():
            try:
                data_base_path = "/storage/emulated/0/db_01/jee_mains_pyqs_data_base"
                cache_path = f"{data_base_path}/cache"
                self.db = DataBase(data_base_path = "/storage/emulated/0/db_01/jee_mains_pyqs_data_base",
cache_path = f"{data_base_path}/cache")
                self.filter = Filter(self.db.chapters_dict)
                self.after(0, self._populate_tree)
                self.after(0, self._populate_filter_fields)
                self.after(0, lambda: self._status.set(f"Loaded {len(self.filter.current_set)} questions."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Load Failed", str(e)))
            finally:
                self.after(0, lambda: self._set_busy(False))
        threading.Thread(target=_load, daemon=True).start()

    def _populate_filter_fields(self):
        if not self.filter:
            self.param_cb["values"] = []
            self.value_cb["values"] = []
            return
        try:
            poss = self.filter.get_possible_filter_values()
            params = sorted(poss.keys())
        except Exception:
            params = sorted(list(self.filter.filterable_param)) if hasattr(self.filter, "filterable_param") else []
        self.param_cb["values"] = params
        self.param_cb.set("")
        self.value_cb["values"] = []
        self.value_cb.set("")

    def on_param_selected(self):
        param = self.param_cb.get()
        if not param or not self.filter:
            return
        poss = self.filter.get_possible_filter_values()
        vals = poss.get(param, [])
        display_vals = []
        for v in vals:
            if v is None:
                display_vals.append("None")
            elif isinstance(v, (dict, list, tuple, bool)):
                try:
                    display_vals.append(json.dumps(v, default=str, sort_keys=True))
                except Exception:
                    display_vals.append(str(v))
            else:
                display_vals.append(str(v))
        # dedupe
        seen = set()
        unique = []
        for s in display_vals:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        self.value_cb["values"] = unique
        if unique:
            self.value_cb.set(unique[0])
        else:
            self.value_cb.set("")

    def apply_selected_filter(self):
        if not self.filter:
            messagebox.showwarning("Warning", "Load the database first.")
            return
        param = self.param_cb.get()
        value_str = self.value_cb.get()
        if not param:
            messagebox.showwarning("Warning", "Select a filter field.")
            return
        if value_str == "":
            messagebox.showwarning("Warning", "Select a filter value.")
            return

        self._set_busy(True, f"Filtering by {param} = {value_str}...")
        def _apply():
            try:
                if value_str == "None":
                    target_val = None
                else:
                    try:
                        target_val = json.loads(value_str)
                    except Exception:
                        try:
                            target_val = int(value_str)
                        except Exception:
                            target_val = value_str

                new_set = []
                for q in self.filter.current_set:
                    attr = getattr(q, param, None)
                    if isinstance(attr, (list, dict, tuple)):
                        try:
                            attr_s = json.dumps(attr, default=str, sort_keys=True)
                        except Exception:
                            attr_s = str(attr)
                        match = attr_s == (json.dumps(target_val, default=str, sort_keys=True) if not isinstance(target_val, str) else target_val)
                    else:
                        if isinstance(attr, bool) and isinstance(target_val, str):
                            match = str(attr) == target_val
                        else:
                            match = attr == target_val
                    if match:
                        new_set.append(q)

                self.filter.current_set = new_set
                self.after(0, self._populate_tree)
                self.after(0, self._populate_filter_fields)
                self.after(0, lambda: self._status.set(f"Filtered to {len(self.filter.current_set)} questions."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Filter Failed", str(e)))
            finally:
                self.after(0, lambda: self._set_busy(False))
        threading.Thread(target=_apply, daemon=True).start()

    def reset_filters(self):
        if not self.db:
            return
        self._set_busy(True, "Resetting filters...")
        def _reset():
            try:
                self.filter = Filter(self.db.chapters_dict)
                self.after(0, self._populate_tree)
                self.after(0, self._populate_filter_fields)
                self.after(0, lambda: self._status.set(f"Reset — {len(self.filter.current_set)} questions."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Reset Failed", str(e)))
            finally:
                self.after(0, lambda: self._set_busy(False))
        threading.Thread(target=_reset, daemon=True).start()

    # --------------------------
    # Clustering / Export
    # --------------------------
    def run_cluster(self):
        if not self.filter:
            messagebox.showwarning("Warning", "Load the database first.")
            return
        self._set_busy(True, "Running clustering...")
        def _cluster():
            try:
                clusters = self.filter.cluster()
                self._clusters = clusters
                self.after(0, lambda: self._status.set(f"Clustered into {len(clusters)} groups."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Clustering Failed", str(e)))
            finally:
                self.after(0, lambda: self._set_busy(False))
        threading.Thread(target=_cluster, daemon=True).start()

    def export_html(self):
        if not self._clusters:
            messagebox.showinfo("Info", "Run clustering first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not path:
            return
        self._set_busy(True, "Exporting clusters to HTML...")
        def _export():
            try:
                pdfy.render_cluster_to_html(self._clusters, path)
                self.after(0, lambda: self._status.set(f"Exported HTML to {path}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Export Failed", str(e)))
            finally:
                self.after(0, lambda: self._set_busy(False))
        threading.Thread(target=_export, daemon=True).start()

    # --------------------------
    # UI helpers
    # --------------------------
    def _set_busy(self, busy: bool, msg=""):
        self._busy.set(busy)
        self._status.set(msg or "Ready")
        if busy:
            try:
                self.progress.start(10)
            except Exception:
                pass
        else:
            try:
                self.progress.stop()
            except Exception:
                pass

# ...existing code...
    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        if not self.filter or not getattr(self.filter, "current_set", None):
            self._status.set("No questions to display.")
            return

        count = 0
        for q in self.filter.current_set:
            tid = getattr(q, "question_id", "") or ""
            exam = getattr(q, "exam", "") or ""
            year = getattr(q, "year", "") or ""
            subject = getattr(q, "subject", "") or ""
            chapter = getattr(q, "chapter", "") or ""
            self.tree.insert("", "end", values=(tid, exam, year, subject, chapter))
            count += 1

        # Update status with current visible question count
        self._status.set(f"Showing {count} questions.")
# ...existing code...


if __name__ == "__main__":
    app = App()
    app.mainloop()