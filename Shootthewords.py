import os
import random
import subprocess
import threading
import tkinter as tk
from tkinter import font

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

GUN_STYLES = [
    {"name": "AK47", "color": "#FF6F61"},
    {"name": "Mac10", "color": "#6B5B95"},
    {"name": "Kacstoner", "color": "#88B04B"},
    {"name": "Titan", "color": "#FFA500"},
    {"name": "Viper", "color": "#00A5CF"},
    {"name": "Raptor", "color": "#F7CAC9"},
    {"name": "Blaze", "color": "#92A8D1"},
    {"name": "Comet", "color": "#955251"},
    {"name": "Phantom", "color": "#B565A7"},
    {"name": "Shadow", "color": "#009B77"},
]

GUN_OPTION_NAMES = ["AK47", "AWP", "Rifle"]

WORDS = [
    {"word": "potato", "parts": ["po", "ta", "to"]},
    {"word": "banana", "parts": ["ba", "na", "na"]},
    {"word": "tomato", "parts": ["to", "ma", "to"]},
    {"word": "rainbow", "parts": ["rain", "bow"]},
    {"word": "butterfly", "parts": ["but", "ter", "fly"]},
    {"word": "sunflower", "parts": ["sun", "flow", "er"]},
    {"word": "icecream", "parts": ["ice", "cream"]},
    {"word": "elephant", "parts": ["el", "e", "phant"]},
    {"word": "dinosaur", "parts": ["di", "no", "saur"]},
    {"word": "pineapple", "parts": ["pine", "ap", "ple"]},
    {"word": "cupcake", "parts": ["cup", "cake"]},
    {"word": "jellybean", "parts": ["jel", "ly", "bean"]},
    {"word": "backpack", "parts": ["back", "pack"]},
    {"word": "playground", "parts": ["play", "ground"]},
    {"word": "firetruck", "parts": ["fire", "truck"]},
    {"word": "moonlight", "parts": ["moon", "light"]},
    {"word": "spaceship", "parts": ["space", "ship"]},
    {"word": "notebook", "parts": ["note", "book"]},
    {"word": "toothbrush", "parts": ["tooth", "brush"]},
    {"word": "sandwich", "parts": ["sand", "wich"]},
    {"word": "chocolate", "parts": ["choc", "o", "late"]},
    {"word": "kangaroo", "parts": ["kan", "ga", "roo"]},
    {"word": "honeybee", "parts": ["hon", "ey", "bee"]},
    {"word": "ladybug", "parts": ["la", "dy", "bug"]},
    {"word": "raincoat", "parts": ["rain", "coat"]},
    {"word": "fireplace", "parts": ["fire", "place"]},
    {"word": "mountain", "parts": ["moun", "tain"]},
    {"word": "snowflake", "parts": ["snow", "flake"]},
    {"word": "skateboard", "parts": ["skate", "board"]},
    {"word": "pajamas", "parts": ["pa", "ja", "mas"]},
    {"word": "marshmallow", "parts": ["marsh", "mal", "low"]},
    {"word": "carousel", "parts": ["car", "ou", "sel"]},
    {"word": "honeycomb", "parts": ["hon", "ey", "comb"]},
    {"word": "dragonfly", "parts": ["drag", "on", "fly"]},
    {"word": "whisper", "parts": ["whi", "sper"]},
    {"word": "rainforest", "parts": ["rain", "forest"]},
    {"word": "storybook", "parts": ["sto", "ry", "book"]},
    {"word": "headphone", "parts": ["head", "phone"]},
    {"word": "rainstorm", "parts": ["rain", "storm"]},
    {"word": "lightning", "parts": ["light", "ning"]},
    {"word": "hammock", "parts": ["ham", "mock"]},
    {"word": "dolphin", "parts": ["dol", "phin"]},
    {"word": "balloon", "parts": ["bal", "loon"]},
    {"word": "snowman", "parts": ["snow", "man"]},
    {"word": "firefly", "parts": ["fire", "fly"]},
    {"word": "penguin", "parts": ["pen", "guin"]},
    {"word": "watermelon", "parts": ["wa", "ter", "me", "lon"]},
    {"word": "seashell", "parts": ["sea", "shell"]},
    {"word": "toothpaste", "parts": ["tooth", "paste"]},
    {"word": "mailbox", "parts": ["mail", "box"]},
    {"word": "blueberry", "parts": ["blue", "ber", "ry"]},
    {"word": "sunshine", "parts": ["sun", "shine"]},
    {"word": "playtime", "parts": ["play", "time"]},
    {"word": "footprint", "parts": ["foot", "print"]},
]

class ShootTheWords:
    def __init__(self, root):
        self.root = root
        self.root.title("Shoot the Words")
        self.root.geometry("820x540")
        self.root.resizable(False, False)

        self.header_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.large_font = font.Font(family="Helvetica", size=18)
        self.button_font = font.Font(family="Helvetica", size=14)
        self.small_font = font.Font(family="Helvetica", size=12)

        self.sound_enabled = True
        self.engine = None
        self.speech_process = None
        self.create_speech_engine()
        self.use_powershell = self.has_powershell_speech()

        self.previous_round = []
        self.current_round = []
        self.current_word = None
        self.chosen_parts = []
        self.syllable_buttons = []
        self.gun_images = self.make_gun_images()
        self.bg_image = self.make_background_image()

        self.build_layout()
        self.reset_round(initial=True)
        self.show_selection_screen()
        self.speak("Welcome to Shoot the Words. Tap a gun to hear the hidden word.")

    def create_speech_engine(self):
        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 150)
                self.engine.setProperty("volume", 1.0)
            except Exception:
                self.engine = None
        else:
            self.engine = None

    def has_powershell_speech(self):
        if os.name != "nt":
            return False
        try:
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Add-Type -AssemblyName System.speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('test');",
                ],
                capture_output=True,
                timeout=10,
            )
            return True
        except Exception:
            return False

    def make_gun_images(self):
        loaded = self.load_gun_image_files()
        if loaded:
            return loaded

        images = []
        for style in GUN_STYLES:
            img = tk.PhotoImage(width=160, height=80)
            for x in range(160):
                for y in range(80):
                    img.put(style["color"], (x, y))
            for x in range(10, 130):
                for y in range(32, 40):
                    img.put("#2C3E50", (x, y))
            for x in range(40, 120):
                for y in range(22, 32):
                    img.put("#4D5656", (x, y))
            for x in range(48, 112):
                for y in range(40, 52):
                    img.put("#4D5656", (x, y))
            for x in range(100, 150):
                for y in range(34, 52):
                    img.put("#2C3E50", (x, y))
            for x in range(72, 82):
                for y in range(42, 64):
                    img.put("#2C3E50", (x, y))
            for x in range(130, 142):
                for y in range(30, 38):
                    img.put("#F7DC6F", (x, y))
            for x in range(132, 145):
                for y in range(27, 31):
                    img.put("#F5B041", (x, y))
            images.append(img)
        return images

    def load_gun_image_files(self):
        # If you add real PNGs into a guns/ folder next to this script,
        # they will be loaded automatically and used instead of the drawn icons.
        asset_dir = os.path.join(os.path.dirname(__file__), "guns")
        if not os.path.isdir(asset_dir):
            return []

        desired_base = ["AK-47.png", "AWP.png"]
        files = [f for f in sorted(os.listdir(asset_dir)) if f.lower().endswith((".png", ".gif", ".ppm", ".pgm", ".webp"))]
        ordered_files = []
        for name in desired_base:
            if name in files:
                ordered_files.append(name)
        for f in files:
            if f not in ordered_files:
                ordered_files.append(f)
        ordered_files = ordered_files[:3]

        images = []
        for filename in ordered_files:
            path = os.path.join(asset_dir, filename)
            if Image is not None and ImageTk is not None:
                try:
                    pil_img = Image.open(path).convert("RGBA")
                    pil_img = pil_img.resize((160, 80), Image.LANCZOS)
                    images.append(ImageTk.PhotoImage(pil_img))
                    continue
                except Exception:
                    pass
            try:
                images.append(tk.PhotoImage(file=path))
            except Exception:
                continue
        return images

    def make_background_image(self):
        bg = tk.PhotoImage(width=820, height=540)
        for x in range(820):
            for y in range(540):
                blue = int(35 + (x / 820) * 30)
                red = int(50 + (y / 540) * 70)
                green = int(40 + (x / 820) * 30)
                bg.put(f"#{red:02x}{green:02x}{blue:02x}", (x, y))
        for cx, cy, radius, color in [(180, 120, 80, "#F7DC6F"), (620, 110, 65, "#E74C3C"), (440, 260, 95, "#F5B041")]:
            for x in range(cx - radius, cx + radius):
                for y in range(cy - radius, cy + radius):
                    if 0 <= x < 820 and 0 <= y < 540 and (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                        bg.put(color, (x, y))
        for x in range(0, 820, 20):
            for y in range(420, 540, 15):
                if (x + y) % 30 == 0:
                    for dx in range(5):
                        for dy in range(3):
                            if 0 <= x + dx < 820 and 0 <= y + dy < 540:
                                bg.put("#A6ACAF", (x + dx, y + dy))
        for x in range(60, 760, 110):
            for y in range(100, 420, 80):
                for dx in range(-10, 11):
                    for dy in range(-10, 11):
                        if 0 <= x + dx < 820 and 0 <= y + dy < 540 and dx*dx + dy*dy <= 100:
                            bg.put("#2C3E50", (x + dx, y + dy))
        return bg

    def build_layout(self):
        self.root.configure(bg="#17202A")
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        self.title_label = tk.Label(
            self.root,
            text="Shoot the Words",
            font=self.header_font,
            fg="#F8F9F9",
            bg="#17202A",
            pady=10,
        )
        self.title_label.pack(pady=(8, 0))

        self.selection_frame = tk.Frame(self.root, bg="#17202A")
        self.word_frame = tk.Frame(self.root, bg="#17202A")

        self.selection_message = tk.Label(
            self.selection_frame,
            text="Pick a gun to reveal a hidden word.",
            font=self.large_font,
            fg="#F8F9F9",
            bg="#17202A",
        )
        self.selection_message.pack(pady=(10, 16))

        self.guns_frame = tk.Frame(self.selection_frame, bg="#17202A")
        self.guns_frame.pack()

        self.gun_image_labels = []
        self.gun_buttons = []
        for index in range(3):
            option_frame = tk.Frame(self.guns_frame, bg="#1B2631", bd=3, relief="ridge")
            option_frame.grid(row=0, column=index, padx=12, pady=4, sticky="n")

            image_label = tk.Label(option_frame, bg="#1B2631")
            image_label.pack(padx=6, pady=(6, 2))
            image_label.bind("<Button-1>", lambda event, i=index: self.on_gun_click(i))
            self.gun_image_labels.append(image_label)

            button = tk.Button(
                option_frame,
                text="Select",
                font=self.button_font,
                width=18,
                height=1,
                bd=4,
                relief="raised",
                command=lambda i=index: self.on_gun_click(i),
            )
            button.pack(padx=6, pady=(0, 8))
            self.gun_buttons.append(button)

        self.word_label = tk.Label(
            self.word_frame,
            text="",
            font=self.header_font,
            fg="#F8F9F9",
            bg="#17202A",
            wraplength=760,
            justify="center",
        )
        self.word_label.pack(pady=(12, 8))

        self.instructions_label = tk.Label(
            self.word_frame,
            text="Tap the syllables in the right order to build the word.",
            font=self.small_font,
            fg="#F8F9F9",
            bg="#17202A",
        )
        self.instructions_label.pack(pady=(0, 10))

        self.answer_label = tk.Label(
            self.word_frame,
            text="Answer: ",
            font=self.large_font,
            fg="#F8F9F9",
            bg="#17202A",
            wraplength=760,
            justify="center",
        )
        self.answer_label.pack(pady=(0, 12))

        self.syllables_frame = tk.Frame(self.word_frame)
        self.syllables_frame.pack(pady=(0, 10))

        self.feedback_label = tk.Label(
            self.word_frame,
            text="",
            font=self.large_font,
            fg="#F8F9F9",
            bg="#17202A",
            wraplength=760,
            justify="center",
        )
        self.feedback_label.pack(pady=(4, 10))

        self.controls_frame = tk.Frame(self.root, bg="#17202A")
        self.controls_frame.pack(side="bottom", pady=12)

        self.reset_button = tk.Button(
            self.controls_frame,
            text="Reset",
            font=self.button_font,
            width=10,
            bg="#F7DC6F",
            command=self.reset_selection,
            state="disabled",
        )
        self.reset_button.grid(row=0, column=0, padx=8)

        self.next_button = tk.Button(
            self.controls_frame,
            text="Next",
            font=self.button_font,
            width=10,
            bg="#D5D8DC",
            command=self.on_next,
            state="disabled",
        )
        self.next_button.grid(row=0, column=1, padx=8)

        self.repeat_button = tk.Button(
            self.controls_frame,
            text="Repeat",
            font=self.button_font,
            width=10,
            bg="#AED6F1",
            command=self.on_repeat,
            state="disabled",
        )
        self.repeat_button.grid(row=0, column=2, padx=8)

        self.sound_button = tk.Button(
            self.controls_frame,
            text="Sound: On",
            font=self.button_font,
            width=12,
            bg="#2ECC71",
            fg="white",
            command=self.toggle_sound,
        )
        self.sound_button.grid(row=0, column=3, padx=8)

    def reset_round(self, initial=False, previous_selected=None):
        if initial or not self.previous_round:
            self.current_round = random.sample(WORDS, 3)
        else:
            remaining = [w for w in WORDS if w not in self.previous_round]
            if not remaining:
                remaining = WORDS[:]
            new_word = random.choice(remaining)
            candidates = [w for w in self.previous_round if w is not previous_selected]
            keep_count = min(2, len(candidates))
            kept = random.sample(candidates, keep_count) if keep_count else []
            while len(kept) < 3:
                choice = random.choice(WORDS)
                if choice not in kept and choice not in self.previous_round:
                    kept.append(choice)
            self.current_round = kept
        self.previous_round = self.current_round[:]
        self.current_word = None
        self.chosen_parts = []
        self.selected_order = []
        self.feedback_label.config(text="")
        self.answer_label.config(text="Answer: ")
        self.reset_button.config(state="disabled")
        self.repeat_button.config(state="disabled")
        self.next_button.config(state="disabled")

    def show_selection_screen(self):
        self.word_frame.pack_forget()
        self.gun_images = self.load_gun_image_files() or self.make_gun_images()
        self.selection_frame.pack(padx=24, pady=(0, 24))
        for index, gun_button in enumerate(self.gun_buttons):
            style = GUN_STYLES[index % len(GUN_STYLES)]
            image_label = self.gun_image_labels[index]
            if self.gun_images:
                image = self.gun_images[index % len(self.gun_images)]
                image_label.config(image=image, width=160, height=80)
                image_label.image = image
                gun_button.config(text="Select", bg=style["color"], activebackground=style["color"], fg="white")
            else:
                image_label.config(image="", width=160, height=80, bg=style["color"])
                gun_button.config(text="Select", bg=style["color"], activebackground=style["color"], fg="white")
            gun_button.config(relief="raised")
        self.title_label.config(text="Shoot the Words")
        self.selection_message.config(text="Pick a gun to find a hidden word.")

    def on_gun_click(self, index):
        self.current_word = self.current_round[index]
        self.current_word_index = index
        self.selection_frame.pack_forget()
        self.show_word_screen()
        self.speak(f"{self.current_word['word']}")

    def show_word_screen(self):
        self.title_label.config(text="Build the word from syllables")
        self.word_label.config(text=self.current_word["word"].title())
        self.instructions_label.config(text="Build the word by tapping the syllables below.")
        self.answer_label.config(text="Answer: ")
        self.feedback_label.config(text="")
        self.reset_button.config(state="normal")
        self.repeat_button.config(state="normal")
        self.next_button.config(state="disabled")
        self.stop_speech()
        self.speak(f"The word is {self.current_word['word']}. Tap the syllables in order.")
        self.chosen_parts = []
        self.syllables_frame.destroy()
        self.syllables_frame = tk.Frame(self.word_frame)
        self.syllables_frame.pack(pady=(0, 10))
        parts = self.current_word["parts"][:]
        random.shuffle(parts)
        self.syllable_buttons = []
        for part in parts:
            button = tk.Button(
                self.syllables_frame,
                text=part,
                font=self.button_font,
                width=10,
                height=2,
                bg="#85C1E9",
                fg="#1B2631",
                relief="raised",
                activebackground="#5499C7",
                command=lambda p=part, b=part: self.on_part_click(p),
            )
            button.pack(side="left", padx=8, pady=6)
            self.syllable_buttons.append(button)
        self.word_frame.pack(padx=24, pady=(0, 24))

    def on_part_click(self, part):
        if not self.current_word:
            return
        expected_part = self.current_word["parts"][len(self.chosen_parts)]
        if part == expected_part:
            self.chosen_parts.append(part)
            self.answer_label.config(text="Answer: " + " ".join(self.chosen_parts))
            self.update_button_states(part, correct=True)
            if len(self.chosen_parts) == len(self.current_word["parts"]):
                self.feedback_label.config(text="Great job! You built the word correctly.")
                self.speak("Great job! You built the word correctly.")
                self.next_button.config(state="normal", bg="#58D68D")
                self.disable_remaining_buttons()
        else:
            self.feedback_label.config(
                text="Oops! That is not the right next part. Press Reset to try again.",
                fg="#C0392B",
            )
            self.speak("Oops, try again. Press reset and try again.")
            self.disable_remaining_buttons()

    def update_button_states(self, part, correct):
        for button in self.syllable_buttons:
            if button["text"] == part and button["state"] == "normal":
                button.config(bg="#ABEBC6" if correct else "#F5B7B1", state="disabled")
                break

    def disable_remaining_buttons(self):
        for button in self.syllable_buttons:
            if button["state"] == "normal":
                button.config(state="disabled")

    def reset_selection(self):
        if not self.current_word:
            return
        self.stop_speech()
        self.show_word_screen()
        self.feedback_label.config(text="Try tapping the syllables in the correct order.", fg="#F8F9F9")

    def on_repeat(self):
        if self.current_word:
            self.stop_speech()
            self.feedback_label.config(text="Repeating the word...", fg="#F8F9F9")
            self.speak(self.current_word["word"])
        else:
            self.speak("Pick a gun to begin.")

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.sound_button.config(text="Sound: On", bg="#27AE60")
            self.speak("Sound is on.")
        else:
            self.sound_button.config(text="Sound: Off", bg="#E74C3C")

    def on_next(self):
        self.stop_speech()
        self.reset_round(initial=False, previous_selected=self.current_word)
        self.show_selection_screen()
        self.speak("Great work! Here are three new words. Pick another gun.")

    def stop_speech(self):
        if self.engine is not None:
            try:
                self.engine.stop()
            except Exception:
                pass
        if self.speech_process is not None:
            try:
                self.speech_process.terminate()
                self.speech_process = None
            except Exception:
                pass

    def speak(self, text):
        if not self.sound_enabled:
            return
        if self.use_powershell:
            self._speak_powershell(text)
            return
        if self.engine is not None:
            try:
                self.stop_speech()
                def worker():
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception:
                        if self.use_powershell:
                            self._speak_powershell(text)
                threading.Thread(target=worker, daemon=True).start()
                return
            except Exception:
                self.engine = None
        if self.use_powershell:
            self._speak_powershell(text)

    def _speak_powershell(self, text):
        self.stop_speech()
        escaped_text = text.replace('"', '""')
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Add-Type -AssemblyName System.speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak(\"{escaped_text}\");",
        ]
        try:
            self.speech_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            self.speech_process = None


if __name__ == "__main__":
    root = tk.Tk()
    ShootTheWords(root)
    root.mainloop()
