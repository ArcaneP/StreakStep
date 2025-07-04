# === ADDITIONAL FEATURE FOR VICTORIES/SETBACKS ===
from tkinter import messagebox
import tkinter as tk
import json
import os
from datetime import datetime, timedelta
import webbrowser
import requests
import certifi

JOURNAL_FILE = "journal_entries.json"
SAVE_FILE = "streakstep_data.json"
DEBUG_MODE = False
SHOW_FULL_TIMER_DEBUG = False  # Toggle full/simple timer at launch

class StreakStepApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StreakStep - Day Timer Tracker")
        self.root.geometry("320x250")
        self.root.configure(bg="#2C3E50")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.full_timer_mode = SHOW_FULL_TIMER_DEBUG
        self.congrats_shown = False

        self.data = self.load_data()

        # API TESTING 

        def get_current_time_from_api():
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(
                    "https://worldtimeapi.org/api/ip",
                    headers=headers,
                    timeout=5,
                    verify=certifi.where()
                )
                if response.status_code == 200:
                    data = response.json()
                    return datetime.fromisoformat(data["datetime"])
                else:
                    print("Error fetching time:", response.status_code)
            except Exception as e:
                print("Error:", e)
            return datetime.now()

        print(get_current_time_from_api())

        #END API

        # === UI ===
        self.debug_label = tk.Label(root, text="", font=("Helvetica", 10), bg="#2C3E50", fg="#95A5A6")
        self.debug_label.pack(pady=(5, 0))

        self.motivation_label = tk.Label(root, text="You can do it!", font=("Helvetica", 16, "bold"), fg="#ECF0F1", bg="#2C3E50")
        self.motivation_label.pack(pady=(5, 5))

        self.timer_label = tk.Label(root, text="", font=("Helvetica", 22), fg="#FFFFFF", bg="#2C3E50")
        self.timer_label.pack(pady=5)

        #DESCRIPTION IDEA
        description = tk.Text(root, height=1, width=30)
        
        # description.pack()

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
        self.save_data()

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

        journal_window.geometry("260x300")
        journal_window.configure(bg="#34495E")
        journal_window.resizable(False, False)

        label = tk.Label(journal_window, text="My Entry", font=("Helvetica", 12), fg="white", bg="#34495E")
        label.pack(pady=10)

        entry_title = tk.Entry(journal_window, font=("Helvetica", 10))
        entry_title.pack(pady=5)
        entry_title.insert(0, "Title")
        self.description = tk.Text(journal_window, height=5, width=30)
        self.description.pack()

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

        desc = self.description.get("1.0", "end").strip()
        entry = {
            "title": title.strip(),
            "type": entry_type,
            "description": desc,
            "timestamp": datetime.now().isoformat()
        }
        print(entry)

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

        # Close old entries window if open
        if hasattr(self, 'entries_window') and self.entries_window.winfo_exists():
            self.entries_window.destroy()

        if not os.path.exists(JOURNAL_FILE):
            return

        with open(JOURNAL_FILE, "r") as f:
             entries = json.load(f)

        self.entries_window = tk.Toplevel(self.root)
        self.entries_window.title("Your Journal Entries")
        self.entries_window.geometry("320x400")
        self.entries_window.configure(bg="#1C2833")

          # === Scrollable Frame Setup ===
        canvas = tk.Canvas(self.entries_window, bg="#1C2833", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.entries_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#1C2833")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === Add Entry Buttons ===
        for entry in entries:
            color = "#2ECC71" if entry["type"] == "victory" else "#E74C3C"

            frame = tk.Frame(scroll_frame, bg="#1C2833")
            frame.pack(fill="x", padx=10, pady=3)

            tk.Label(frame, text="✦", font=("Helvetica", 14), fg=color, bg="#1C2833").pack(side="left")

            entry_btn = tk.Button(
                frame,
                text=entry["title"],
                font=("Helvetica", 10),
                fg="white",
                bg="#1C2833",
                bd=0,
                activebackground="#34495E",
                anchor="w",
                command=lambda e=entry: self.open_entry_view(e)
            )
            entry_btn.pack(side="left", padx=8, fill="x", expand=True)

    def open_entry_view(self, entry):
        view_window = tk.Toplevel(self.root)
        view_window.title(f"View Entry: {entry['title']}")
        view_window.geometry("350x550")
        view_window.configure(bg="#34495E")

        # Display Title
        tk.Label(view_window, text="Title:", bg="#34495E", fg="white", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        tk.Label(view_window, text=entry["title"], bg="#34495E", fg="white").pack(anchor="w", padx=10, pady=(0,10))

        # Display Type
        tk.Label(view_window, text="Type:", bg="#34495E", fg="white", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
        tk.Label(view_window, text=entry["type"], bg="#34495E", fg="white").pack(anchor="w", padx=10, pady=(0,10))

        # Display Description
        tk.Label(view_window, text="Description:", bg="#34495E", fg="white", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
        desc_text = tk.Text(view_window, width=40, height=16, bg="#2C3E50", fg="white", relief="flat")
        desc_text.insert("1.0", entry.get("description", ""))
        desc_text.config(state="disabled")  # make read-only
        desc_text.pack(padx=10, pady=(0,10))

        def delete_entry():
            if not os.path.exists(JOURNAL_FILE):
                return

            with open(JOURNAL_FILE, "r") as f:
                entries = json.load(f)
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
            if confirm:
                entries.remove(entry)
            with open(JOURNAL_FILE, "w") as f:
                json.dump(entries, f, indent=2)
            messagebox.showinfo("Deleted", "Entry deleted successfully!")
            view_window.destroy()
            self.show_journal_entries()

        delete_btn = tk.Button(view_window, text="Delete Entry", bg="#E74C3C", fg="white", command=delete_entry)
        delete_btn.pack(pady=10)

        edit_btn = tk.Button(view_window, text="Edit Entry", bg="#3498DB", fg="white",
                     command=lambda: self.open_entry_edit(entry, view_window))
        edit_btn.pack(pady=5)

    def open_entry_edit(self, entry, view_window):
        view_window.destroy()  # Close the view window

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Journal Entry")
        edit_window.geometry("300x300")

        tk.Label(edit_window, text="Title:").pack()
        title_entry = tk.Entry(edit_window)
        title_entry.insert(0, entry["title"])
        title_entry.pack()

        tk.Label(edit_window, text="Type:").pack()
        type_var = tk.StringVar(value=entry["type"])
        type_menu = tk.OptionMenu(edit_window, type_var, "victory", "setback")
        type_menu.pack()

        tk.Label(edit_window, text="Description:").pack()
        desc_entry = tk.Text(edit_window, height=5, wrap="word")
        desc_entry.insert("1.0", entry["description"])
        desc_entry.pack()

        def save_changes():
            if not os.path.exists(JOURNAL_FILE):
                return

            with open(JOURNAL_FILE, "r") as f:
                entries = json.load(f)

            # Update the entry by matching the timestamp
            for i, e in enumerate(entries):
                if e["timestamp"] == entry["timestamp"]:
                    entries[i]["title"] = title_entry.get().strip()
                    entries[i]["type"] = type_var.get()
                    entries[i]["description"] = desc_entry.get("1.0", "end-1c").strip()
                    break

            with open(JOURNAL_FILE, "w") as f:
                json.dump(entries, f, indent=2)

            messagebox.showinfo("Saved", "Entry updated successfully!")
            edit_window.destroy()
            self.show_journal_entries()

        save_btn = tk.Button(edit_window, text="Save Changes", bg="#2ECC71", fg="white", command=save_changes)
        save_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = StreakStepApp(root)
    root.mainloop()
