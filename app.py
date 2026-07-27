import os
import random
import customtkinter as ctk

# Pygame Audio Setup
try:
    import pygame

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    AUDIO_ENABLED = True
except Exception:
    AUDIO_ENABLED = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Minesweeper(ctk.CTk):

    def __init__(self, rows=8, cols=8, mines=10):
        super().__init__()

        self.title("💣S-Minesweeper")
        self.geometry("540x640")
        self.resizable(False, False)

        self.rows = rows
        self.cols = cols
        self.mines_count = mines

        # Audio file exact paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.boom_sound = os.path.join(self.script_dir, "boom.mp3")
        self.click_sound = os.path.join(self.script_dir, "click.mp3")

        self.grid_buttons = {}
        self.board = []
        self.revealed = set()
        self.flags = set()
        self.game_over = False

        # 🔥 ব্যাকগ্রাউন্ড (win_bg) আর মেইন বক্স (board_bg) পুরো আলাদা কালার 🔥
        self.themes = {
            "Red + Yellow": {
                "win_bg": "#1a0000",
                "board_bg": "#4a0000",
                "btn_bg": "#dc2626",
                "btn_hover": "#ef4444",
                "revealed": "#7f1d1d",
                "text": "#facc15",
            },
            "Blue + Green": {
                "win_bg": "#02121e",
                "board_bg": "#032e3a",
                "btn_bg": "#2563eb",
                "btn_hover": "#3b82f6",
                "revealed": "#1e3a8a",
                "text": "#4ade80",
            },
            "Black + Cyan": {
                "win_bg": "#0a0a0a",
                "board_bg": "#18181b",
                "btn_bg": "#0f172a",
                "btn_hover": "#1e293b",
                "revealed": "#020617",
                "text": "#06b6d4",
            },
            "Black + Neo Green": {
                "win_bg": "#000000",
                "board_bg": "#121212",
                "btn_bg": "#1f1f1f",
                "btn_hover": "#2e2e2e",
                "revealed": "#09090b",
                "text": "#22c55e",
            },
            "White + Pastel Pink": {
                "win_bg": "#fdf2f8",
                "board_bg": "#fbcfe8",
                "btn_bg": "#ffffff",
                "btn_hover": "#f472b6",
                "revealed": "#f9a8d4",
                "text": "#831843",
            },
            "Neon Green + Neon Blue": {
                "win_bg": "#020617",
                "board_bg": "#0f172a",
                "btn_bg": "#10b981",
                "btn_hover": "#34d399",
                "revealed": "#1e293b",
                "text": "#38bdf8",
            },
        }
        self.current_theme = self.themes["Black + Neo Green"]

        self.setup_ui()
        self.reset_game()

    def play_sound(self, sound_path):
        if AUDIO_ENABLED and os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.play()
            except Exception as e:
                print("Sound Error:", e)

    def setup_ui(self):
        self.configure(fg_color=self.current_theme["win_bg"])

        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=10, fill="x", padx=20)

        self.status_label = ctk.CTkLabel(
            self.top_frame, text="💣 Mines: 10", font=("Segoe UI", 16, "bold")
        )
        self.status_label.pack(side="left")

        self.theme_option = ctk.CTkOptionMenu(
            self.top_frame,
            values=list(self.themes.keys()),
            command=self.change_theme,
            width=180,
        )
        self.theme_option.pack(side="right", padx=5)

        self.restart_btn = ctk.CTkButton(
            self.top_frame,
            text="🔄 Restart",
            width=80,
            command=self.reset_game,
            fg_color="#3b82f6",
            hover_color="#2563eb",
        )
        self.restart_btn.pack(side="right", padx=5)

        # Main Board Frame (কালার উইন্ডোর সাথে আর মিলবে না)
        self.board_frame = ctk.CTkFrame(
            self,
            fg_color=self.current_theme["board_bg"],
            corner_radius=12,
            border_width=2,
            border_color="#3f3f46",
        )
        self.board_frame.pack(pady=10, padx=20, expand=True)

        self.info_label = ctk.CTkLabel(
            self,
            text="💡 Left Click: Reveal | Right Click: Flag 🚩",
            font=("Segoe UI", 12),
        )
        self.info_label.pack(pady=5)

    def change_theme(self, theme_name):
        self.current_theme = self.themes[theme_name]

        # উইন্ডো আর মেইন বক্সে আলাদা আলাদা কালার সেট হচ্ছে
        self.configure(fg_color=self.current_theme["win_bg"])
        self.board_frame.configure(fg_color=self.current_theme["board_bg"])

        for (r, c), btn in self.grid_buttons.items():
            if (r, c) not in self.revealed:
                btn.configure(
                    fg_color=self.current_theme["btn_bg"],
                    hover_color=self.current_theme["btn_hover"],
                    text_color=self.current_theme["text"],
                )
            else:
                btn.configure(fg_color=self.current_theme["revealed"])

    def reset_game(self):
        self.game_over = False
        self.revealed.clear()
        self.flags.clear()
        self.status_label.configure(text=f"💣 Mines: {self.mines_count}")

        for btn in self.grid_buttons.values():
            btn.destroy()
        self.grid_buttons.clear()

        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        placed_mines = 0
        while placed_mines < self.mines_count:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.board[r][c] != "M":
                self.board[r][c] = "M"
                placed_mines += 1

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == "M":
                    continue
                mines_around = sum(
                    1
                    for nr in range(r - 1, r + 2)
                    for nc in range(c - 1, c + 2)
                    if 0 <= nr < self.rows
                    and 0 <= nc < self.cols
                    and self.board[nr][nc] == "M"
                )
                self.board[r][c] = mines_around

        for r in range(self.rows):
            for c in range(self.cols):
                btn = ctk.CTkButton(
                    self.board_frame,
                    text="",
                    width=44,
                    height=44,
                    corner_radius=6,
                    font=("Segoe UI", 16, "bold"),
                    fg_color=self.current_theme["btn_bg"],
                    hover_color=self.current_theme["btn_hover"],
                    text_color=self.current_theme["text"],
                    command=lambda row=r, col=c: self.left_click(row, col),
                )
                btn.grid(row=r, column=c, padx=3, pady=3)

                btn.bind(
                    "<Button-3>",
                    lambda e, row=r, col=c: self.right_click(row, col),
                )
                self.grid_buttons[(r, c)] = btn

    def left_click(self, r, c):
        if self.game_over or (r, c) in self.flags or (r, c) in self.revealed:
            return

        # 🔊 Click sound
        self.play_sound(self.click_sound)

        # 💥 Hit a mine!
        if self.board[r][c] == "M":
            self.game_over = True
            self.play_sound(self.boom_sound)  # 💣 Blast sound!
            self.status_label.configure(text="💥 GAME OVER!")
            self.reveal_all_mines()
            return

        self.reveal_cell(r, c)

        if len(self.revealed) == (self.rows * self.cols) - self.mines_count:
            self.game_over = True
            self.status_label.configure(text="🎉 YOU WIN!")

    def reveal_cell(self, r, c):
        if (
            (r, c) in self.revealed
            or not (0 <= r < self.rows and 0 <= c < self.cols)
            or (r, c) in self.flags
        ):
            return

        self.revealed.add((r, c))
        btn = self.grid_buttons[(r, c)]
        val = self.board[r][c]

        btn.configure(
            fg_color=self.current_theme["revealed"], state="disabled"
        )

        if val > 0:
            btn.configure(
                text=str(val), text_color_disabled=self.current_theme["text"]
            )
        elif val == 0:
            btn.configure(text="")
            for nr in range(r - 1, r + 2):
                for nc in range(c - 1, c + 2):
                    if (nr, nc) != (r, c):
                        self.reveal_cell(nr, nc)

    def right_click(self, r, c):
        if self.game_over or (r, c) in self.revealed:
            return

        # 🔊 Flag click sound
        self.play_sound(self.click_sound)
        btn = self.grid_buttons[(r, c)]

        if (r, c) in self.flags:
            self.flags.remove((r, c))
            btn.configure(text="", state="normal")
        else:
            self.flags.add((r, c))
            btn.configure(
                text="🚩", text_color_disabled="#ef4444", state="disabled"
            )

        remaining = self.mines_count - len(self.flags)
        self.status_label.configure(text=f"💣 Mines: {remaining}")

    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == "M":
                    btn = self.grid_buttons[(r, c)]
                    btn.configure(
                        text="💣",
                        fg_color="#ef4444",
                        text_color_disabled="#ffffff",
                        state="disabled",
                    )


if __name__ == "__main__":
    app = Minesweeper()
    app.mainloop()