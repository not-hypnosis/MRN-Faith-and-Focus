"""MRN Focus: a small, offline focus timer."""

import ctypes
import os
import random
import sys
import time
import tkinter as tk
from tkinter import ttk


MODES = {
    "Focus": 25 * 60,
    "Short Break": 5 * 60,
    "Long Break": 15 * 60,
}

APP_NAME = "MRN Focus"
APP_VERSION = "1.0.0"
ICON_FILENAME = "mrn_focus.ico"

MESSAGES = (
    ("Well done is better than well said.", "Benjamin Franklin · Poor Richard's Almanack"),
    (
        "Our doubts are traitors, and make us lose the good we oft might win, "
        "by fearing to attempt.",
        "William Shakespeare · Measure for Measure",
    ),
    (
        "If there is no struggle, there is no progress.",
        "Frederick Douglass · 1857 speech",
    ),
    (
        "Go confidently in the direction of your dreams. "
        "Live the life you have imagined.",
        "Henry David Thoreau · Walden",
    ),
    (
        "Nothing in life is to be feared; it is only to be understood.",
        "Marie Curie · 1921 interview",
    ),
    (
        "The journey of a thousand miles begins with a single step.",
        "Laozi · Tao Te Ching, chapter 64",
    ),
    (
        "If I have seen further it is by standing on the shoulders of giants.",
        "Isaac Newton · 1675 letter to Robert Hooke",
    ),
    ("Keep the appointment you made with your own potential.", "Original · Discipline"),
    ("A small routine, kept faithfully, can steady a restless day.", "Original · Discipline"),
    ("Make the next right choice, even when nobody sees it.", "Original · Discipline"),
    ("Let your habits carry you when motivation grows quiet.", "Original · Discipline"),
    ("Begin before you feel ready; refine as you go.", "Original · Discipline"),
    ("The work you repeat becomes the strength you can rely on.", "Original · Discipline"),
    ("Patience is progress that has learned how to breathe.", "Original · Persistence"),
    ("A setback is a page, not the ending.", "Original · Persistence"),
    ("Return to the path; it does not ask how long you were away.", "Original · Persistence"),
    ("Steady effort can reach what hurried effort cannot hold.", "Original · Persistence"),
    ("Rest, gather yourself, and give the difficult thing another honest try.", "Original · Persistence"),
    ("Every attempt leaves you better prepared for the next.", "Original · Persistence"),
    ("You are allowed to grow beyond the version of you that began.", "Original · Confidence"),
    ("Courage can be quiet: it is still courage when your voice shakes.", "Original · Confidence"),
    ("Take up space in the life you are working to build.", "Original · Confidence"),
    ("You have learned hard things before; trust that evidence.", "Original · Confidence"),
    ("Let ambition be an invitation, not a verdict on your worth.", "Original · Confidence"),
    ("Choose the brave next step, not the perfect whole plan.", "Original · Confidence"),
    ("Hope can be practical: it gives tomorrow a place to begin.", "Original · Faith"),
    ("You do not need certainty to take one hopeful step.", "Original · Faith"),
    ("Notice what is good, and let gratitude strengthen your resolve.", "Original · Faith"),
    ("When the way is unclear, trust the strength you have already gathered.", "Original · Faith"),
    ("There is room for doubt and for a steady belief in yourself.", "Original · Faith"),
    ("Let kindness toward yourself be part of your courage.", "Original · Faith"),
    (
        "At the last quiet platform, a green lamp appears for anyone "
        "willing to begin again.",
        "Original · Midnight folklore",
    ),
    (
        "They say the old clock skips a minute whenever someone chooses "
        "to keep going.",
        "Original · Midnight folklore",
    ),
    (
        "A lantern waits at the edge of the map; it brightens with every "
        "step you take.",
        "Original · Midnight folklore",
    ),
    (
        "In the empty library, one blank page is always left open for "
        "the person who has not given up.",
        "Original · Midnight folklore",
    ),
    (
        "The night train has no timetable; it arrives when you decide "
        "your story is not over.",
        "Original · Midnight folklore",
    ),
    (
        "Somewhere in the fog, a bell rings once for every promise "
        "you keep to yourself.",
        "Original · Midnight folklore",
    ),
    (
        "The shadow at your shoulder is only your past, keeping pace "
        "as you move ahead.",
        "Original · Midnight folklore",
    ),
    (
        "A hidden door appears in the familiar wall after you try "
        "one more time.",
        "Original · Midnight folklore",
    ),
)

COLORS = {
    "background": "#101311",
    "surface": "#191E1B",
    "surface_alt": "#222925",
    "border": "#3A463F",
    "green": "#00D084",
    "green_hover": "#A5F04A",
    "text": "#FFFFFF",
    "muted": "#CBD3CD",
    "subtle": "#A8B3AA",
}


class FocusApp:
    def __init__(self, root):
        self.root = root
        self.mode = "Focus"
        self.focus_duration = MODES["Focus"]
        self.remaining = self._duration_for_mode(self.mode)
        self.running = False
        self.deadline = None
        self.tick_id = None
        self.next_message_at = None
        self.message_seconds_left = 300
        self.sessions_completed = 0
        self.last_message = None
        self.closing = False
        self.notification_id = None
        self.progress_animation_id = None
        self.layout_id = None

        self.root.title(APP_NAME)
        self.root.configure(bg=COLORS["background"])
        resource_dir = getattr(
            sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))
        )
        self.root.iconbitmap(os.path.join(resource_dir, ICON_FILENAME))
        self.root.geometry("1280x900")
        self.root.minsize(640, 700)
        if sys.platform == "win32":
            self.root.state("zoomed")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self._configure_styles()
        self._build_ui()
        self._install_shortcut_bindings()
        self.root.bind("<Configure>", self._schedule_layout, add="+")
        self.layout_id = self.root.after(100, self._adapt_layout)
        self._show_random_message()
        self._update_timer_label()

    def _configure_styles(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Duration.TEntry",
            fieldbackground=COLORS["surface_alt"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["surface_alt"],
            darkcolor=COLORS["border"],
            padding=(8, 7),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Duration.TEntry",
            bordercolor=[("focus", COLORS["green"])],
        )
        style.configure(
            "Mode.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            borderwidth=1,
            bordercolor=COLORS["border"],
            padding=(16, 9),
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "Mode.TButton",
            background=[("active", "#303A33")],
            bordercolor=[("active", COLORS["green"])],
            foreground=[("active", COLORS["text"])],
        )
        style.configure(
            "SelectedMode.TButton",
            background=COLORS["green"],
            foreground="#08150F",
            borderwidth=1,
            bordercolor=COLORS["green"],
            padding=(16, 9),
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "SelectedMode.TButton",
            background=[("active", COLORS["green_hover"])],
            bordercolor=[("active", COLORS["green_hover"])],
            foreground=[("active", "#08150F")],
        )
        style.configure(
            "Start.TButton",
            background=COLORS["green"],
            foreground="#08150F",
            borderwidth=0,
            padding=(25, 13),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Start.TButton",
            background=[
                ("active", COLORS["green_hover"]),
                ("disabled", COLORS["border"]),
            ],
            foreground=[("disabled", COLORS["muted"])],
        )
        style.configure(
            "Secondary.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            borderwidth=1,
            bordercolor=COLORS["border"],
            padding=(25, 13),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Secondary.TButton",
            background=[
                ("active", "#303A33"),
                ("disabled", COLORS["surface"]),
            ],
            bordercolor=[("active", COLORS["green"])],
            foreground=[("disabled", COLORS["muted"])],
        )

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        page = tk.Frame(self.root, bg=COLORS["background"], padx=54, pady=34)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)

        header = tk.Frame(page, bg=COLORS["background"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 26))
        header.columnconfigure(0, weight=1, uniform="header_sides")
        header.columnconfigure(2, weight=1, uniform="header_sides")
        brand = tk.Frame(header, bg=COLORS["background"])
        brand.grid(row=0, column=0, sticky="w")
        tk.Label(
            brand,
            text="MRN",
            bg=COLORS["background"],
            fg=COLORS["green"],
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        tk.Label(
            brand,
            text="FOCUS",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", padx=(8, 0), pady=(2, 0))
        self.welcome_label = tk.Label(
            header,
            text="Welcome back, Mrn.",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        self.welcome_label.grid(row=0, column=1, padx=16)
        tk.Label(
            header,
            text="MAKE SPACE FOR WHAT MATTERS",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=2, sticky="e", pady=(3, 0))

        body = tk.Frame(page, bg=COLORS["background"])
        self.body = body
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3, uniform="panels")
        body.columnconfigure(1, weight=2, uniform="panels")
        body.rowconfigure(0, weight=1)

        card = tk.Frame(
            body,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=48,
            pady=34,
        )
        self.timer_card = card
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(5, weight=1)

        tk.Label(
            card,
            text="CURRENT SESSION",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, pady=(0, 18))

        mode_selector = tk.Frame(card, bg=COLORS["surface"])
        mode_selector.grid(row=1, column=0, pady=(0, 8))
        self.mode_buttons = {}
        for mode in MODES:
            button = ttk.Button(
                mode_selector,
                text=mode,
                style="SelectedMode.TButton" if mode == self.mode else "Mode.TButton",
                command=lambda selected=mode: self._change_mode(selected),
            )
            button.pack(side="left", padx=5)
            self.mode_buttons[mode] = button

        duration_controls = tk.Frame(card, bg=COLORS["surface"])
        duration_controls.grid(row=2, column=0, pady=(6, 0))
        tk.Label(
            duration_controls,
            text="Focus length",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 10))
        self.focus_minutes_var = tk.StringVar(value="25")
        self.focus_minutes_entry = ttk.Entry(
            duration_controls,
            textvariable=self.focus_minutes_var,
            width=5,
            justify="center",
            style="Duration.TEntry",
        )
        self.focus_minutes_entry.pack(side="left", padx=(0, 8))
        self.focus_minutes_entry.bind("<Return>", self._apply_focus_duration)
        tk.Label(
            duration_controls,
            text="min",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(0, 10))
        self.apply_duration_button = ttk.Button(
            duration_controls,
            text="Apply",
            style="Secondary.TButton",
            command=self._apply_focus_duration,
        )
        self.apply_duration_button.pack(side="left")
        self.duration_feedback = tk.Label(
            card,
            text="",
            bg=COLORS["surface"],
            fg=COLORS["green_hover"],
            font=("Segoe UI", 9),
        )
        self.duration_feedback.grid(row=3, column=0, pady=(4, 0))

        self.mode_badge = tk.Label(
            card,
            text="FOCUS SESSION  |  25 MIN",
            bg=COLORS["green"],
            fg="#08150F",
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=6,
        )
        self.mode_badge.grid(row=4, column=0, pady=(14, 0))

        self.timer_label = tk.Label(
            card,
            text="25:00",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Segoe UI Light", 150),
        )
        self.timer_label.grid(row=5, column=0, sticky="nsew", pady=(8, 0))

        self.progress_canvas = tk.Canvas(
            card,
            height=20,
            bg=COLORS["surface"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.progress_canvas.grid(row=6, column=0, sticky="ew", padx=54, pady=(4, 18))
        self.progress_canvas.bind("<Configure>", self._draw_progress)
        tk.Label(
            card,
            text="STAY PRESENT. ONE THING AT A TIME.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=7, column=0, pady=(0, 24))

        controls = tk.Frame(card, bg=COLORS["surface"])
        controls.grid(row=8, column=0, pady=(0, 4))
        self.start_button = ttk.Button(
            controls, text="Start", style="Start.TButton", command=self.start
        )
        self.start_button.pack(side="left", padx=7)
        self.pause_button = ttk.Button(
            controls,
            text="Pause",
            style="Secondary.TButton",
            command=self.pause,
            state="disabled",
        )
        self.pause_button.pack(side="left", padx=7)
        ttk.Button(
            controls, text="Reset", style="Secondary.TButton", command=self.reset
        ).pack(side="left", padx=7)

        sidebar = tk.Frame(body, bg=COLORS["background"])
        self.sidebar = sidebar
        sidebar.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(1, weight=1)

        stats = tk.Frame(
            sidebar,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=28,
            pady=24,
        )
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        tk.Label(
            stats,
            text="FOCUS SESSIONS",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        self.session_count_label = tk.Label(
            stats,
            text="0",
            bg=COLORS["surface"],
            fg=COLORS["green_hover"],
            font=("Segoe UI", 66, "bold"),
        )
        self.session_count_label.pack(anchor="w", pady=(4, 0))
        tk.Label(
            stats,
            text="COMPLETED",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        message_box = tk.Frame(
            sidebar,
            bg="#19251E",
            highlightbackground=COLORS["green"],
            highlightthickness=1,
            padx=32,
            pady=30,
        )
        message_box.grid(row=1, column=0, sticky="nsew")
        message_box.columnconfigure(0, weight=1)
        message_box.rowconfigure(1, weight=1)
        tk.Label(
            message_box,
            text="A MOMENT OF PERSPECTIVE",
            bg="#19251E",
            fg=COLORS["green_hover"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, pady=(0, 24))
        self.message_label = tk.Label(
            message_box,
            text="",
            bg="#19251E",
            fg=COLORS["text"],
            font=("Segoe UI", 20),
            wraplength=480,
            justify="center",
        )
        self.message_label.grid(row=1, column=0, sticky="nsew")
        self.attribution_label = tk.Label(
            message_box,
            text="",
            bg="#19251E",
            fg=COLORS["muted"],
            font=("Segoe UI", 11, "bold"),
        )
        self.attribution_label.grid(row=2, column=0, pady=(22, 0))

        self.notification_frame = tk.Frame(
            page,
            bg="#19251E",
            highlightbackground=COLORS["green"],
            highlightthickness=1,
            padx=18,
            pady=11,
        )
        self.notification_frame.columnconfigure(0, weight=1)
        tk.Label(
            self.notification_frame,
            text="SESSION COMPLETE",
            bg="#19251E",
            fg=COLORS["green_hover"],
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self.notification_label = tk.Label(
            self.notification_frame,
            text="",
            bg="#19251E",
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.notification_label.grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.notification_frame.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        self.notification_frame.grid_remove()

    def _install_shortcut_bindings(self):
        self.shortcut_tag = "MRNFocusApplicationKeys"
        self.root.bind_class(self.shortcut_tag, "<KeyPress-space>", self._space_shortcut)
        self.root.bind_class(self.shortcut_tag, "<KeyPress-r>", self._reset_shortcut)
        self.root.bind_class(self.shortcut_tag, "<KeyPress-R>", self._reset_shortcut)

        def add_tag(widget):
            tags = widget.bindtags()
            if self.shortcut_tag not in tags:
                widget.bindtags((self.shortcut_tag,) + tags)
            for child in widget.winfo_children():
                add_tag(child)

        add_tag(self.root)

    def _schedule_layout(self, event):
        if event.widget is not self.root or self.layout_id is not None:
            return
        self.layout_id = self.root.after_idle(self._adapt_layout)

    def _adapt_layout(self):
        self.layout_id = None
        if self.closing:
            return
        card = self.timer_card
        sidebar = self.sidebar
        timer_size = max(
            66,
            min(
                150,
                int(self.root.winfo_height() * 0.145),
                int(card.winfo_width() * 0.2),
            ),
        )
        self.timer_label.configure(font=("Segoe UI Light", timer_size))
        self.message_label.configure(
            wraplength=max(120, min(720, sidebar.winfo_width() - 90))
        )

    def _show_random_message(self):
        choices = tuple(message for message in MESSAGES if message != self.last_message)
        text, source = random.choice(choices or MESSAGES)
        self.last_message = (text, source)
        self.message_label.configure(text=text)
        self.attribution_label.configure(text=source)

    def _duration_for_mode(self, mode):
        return self.focus_duration if mode == "Focus" else MODES[mode]

    def _apply_focus_duration(self, _event=None):
        value = self.focus_minutes_var.get().strip()
        if not value.isdigit() or not 1 <= int(value) <= 180:
            self.duration_feedback.configure(
                text="Enter a whole number from 1 to 180 minutes",
                fg=COLORS["muted"],
            )
            return "break"

        self.focus_duration = int(value) * 60
        self.duration_feedback.configure(text="Focus duration applied", fg=COLORS["green_hover"])
        if self.mode == "Focus":
            self._hide_notification()
            self._stop_tick()
            self._stop_progress_animation()
            self.running = False
            self.deadline = None
            self.next_message_at = None
            self.message_seconds_left = 300
            self.remaining = self.focus_duration
            self.start_button.configure(text="Start", state="normal")
            self.pause_button.configure(state="disabled")
            self.mode_badge.configure(
                text=f"FOCUS SESSION  |  {self.focus_duration // 60} MIN"
            )
            self._update_timer_label()
        return "break"

    def _draw_capsule(self, x0, x1, y0, y1, color):
        canvas = self.progress_canvas
        height = y1 - y0
        width = x1 - x0
        if width <= 0 or height <= 0:
            return
        if width <= height:
            canvas.create_oval(x0, y0, x1, y1, fill=color, outline=color)
            return
        radius = height / 2
        canvas.create_oval(x0, y0, x0 + height, y1, fill=color, outline=color)
        canvas.create_oval(x1 - height, y0, x1, y1, fill=color, outline=color)
        if width > height:
            canvas.create_rectangle(
                x0 + radius,
                y0,
                x1 - radius,
                y1,
                fill=color,
                outline=color,
            )

    def _draw_progress(self, _event=None):
        if not hasattr(self, "progress_canvas"):
            return
        canvas = self.progress_canvas
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        inset = 1
        x0, x1 = inset, max(inset, width - inset)
        y0, y1 = 2, max(2, height - 2)
        if x1 <= x0 or y1 <= y0:
            return

        self._draw_capsule(x0, x1, y0, y1, COLORS["surface_alt"])
        duration = self._duration_for_mode(self.mode)
        if self.running and self.deadline is not None:
            left = max(0.0, self.deadline - time.monotonic())
            fraction = 1.0 - left / duration
        else:
            fraction = (duration - self.remaining) / duration
        fraction = min(1.0, max(0.0, fraction))
        fill_end = x0 + (x1 - x0) * fraction
        if fill_end > x0:
            self._draw_capsule(x0, fill_end, y0, y1, COLORS["green"])

    def _animate_progress(self):
        self.progress_animation_id = None
        if not self.running or self.closing:
            return
        self._draw_progress()
        self.progress_animation_id = self.root.after(30, self._animate_progress)

    def _stop_progress_animation(self):
        if self.progress_animation_id is not None:
            self.root.after_cancel(self.progress_animation_id)
            self.progress_animation_id = None

    def _update_timer_label(self):
        minutes, seconds = divmod(self.remaining, 60)
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        self._draw_progress()

    def _change_mode(self, mode):
        if mode not in MODES:
            return
        self._hide_notification()
        self._stop_tick()
        self._stop_progress_animation()
        self.running = False
        self.mode = mode
        self.remaining = self._duration_for_mode(self.mode)
        self.mode_badge.configure(
            text=f"{self.mode.upper()} SESSION  |  {self.remaining // 60} MIN"
        )
        for selected_mode, button in self.mode_buttons.items():
            button.configure(
                style="SelectedMode.TButton" if selected_mode == self.mode else "Mode.TButton"
            )
        self.deadline = None
        self.message_seconds_left = 300
        self.next_message_at = None
        self.start_button.configure(text="Start", state="normal")
        self.pause_button.configure(state="disabled")
        if self.mode == "Focus":
            self._show_random_message()
        else:
            self.message_label.configure(text="Rest is part of the rhythm.")
            self.attribution_label.configure(text="Take a moment to recharge")
        self._update_timer_label()

    def start(self):
        if self.running or self.remaining <= 0:
            return
        self.running = True
        self.deadline = time.monotonic() + self.remaining
        self.start_button.configure(text="Running", state="disabled")
        self.pause_button.configure(state="normal")
        if self.mode == "Focus":
            self.next_message_at = time.monotonic() + self.message_seconds_left
        self._animate_progress()
        self._tick()

    def pause(self):
        if not self.running:
            return
        now = time.monotonic()
        self.remaining = max(0, int(self.deadline - now + 0.999))
        if self.remaining == 0:
            self._stop_tick()
            self._stop_progress_animation()
            self._finish()
            return
        if self.mode == "Focus" and self.next_message_at is not None:
            self.message_seconds_left = max(0, self.next_message_at - now)
        self.running = False
        self.deadline = None
        self.next_message_at = None
        self._stop_tick()
        self._stop_progress_animation()
        self.start_button.configure(text="Resume", state="normal")
        self.pause_button.configure(state="disabled")
        self._update_timer_label()

    def reset(self):
        self._hide_notification()
        self._stop_tick()
        self._stop_progress_animation()
        self.running = False
        self.deadline = None
        self.next_message_at = None
        self.message_seconds_left = 300
        self.remaining = self._duration_for_mode(self.mode)
        self.mode_badge.configure(
            text=f"{self.mode.upper()} SESSION  |  {self.remaining // 60} MIN"
        )
        self.start_button.configure(text="Start", state="normal")
        self.pause_button.configure(state="disabled")
        if self.mode == "Focus":
            self._show_random_message()
        self._update_timer_label()

    def _tick(self):
        self.tick_id = None
        if not self.running or self.closing:
            return

        now = time.monotonic()
        self.remaining = max(0, int(self.deadline - now + 0.999))
        self._update_timer_label()

        if self.mode == "Focus" and self.next_message_at is not None:
            while now >= self.next_message_at:
                self._show_random_message()
                self.next_message_at += 300
                self.message_seconds_left = 300

        if self.remaining == 0:
            self._stop_progress_animation()
            self._finish()
        else:
            self.tick_id = self.root.after(200, self._tick)

    def _finish(self):
        finished_mode = self.mode
        self.running = False
        self.deadline = None
        self.next_message_at = None
        self.remaining = 0
        self._update_timer_label()
        self.start_button.configure(text="Start", state="normal")
        self.pause_button.configure(state="disabled")

        if finished_mode == "Focus":
            self.sessions_completed += 1
            self.session_count_label.configure(text=str(self.sessions_completed))

        self.root.bell()
        self._show_notification(
            f"{finished_mode} session complete. Take a moment before you continue."
        )

    def _show_notification(self, text):
        self._hide_notification()
        self.notification_label.configure(text=text)
        self.notification_frame.grid()
        self.notification_id = self.root.after(6000, self._expire_notification)

    def _expire_notification(self):
        self.notification_id = None
        self.notification_frame.grid_remove()

    def _hide_notification(self):
        if self.notification_id is not None:
            self.root.after_cancel(self.notification_id)
            self.notification_id = None
        self.notification_frame.grid_remove()

    def _space_shortcut(self, event):
        if isinstance(
            event.widget,
            (tk.Entry, tk.Text, tk.Spinbox, ttk.Entry, ttk.Spinbox, ttk.Combobox),
        ):
            return
        if self.running:
            self.pause()
        else:
            self.start()
        return "break"

    def _reset_shortcut(self, event):
        if isinstance(
            event.widget,
            (tk.Entry, tk.Text, tk.Spinbox, ttk.Entry, ttk.Spinbox, ttk.Combobox),
        ):
            return
        self.reset()
        return "break"

    def _stop_tick(self):
        if self.tick_id is not None:
            self.root.after_cancel(self.tick_id)
            self.tick_id = None

    def close(self):
        self.closing = True
        self._stop_tick()
        self._stop_progress_animation()
        if self.layout_id is not None:
            self.root.after_cancel(self.layout_id)
            self.layout_id = None
        if self.notification_id is not None:
            self.root.after_cancel(self.notification_id)
            self.notification_id = None
        self.root.destroy()


def main():
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass
    root = tk.Tk()
    FocusApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()