# === ADDITIONAL FEATURE FOR VICTORIES/SETBACKS ===
from tkinter import messagebox
import tkinter as tk
import json
import os
from datetime import datetime, timedelta
import webbrowser

JOURNAL_FILE = "journal_entries.json"
SAVE_FILE = "streakstep_data.json"
DEBUG_MODE = False
SHOW_FULL_TIMER_DEBUG = False  # Toggle full/simple timer at launch

class StreakStepApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StreakStep - Day Timer Tracker")
        self.root.geometry("320x200")
        self.root.configure(bg="#2C3E50")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.full_timer_mode = SHOW_FULL_TIMER_DEBUG
        self.congrats_shown = False

        self.data = self.load_data()

        # === UI ===
        self.debug_label = tk.Label(root, text="", font=("Helvetica", 10), bg="#2C3E50", fg="#95A5A6")
        self.debug_label.pack(pady=(5, 0))

        self.motivation_label = tk.Label(root, text="You can do it!", font=("Helvetica", 16, "bold"), fg="#ECF0F1", bg="#2C3E50")
        self.motivation_label.pack(pady=(5, 5))

        self.timer_label = tk.Label(root, text="", font=("Helvetica", 22), fg="#FFFFFF", bg="#2C3E50")
        self.timer_label.pack(pady=5)

        btn_frame = tk.Frame(root, bg="#2C3E50")
        btn_frame.pack(pady=15)

        self.tempted_btn = tk.Button(
            btn_frame, text="I'm Tempted", width=14, font=("Helvetica", 10, "bold"),
            bg="#888A83", fg="white", command=self.open_bible
        )
        self.tempted_btn.grid(row=0, column=0, padx=8)

        self.failed_btn = tk.Button(
            btn_frame, text="I Couldn't Do It :c", width=14, font=("Helvetica", 10, "bold"),
            bg="#E25546", fg="white", command=self.failed
        )
        self.failed_btn.grid(row=0, column=1, padx=8)

        if DEBUG_MODE:
            self.sim_btn = tk.Button(
                root, text="Simulate Day Pass", font=("Helvetica", 10, "bold"),
                bg="#7F8C8D", fg="white", command=self.simulate_day
            )
            self.sim_btn.pack(pady=(0, 6))

        self.journal_button = tk.Button(
            root, text="Journal Menu", font=("Helvetica", 10), bg="#3498DB", fg="white",
            command=self.open_journal_menu
        )
        self.journal_button.pack(pady=(0, 6))

        self.root.bind("<space>", self.toggle_timer_mode)
        self.update_timer()

    def open_bible(self):
        webbrowser.open("https://www.bible.com/bible")

    def failed(self):
        self.data = {
            "streak": 0,
            "goal_days": 1,
            "last_goal_start": datetime.now()
        }
        self.save_data()
        self.update_timer()

    def simulate_day(self):
        self.data["last_goal_start"] -= timedelta(days=1)
        self.update_timer()

    def toggle_timer_mode(self, event=None):
        self.full_timer_mode = not self.full_timer_mode
        self.update_timer()

    def update_timer(self):
        now = datetime.now()
        goal_end = self.data["last_goal_start"] + timedelta(days=self.data["goal_days"])
        remaining = goal_end - now

        if remaining.total_seconds() <= 0:
            self.timer_label.config(text="0 Days")
            if not self.congrats_shown:
                self.congrats_shown = True
                self.ask_continue_or_reset()
        else:
            self.congrats_shown = False
            if self.full_timer_mode:
                days = remaining.days
                hours, rem = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(rem, 60)
                self.timer_label.config(text=f"{days}d {hours}h {minutes}m {seconds}s")
                self.debug_label.config(text="Mode: Full Timer (SPACE)")
            else:
                days = remaining.days + (1 if remaining.seconds > 0 else 0)
                label = "Day left" if days == 1 else "Days left"
                self.timer_label.config(text=f"{days} {label}")
                self.debug_label.config(text="Mode: Simple Timer (SPACE)")

        self.root.after(1000, self.update_timer)

    def ask_continue_or_reset(self):
        result = messagebox.askyesno("Goal Reached!", "Well done! Want to add another day to your goal?")
        if result:
            self.data["streak"] += 1
            self.data["goal_days"] += 1
            self.data["last_goal_start"] = datetime.now()
        else:
            self.data["streak"] = 0
            self.data["goal_days"] = 1
            self.data["last_goal_start"] = datetime.now()
        self.save_data()

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                data["last_goal_start"] = datetime.fromisoformat(data["last_goal_start"])
                return data
            except Exception as e:
                print("Error loading save file:", e)
        return {
            "streak": 0,
            "goal_days": 1,
            "last_goal_start": datetime.now()
        }

    def save_data(self):
        data_to_save = self.data.copy()
        data_to_save["last_goal_start"] = self.data["last_goal_start"].isoformat()
        with open(SAVE_FILE, "w") as f:
            json.dump(data_to_save, f)

    def open_journal_menu(self):
        journal_window = tk.Toplevel(self.root)
        journal_window.title("Journal Entry")
        journal_window.geometry("260x200")
        journal_window.configure(bg="#34495E")
        journal_window.resizable(False, False)

        label = tk.Label(journal_window, text="Victory or Setback?", font=("Helvetica", 12), fg="white", bg="#34495E")
        label.pack(pady=10)

        entry_title = tk.Entry(journal_window, font=("Helvetica", 10))
        entry_title.pack(pady=5)
        entry_title.insert(0, "Title")

        choice_var = tk.StringVar(value="victory")
        victory_button = tk.Radiobutton(
            journal_window, text="Victory", variable=choice_var, value="victory",
            font=("Helvetica", 10), bg="#34495E", fg="lightgreen", selectcolor="#2C3E50"
        )
        victory_button.pack()

        setback_button = tk.Radiobutton(
            journal_window, text="Setback", variable=choice_var, value="setback",
            font=("Helvetica", 10), bg="#34495E", fg="#E74C3C", selectcolor="#2C3E50"
        )
        setback_button.pack()

        save_button = tk.Button(
            journal_window, text="Save Entry", font=("Helvetica", 10, "bold"), bg="#2ECC71", fg="white",
            command=lambda: self.save_journal_entry(entry_title.get(), choice_var.get(), journal_window)
        )
        save_button.pack(pady=10)

    def save_journal_entry(self, title, entry_type, window):
        if not title.strip():
            messagebox.showwarning("Missing Title", "Please enter a title.")
            return

        entry = {
            "title": title.strip(),
            "type": entry_type,
            "timestamp": datetime.now().isoformat()
        }

        entries = []
        if os.path.exists(JOURNAL_FILE):
            with open(JOURNAL_FILE, "r") as f:
                try:
                    entries = json.load(f)
                except:
                    pass

        entries.insert(0, entry)  # newest first

        with open(JOURNAL_FILE, "w") as f:
            json.dump(entries, f, indent=2)

        window.destroy()
        self.show_journal_entries()

    def show_journal_entries(self):
        if not os.path.exists(JOURNAL_FILE):
            return

        with open(JOURNAL_FILE, "r") as f:
            entries = json.load(f)

        entries_window = tk.Toplevel(self.root)
        entries_window.title("Your Journal Entries")
        entries_window.geometry("320x220")
        entries_window.configure(bg="#1C2833")

        for entry in entries:
            color = "#2ECC71" if entry["type"] == "victory" else "#E74C3C"
            frame = tk.Frame(entries_window, bg="#1C2833")
            frame.pack(fill="x", padx=10, pady=3)
            tk.Label(
                frame, text="✦", font=("Helvetica", 14), fg=color, bg="#1C2833"
            ).pack(side="left")
            tk.Label(
                frame, text=entry["title"], font=("Helvetica", 10), fg="white", bg="#1C2833"
            ).pack(side="left", padx=8)

    def open_entry_view(self, entry):
        view_window = tk.Toplevel(self.root)
        view_window.title(f"View/Edit Entry: {entry['title']}")

        tk.Label(view_window, text="Title:").pack()
        title_entry = tk.Entry(view_window, width=40)
        title_entry.insert(0, entry["title"])
        title_entry.pack()

        tk.Label(view_window, text="Type:").pack()
        type_entry = tk.Entry(view_window, width=40)
        type_entry.insert(0, entry["type"])
        type_entry.pack()

        tk.Label(view_window, text="Description:").pack()
        desc_text = tk.Text(view_window, width=50, height=10)
        desc_text.insert("1.0", entry.get("description", ""))
        desc_text.pack()

    def save_changes():
        entry["title"] = title_entry.get()
        entry["type"] = type_entry.get()
        entry["description"] = desc_text.get("1.0", "end").strip()

        # Save to JSON file
        with open(JOURNAL_FILE, "w") as f:
            json.dump(self.entries, f, indent=4)

        messagebox.showinfo("Updated", "Entry updated successfully!")
        view_window.destroy()

    def delete_entry():
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
        if confirm:
            self.entries.remove(entry)

            # Save to JSON file
            with open(JOURNAL_FILE, "w") as f:
                json.dump(self.entries, f, indent=4)

            view_window.destroy()
            messagebox.showinfo("Deleted", "Entry deleted successfully!")

    tk.Button(view_window, text="Save Changes", bg="#2ECC71", fg="white", command=save_changes).pack(pady=5)
    tk.Button(view_window, text="Delete Entry", bg="#E74C3C", fg="white", command=delete_entry).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = StreakStepApp(root)
    root.mainloop()
