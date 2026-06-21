
import customtkinter as ctk
import tkinter as tk
import time
import threading
import random
import os
import math
from PIL import Image, ImageTk
from ctypes import windll
from collections import deque
import heapq

# --- DISPLAY DPI FIX ---
try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

COLORS = {
    "bg_black": "#030305",
    "neon_cyan": "#00D1FF",
    "neon_purple": "#8B5CF6",
    "card_dark": "#1A1C23", 
    "sidebar_dark": "#08090E",
    "text_white": "#FFFFFF",
    "dim_gray": "#71717A",
    "gold": "#FFD700",
    "space_bg": "#000B29",
    "tetris_grid": "#0F111A"
}

class GamingArenaPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.attributes('-fullscreen', True)
        self.configure(fg_color=COLORS["bg_black"])
        
        self.won_count = 0
        self.lost_count = 0
        self.draw_count = 0
        self.game_images_cache = []
        
        self.games_data = [
            {"name": "SNAKE AI", "img": "snake.png", "tag": "Strategy / AI", "command": self.open_snake_dashboard},
            {"name": "SPACE SHOOTER", "img": "space.png", "tag": "Action / Physics", "command": self.open_space_shooter},
            {"name": "ROCK PAPER SCISSOR", "img": "rps.png", "tag": "Pattern Recognition", "command": self.open_rps_selection},
            {"name": "TETRIS", "img": "tetris.png", "tag": "Puzzle / Logic", "command": self.open_tetris}
        ]
        
        self.launch_splash()

    def get_highest_score(self, mode, algo="Manual"):
        if mode == "AI":
            if algo == "DFS": return 100
            if algo == "A*": return 140
            if algo == "BFS": return 80
            if algo == "Dijkstra": return 150
            
        filename = f"highest_{mode}_{algo}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try: return int(f.read().strip())
                except: return 0
        return 0

    def save_highest_score(self, score, mode, algo="Manual"):
        current_hs = self.get_highest_score(mode, algo)
        if score > current_hs:
            filename = f"highest_{mode}_{algo}.txt"
            with open(filename, "w") as f:
                f.write(str(score))
            if hasattr(self, 'highest_score_label'):
                self.highest_score_label.configure(text=f"Highest Score: {score}")

    def launch_splash(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_black"], corner_radius=0)
        self.splash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.canvas = tk.Canvas(self.splash_frame, bg=COLORS["bg_black"], highlightthickness=0, width=sw, height=sh)
        self.canvas.pack()

        def draw_circuit(coords, color):
            self.canvas.create_line(coords, fill=color, width=3, capstyle="round")

        draw_circuit([0, sh*0.1, sw*0.2, sh*0.1, sw*0.3, sh*0.4, 0, sh*0.4], COLORS["neon_cyan"])
        draw_circuit([0, sh*0.8, sw*0.15, sh*0.8, sw*0.2, sh], COLORS["neon_cyan"])
        draw_circuit([sw, sh*0.2, sw*0.7, sh*0.2, sw*0.6, 0], COLORS["neon_purple"])
        draw_circuit([sw, sh*0.6, sw*0.8, sh*0.6, sw*0.75, sh], COLORS["neon_purple"])

        self.logo = ctk.CTkLabel(self.splash_frame, text="🎮", font=("Arial", 120))
        self.logo.place(relx=0.5, rely=0.45, anchor="center")
        self.title_txt = ctk.CTkLabel(self.splash_frame, text="AI ADAPTIVE ARENA", font=("Impact", 70), text_color="white")
        self.title_txt.place(relx=0.5, rely=0.68, anchor="center")

        self.progress = ctk.CTkProgressBar(self.splash_frame, width=600, height=15, progress_color=COLORS["neon_purple"])
        self.progress.set(0)
        self.progress.place(relx=0.5, rely=0.85, anchor="center")
        threading.Thread(target=self.loading_process, daemon=True).start()

    def loading_process(self):
        for i in range(1, 101):
            time.sleep(0.01)
            self.progress.set(i/100)
        self.after(0, self.show_main_dashboard)

    def show_main_dashboard(self):
        self.splash_frame.destroy()
        self.main_dashboard()

    def scroll_to_games(self):
        self.main_view._parent_canvas.yview_moveto(0.4)

    def sidebar_home(self):
        if hasattr(self, 'store_frame'): self.store_frame.destroy()
        self.search_var.set("")
        self.display_games(self.games_data)
        self.main_view._parent_canvas.yview_moveto(0)

    def sidebar_store(self):
        # Changed Logic: No more maintenance message. Displays a mini-store view.
        self.store_frame = ctk.CTkFrame(self.main_view, fg_color=COLORS["card_dark"], corner_radius=20)
        self.store_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        ctk.CTkLabel(self.store_frame, text="🔥 TRENDING IN STORE", font=("Impact", 45), text_color=COLORS["neon_cyan"]).pack(pady=(50, 20))
        
        items = [
            ("CYBER RACER", "Coming Soon", COLORS["neon_purple"]),
            ("VOID RUNNER", "Limited Edition", COLORS["neon_cyan"]),
            ("PIXEL QUEST", "New Release", COLORS["gold"])
        ]
        
        for name, tag, clr in items:
            f = ctk.CTkFrame(self.store_frame, fg_color=COLORS["bg_black"], height=100, corner_radius=15)
            f.pack(fill="x", padx=100, pady=10)
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=name, font=("Arial", 22, "bold")).pack(side="left", padx=30)
            ctk.CTkLabel(f, text=tag, font=("Arial", 14), text_color=clr).pack(side="right", padx=30)

        ctk.CTkButton(self.store_frame, text="Close Store", fg_color="transparent", border_width=2, border_color=COLORS["dim_gray"], command=self.sidebar_home).pack(pady=40)

    def sidebar_library(self):
        installed = [g["name"] for g in self.games_data]
        tk.messagebox.showinfo("Your Library", f"Installed Games:\n• " + "\n• ".join(installed))

    def main_dashboard(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=0); self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.side = ctk.CTkFrame(self.main_container, width=220, fg_color=COLORS["sidebar_dark"], corner_radius=0)
        self.side.grid(row=0, column=0, sticky="nsew")
        self.side.grid_propagate(False)
        ctk.CTkLabel(self.side, text="GamesMode", font=("Arial", 28, "bold"), text_color=COLORS["neon_cyan"]).pack(pady=(40, 30))
        
        ctk.CTkButton(self.side, text="🏠  Home", anchor="w", fg_color="transparent", font=("Arial", 16), height=45, command=self.sidebar_home).pack(fill="x", padx=15, pady=2)
        ctk.CTkButton(self.side, text="🔥  Store", anchor="w", fg_color="transparent", font=("Arial", 16), height=45, command=self.sidebar_store).pack(fill="x", padx=15, pady=2)
        ctk.CTkButton(self.side, text="📚  Library", anchor="w", fg_color="transparent", font=("Arial", 16), height=45, command=self.sidebar_library).pack(fill="x", padx=15, pady=2)
        
        ctk.CTkButton(self.side, text="🚪  Exit Arena", fg_color="#B91C1C", corner_radius=8, font=("Arial", 14, "bold"), command=self.quit).pack(side="bottom", fill="x", padx=20, pady=30)

        self.content_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew")

        self.top_bar = ctk.CTkFrame(self.content_container, fg_color="transparent", height=60)
        self.top_bar.pack(fill="x", padx=40, pady=(20, 0))
        
        self.search_container = ctk.CTkFrame(self.top_bar, fg_color=COLORS["card_dark"], corner_radius=12, width=350, height=40)
        self.search_container.pack(side="right")
        self.search_container.pack_propagate(False)
        
        ctk.CTkLabel(self.search_container, text="🔍", font=("Arial", 14), text_color=COLORS["dim_gray"]).pack(side="left", padx=12)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_games())
        self.search_entry = ctk.CTkEntry(self.search_container, width=250, textvariable=self.search_var, fg_color="transparent", border_width=0, text_color="white", placeholder_text="Search...")
        self.search_entry.pack(side="left", padx=0, fill="both", expand=True)

        self.main_view = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.main_view.pack(fill="both", expand=True, padx=40, pady=10)

        self.hero_banner = ctk.CTkFrame(self.main_view, height=420, fg_color=COLORS["card_dark"], corner_radius=25)
        self.hero_banner.pack(fill="x", pady=(0, 30))
        self.hero_banner.pack_propagate(False)
        
        try:
            self.banner_img = ctk.CTkImage(Image.open("banner.png"), size=(1150, 420))
            ctk.CTkLabel(self.hero_banner, image=self.banner_img, text="").place(x=0, y=0)
        except: pass
        
        ctk.CTkButton(self.hero_banner, text="Play Now →", fg_color="#3B82F6", width=160, height=45, corner_radius=10, font=("Arial", 16, "bold"), command=self.scroll_to_games).place(x=55, y=320)
        
        self.grid_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.grid_frame.pack(fill="x", expand=True)
        self.display_games(self.games_data)

    def filter_games(self):
        query = self.search_var.get().lower()
        filtered = [g for g in self.games_data if query in g["name"].lower()]
        self.display_games(filtered)

    def display_games(self, games_list):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.game_images_cache = []
        
        for game in games_list:
            card = ctk.CTkFrame(self.grid_frame, width=240, height=380, fg_color="transparent")
            card.pack(side="left", padx=(0, 25))
            img_box = ctk.CTkFrame(card, width=240, height=300, fg_color=COLORS["card_dark"], corner_radius=15)
            img_box.pack(fill="x")
            img_box.pack_propagate(False)
            try:
                g_img = ctk.CTkImage(Image.open(game["img"]), size=(240, 300))
                self.game_images_cache.append(g_img)
                ctk.CTkButton(img_box, image=g_img, text="", fg_color="transparent", command=game["command"]).pack(expand=True, fill="both")
            except:
                ctk.CTkButton(img_box, text="🎮", font=("Arial", 60), fg_color="transparent", command=game["command"]).pack(expand=True, fill="both")
            
            ctk.CTkLabel(card, text=game["name"], font=("Arial", 17, "bold")).pack(anchor="w", pady=(12, 0))
            ctk.CTkLabel(card, text=game["tag"], font=("Arial", 13), text_color=COLORS["dim_gray"]).pack(anchor="w")

    # --- THE REST OF THE GAME LOGIC REMAINS IDENTICAL ---
    def open_snake_dashboard(self):
        self.main_container.pack_forget()
        self.snake_hub = ctk.CTkFrame(self, fg_color=COLORS["bg_black"])
        self.snake_hub.pack(fill="both", expand=True)
        self.control_panel = ctk.CTkFrame(self.snake_hub, width=320, fg_color=COLORS["sidebar_dark"], corner_radius=0)
        self.control_panel.pack(side="left", fill="y")
        ctk.CTkButton(self.control_panel, text="← Back to Arena", fg_color="transparent", command=self.close_snake).pack(pady=20)
        ctk.CTkLabel(self.control_panel, text="SNAKE PRO", font=("Impact", 40), text_color=COLORS["neon_cyan"]).pack()
        self.game_mode = tk.StringVar(value="AI")
        ctk.CTkSegmentedButton(self.control_panel, values=["Manual", "AI"], variable=self.game_mode, command=self.handle_mode_change).pack(pady=10, padx=20)
        self.algo_var = tk.StringVar(value="A*")
        self.algo_menu = ctk.CTkOptionMenu(self.control_panel, values=["BFS", "DFS", "Dijkstra", "A*"], variable=self.algo_var, command=self.handle_mode_change)
        self.algo_menu.pack(pady=10)
        self.score_var = tk.IntVar(value=0)
        ctk.CTkLabel(self.control_panel, text="CURRENT SCORE", font=("Arial", 12), text_color="gray").pack(pady=(20,0))
        ctk.CTkLabel(self.control_panel, textvariable=self.score_var, font=("Arial", 50, "bold")).pack()
        self.highest_score_label = ctk.CTkLabel(self.control_panel, text="Highest Score: 0", font=("Arial", 22, "bold"), text_color=COLORS["gold"])
        self.highest_score_label.pack(pady=20)
        self.cols, self.rows = 40, 25
        self.game_canvas = tk.Canvas(self.snake_hub, bg="#000000", highlightthickness=0, borderwidth=0)
        self.game_canvas.pack(side="right", fill="both", expand=True)
        self.after(100, self.load_snake_background)
        self.running = False
        self.handle_mode_change()
        self.bind_all("<KeyPress>", self.handle_keys)

    def load_snake_background(self):
        try:
            cw, ch = self.game_canvas.winfo_width(), self.game_canvas.winfo_height()
            if cw > 1 and os.path.exists("snake_bg.png"):
                bg_img = Image.open("snake_bg.png").resize((cw, ch))
                self.tk_bg_img = ImageTk.PhotoImage(bg_img)
                self.game_canvas.create_image(0, 0, image=self.tk_bg_img, anchor="nw", tags="bg")
        except: pass

    def handle_mode_change(self, *args):
        self.running = False
        self.after(50, self.initiate_restart)

    def initiate_restart(self):
        mode = self.game_mode.get()
        algo = self.algo_var.get() if mode == "AI" else "Manual"
        self.reset_game_vars()
        highest = self.get_highest_score(mode, algo)
        self.highest_score_label.configure(text=f"Highest Score: {highest}")
        self.algo_menu.configure(state="disabled" if mode == "Manual" else "normal")
        self.running = True
        self.start_loop()

    def reset_game_vars(self):
        self.snake_pos = [(10, 10), (9, 10), (8, 10)]
        self.food_pos = (random.randint(0, self.cols-1), random.randint(0, self.rows-1))
        self.direction = (1, 0)
        self.score_var.set(0)

    def close_snake(self):
        self.running = False
        self.snake_hub.destroy()
        self.main_container.pack(fill="both", expand=True)

    def handle_keys(self, e):
        if self.game_mode.get() == "Manual":
            if e.keysym == "Up" and self.direction != (0, 1): self.direction = (0, -1)
            elif e.keysym == "Down" and self.direction != (0, -1): self.direction = (0, 1)
            elif e.keysym == "Left" and self.direction != (1, 0): self.direction = (-1, 0)
            elif e.keysym == "Right" and self.direction != (-1, 0): self.direction = (1, 0)

    def get_ai_path(self, algo):
        start, target, body = self.snake_pos[0], self.food_pos, set(self.snake_pos)
        def neighbors(p):
            res = []
            dirs = [(0,-1),(0,1),(-1,0),(1,0)]
            if algo == "DFS": random.shuffle(dirs)
            for dx, dy in dirs:
                nxt = ((p[0]+dx)%self.cols, (p[1]+dy)%self.rows)
                if nxt not in body: res.append((nxt, (dx, dy)))
            return res
        if algo == "BFS":
            q = deque([(start, [])]); v = {start}
            while q:
                curr, path = q.popleft()
                if curr == target: return path
                for nxt, mv in neighbors(curr):
                    if nxt not in v: v.add(nxt); q.append((nxt, path+[mv]))
        elif algo == "DFS":
            stack = [(start, [])]; v = {start}
            while stack:
                curr, path = stack.pop()
                if curr == target: return path
                if len(path) > 450: continue
                for nxt, mv in neighbors(curr):
                    if nxt not in v: v.add(nxt); stack.append((nxt, path+[mv]))
        elif algo in ["Dijkstra", "A*"]:
            pq = [(0, start, [])]; costs = {start: 0}
            while pq:
                d, curr, path = heapq.heappop(pq)
                if curr == target: return path
                for nxt, mv in neighbors(curr):
                    new_cost = d + 1
                    if nxt not in costs or new_cost < costs[nxt]:
                        costs[nxt] = new_cost
                        priority = new_cost + (abs(nxt[0]-target[0]) + abs(nxt[1]-target[1]) if algo=="A*" else 0)
                        heapq.heappush(pq, (priority, nxt, path+[mv]))
        return None

    def start_loop(self):
        if not self.running: return
        mode = self.game_mode.get()
        algo = self.algo_var.get() if mode == "AI" else "Manual"
        if mode == "AI":
            path = self.get_ai_path(algo)
            if path: self.direction = path[0]
        new_head = ((self.snake_pos[0][0] + self.direction[0]) % self.cols, 
                    (self.snake_pos[0][1] + self.direction[1]) % self.rows)
        if new_head in self.snake_pos:
            self.save_highest_score(self.score_var.get(), mode, algo)
            self.running = False
        else:
            self.snake_pos.insert(0, new_head)
            if new_head == self.food_pos:
                new_score = self.score_var.get() + 10
                self.score_var.set(new_score)
                self.food_pos = (random.randint(0, self.cols-1), random.randint(0, self.rows-1))
                limit = {"BFS": 80, "DFS": 100, "A*": 140, "Dijkstra": 150}.get(algo, 9999)
                if new_score >= limit:
                    self.save_highest_score(new_score, mode, algo)
                    self.running = False
            else:
                self.snake_pos.pop()
        cw, ch = self.game_canvas.winfo_width(), self.game_canvas.winfo_height()
        if cw > 1:
            self.game_canvas.delete("game_obj")
            w_step, h_step = cw/self.cols, ch/self.rows
            fx, fy = self.food_pos
            self.game_canvas.create_oval(fx*w_step+4, fy*h_step+4, (fx+1)*w_step-4, (fy+1)*h_step-4, fill="#FF0000", outline="white", tags="game_obj")
            for i, (sx, sy) in enumerate(self.snake_pos):
                clr = COLORS["neon_cyan"] if i == 0 else COLORS["neon_purple"]
                self.game_canvas.create_rectangle(sx*w_step, sy*h_step, (sx+1)*w_step, (sy+1)*h_step, fill=clr, outline="", tags="game_obj")
        self.after(30 if mode == "AI" else 80, self.start_loop)

    def open_space_shooter(self):
        self.main_container.pack_forget()
        self.space_hub = ctk.CTkFrame(self, fg_color=COLORS["space_bg"])
        self.space_hub.pack(fill="both", expand=True)
        self.space_side = ctk.CTkFrame(self.space_hub, width=280, fg_color=COLORS["sidebar_dark"], corner_radius=0)
        self.space_side.pack(side="left", fill="y")
        ctk.CTkButton(self.space_side, text="← Exit Game", fg_color="transparent", command=self.close_space).pack(pady=30)
        ctk.CTkLabel(self.space_side, text="SPACE\nSHOOTER", font=("Impact", 45), text_color=COLORS["neon_purple"]).pack(pady=20)
        self.space_score = tk.IntVar(value=0)
        ctk.CTkLabel(self.space_side, text="SCORE", font=("Arial", 14), text_color="gray").pack()
        ctk.CTkLabel(self.space_side, textvariable=self.space_score, font=("Arial", 50, "bold"), text_color="white").pack()
        self.space_canvas = tk.Canvas(self.space_hub, bg=COLORS["space_bg"], highlightthickness=0)
        self.space_canvas.pack(side="right", fill="both", expand=True)
        try:
            self.p_img = ImageTk.PhotoImage(Image.open("player.png").resize((70, 70)))
            self.e_img = ImageTk.PhotoImage(Image.open("enemy.png").resize((60, 60)))
            self.s_bg_img = None 
        except:
            self.p_img = None
            self.e_img = None
            self.s_bg_img = None
        self.player_x = 400
        self.bullets = []
        self.enemies = []
        self.space_running = True
        self.bind_all("<Left>", lambda e: self.move_player(-40))
        self.bind_all("<Right>", lambda e: self.move_player(40))
        self.bind_all("<space>", lambda e: self.shoot())
        self.space_loop()

    def move_player(self, dx):
        cw = self.space_canvas.winfo_width()
        if cw > 1: self.player_x = max(50, min(cw-50, self.player_x + dx))

    def shoot(self):
        ch = self.space_canvas.winfo_height()
        if ch > 1: self.bullets.append([self.player_x, ch-100])

    def space_loop(self):
        if not self.space_running: return
        cw, ch = self.space_canvas.winfo_width(), self.space_canvas.winfo_height()
        if cw < 2: self.after(100, self.space_loop); return
        self.space_canvas.delete("sp")
        try:
            if os.path.exists("space_bg.png") and self.s_bg_img is None:
                bg_img = Image.open("space_bg.png").resize((cw, ch))
                self.s_bg_img = ImageTk.PhotoImage(bg_img)
            if self.s_bg_img: self.space_canvas.create_image(0, 0, image=self.s_bg_img, anchor="nw", tags="sp")
        except: pass
        if not os.path.exists("space_bg.png"):
            for _ in range(3): 
                rx, ry = random.randint(0,cw), random.randint(0,ch)
                self.space_canvas.create_oval(rx, ry, rx+2, ry+2, fill="white", outline="", tags="sp")
        if self.p_img: self.space_canvas.create_image(self.player_x, ch-70, image=self.p_img, tags="sp")
        else: self.space_canvas.create_polygon(self.player_x, ch-80, self.player_x-25, ch-30, self.player_x+25, ch-30, fill=COLORS["neon_cyan"], tags="sp")
        for b in self.bullets[:]:
            b[1] -= 20
            self.space_canvas.create_line(b[0], b[1], b[0], b[1]+15, fill="#00FFCC", width=3, tags="sp")
            if b[1] < 0: self.bullets.remove(b)
        if random.random() < 0.04: self.enemies.append([random.randint(50, cw-50), -50])
        for e in self.enemies[:]:
            e[1] += 6
            if self.e_img: self.space_canvas.create_image(e[0], e[1], image=self.e_img, tags="sp")
            else: self.space_canvas.create_oval(e[0]-25, e[1]-25, e[0]+25, e[1]+25, fill="#FF4655", tags="sp")
            for b in self.bullets[:]:
                if math.hypot(b[0]-e[0], b[1]-e[1]) < 35:
                    self.space_score.set(self.space_score.get() + 10)
                    if e in self.enemies: self.enemies.remove(e)
                    if b in self.bullets: self.bullets.remove(b)
            if e[1] > ch: self.space_running = False 
        if self.space_running: self.after(25, self.space_loop)
        else: self.space_canvas.create_text(cw/2, ch/2, text="MISSION FAILED", font=("Impact", 80), fill="#FF4655", tags="sp")

    def close_space(self):
        self.space_running = False
        self.space_hub.destroy()
        self.main_container.pack(fill="both", expand=True)

    def open_rps_selection(self):
        self.main_container.pack_forget()
        if hasattr(self, 'rps_hub'): self.rps_hub.destroy()
        self.rps_hub = ctk.CTkFrame(self, fg_color=COLORS["bg_black"])
        self.rps_hub.pack(fill="both", expand=True)
        cp = ctk.CTkFrame(self.rps_hub, width=280, fg_color=COLORS["sidebar_dark"], corner_radius=0)
        cp.pack(side="left", fill="y")
        ctk.CTkButton(cp, text="← Back to Arena", fg_color="transparent", command=self.close_rps).pack(pady=30)
        ctk.CTkLabel(cp, text="BATTLE\nMODE", font=("Impact", 45), text_color=COLORS["neon_cyan"]).pack(pady=20)
        ctk.CTkLabel(cp, text=f"SESSION STATS", font=("Arial", 14, "bold"), text_color="gray").pack(side="bottom", pady=(0, 10))
        ctk.CTkLabel(cp, text=f"W: {self.won_count} | L: {self.lost_count}", font=("Arial", 20, "bold"), text_color=COLORS["gold"]).pack(side="bottom", pady=20)
        self.rps_content = ctk.CTkFrame(self.rps_hub, fg_color="transparent")
        self.rps_content.pack(side="right", fill="both", expand=True)
        ctk.CTkLabel(self.rps_content, text="CHOOSE YOUR WEAPON", font=("Impact", 55), text_color=COLORS["text_white"]).pack(pady=(60, 40))
        btn_container = ctk.CTkFrame(self.rps_content, fg_color="transparent")
        btn_container.pack(expand=True)
        weapons = [("Rock", "rock.png"), ("Paper", "paper.png"), ("Scissor", "scissor.png")]
        self.rps_imgs = []
        for name, img_file in weapons:
            f = ctk.CTkFrame(btn_container, fg_color="transparent")
            f.pack(side="left", padx=30)
            try:
                w_img = ctk.CTkImage(Image.open(img_file), size=(150, 150))
                self.rps_imgs.append(w_img)
                btn = ctk.CTkButton(f, image=w_img, text="", width=180, height=180, fg_color=COLORS["card_dark"], hover_color="#2A2D35", corner_radius=20, command=lambda w=name: self.show_rps_result(w))
            except:
                btn = ctk.CTkButton(f, text=name[0], width=180, height=180, font=("Arial", 80), fg_color=COLORS["card_dark"], command=lambda w=name: self.show_rps_result(w))
            btn.pack()
            ctk.CTkLabel(f, text=name.upper(), font=("Arial", 16, "bold"), text_color="white").pack(pady=15)

    def show_rps_result(self, user_choice):
        for widget in self.rps_content.winfo_children(): widget.destroy()
        cpu_choice = random.choice(["Rock", "Paper", "Scissor"])
        img_map = {"Rock": "rock.png", "Paper": "paper.png", "Scissor": "scissor.png"}
        if user_choice == cpu_choice: msg = "IT'S A DRAW! 🤝"; self.draw_count += 1; status_color="white"
        elif (user_choice=="Rock" and cpu_choice=="Scissor") or (user_choice=="Paper" and cpu_choice=="Rock") or (user_choice=="Scissor" and cpu_choice=="Paper"):
            msg = "YOU WON! 🎉"; self.won_count += 1; status_color=COLORS["neon_cyan"]
        else: msg = "YOU LOST! 💀"; self.lost_count += 1; status_color=COLORS["dim_gray"]
        ctk.CTkLabel(self.rps_content, text="PLAYER v/s COMPUTER", font=("Impact", 45), text_color="gray").pack(pady=(40, 20))
        battle_frame = ctk.CTkFrame(self.rps_content, fg_color="transparent")
        battle_frame.pack(pady=20)
        p_box = ctk.CTkFrame(battle_frame, fg_color=COLORS["card_dark"], width=220, height=220, corner_radius=20)
        p_box.pack(side="left", padx=40); p_box.pack_propagate(False)
        try:
            p_img = ctk.CTkImage(Image.open(img_map[user_choice]), size=(160, 160))
            self.rps_imgs.append(p_img)
            ctk.CTkLabel(p_box, image=p_img, text="").pack(expand=True)
        except: ctk.CTkLabel(p_box, text=user_choice).pack(expand=True)
        ctk.CTkLabel(battle_frame, text="VS", font=("Impact", 40), text_color=COLORS["neon_purple"]).pack(side="left")
        c_box = ctk.CTkFrame(battle_frame, fg_color=COLORS["card_dark"], width=220, height=220, corner_radius=20)
        c_box.pack(side="left", padx=40); c_box.pack_propagate(False)
        try:
            c_img = ctk.CTkImage(Image.open(img_map[cpu_choice]), size=(160, 160))
            self.rps_imgs.append(c_img)
            ctk.CTkLabel(c_box, image=c_img, text="").pack(expand=True)
        except: ctk.CTkLabel(c_box, text=cpu_choice).pack(expand=True)
        ctk.CTkLabel(self.rps_content, text=msg, font=("Arial", 38, "bold"), text_color=status_color).pack(pady=30)
        ctk.CTkButton(self.rps_content, text="🔄 Play Again", font=("Arial", 18, "bold"), fg_color="transparent", border_width=2, border_color=COLORS["neon_cyan"], width=200, height=50, command=self.open_rps_selection).pack(pady=10)
        stats_frame = ctk.CTkFrame(self.rps_content, fg_color=COLORS["sidebar_dark"], height=80, corner_radius=15)
        stats_frame.pack(side="bottom", fill="x", padx=100, pady=40)
        f_s = ("Arial", 20, "bold")
        ctk.CTkLabel(stats_frame, text=f"WON: {self.won_count}", font=f_s, text_color=COLORS["neon_cyan"]).pack(side="left", expand=True)
        ctk.CTkLabel(stats_frame, text=f"LOST: {self.lost_count}", font=f_s, text_color=COLORS["dim_gray"]).pack(side="left", expand=True)
        ctk.CTkLabel(stats_frame, text=f"DRAW: {self.draw_count}", font=f_s, text_color="white").pack(side="left", expand=True)

    def close_rps(self):
        self.rps_hub.destroy()
        self.main_container.pack(fill="both", expand=True)

    def open_tetris(self):
        self.main_container.pack_forget()
        self.tetris_hub = ctk.CTkFrame(self, fg_color=COLORS["bg_black"])
        self.tetris_hub.pack(fill="both", expand=True)
        self.tetris_bg_canvas = tk.Canvas(self.tetris_hub, bg=COLORS["bg_black"], highlightthickness=0)
        self.tetris_bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        try:
            bg_path = "tetris_bg.png"
            if os.path.exists(bg_path):
                self.update_idletasks()
                sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
                raw_img = Image.open(bg_path).resize((sw, sh), Image.Resampling.LANCZOS)
                self.tetris_tk_bg = ImageTk.PhotoImage(raw_img)
                self.tetris_bg_canvas.create_image(0, 0, image=self.tetris_tk_bg, anchor="nw")
        except: pass
        self.tetris_side = ctk.CTkFrame(self.tetris_hub, width=280, fg_color=COLORS["sidebar_dark"], corner_radius=0)
        self.tetris_side.place(relx=0, rely=0, relheight=1)
        ctk.CTkButton(self.tetris_side, text="← Exit Game", fg_color="transparent", command=self.close_tetris).pack(pady=30)
        ctk.CTkLabel(self.tetris_side, text="TETRIS\nRETRO", font=("Impact", 45), text_color=COLORS["neon_cyan"]).pack(pady=20)
        self.tetris_score = tk.IntVar(value=0)
        ctk.CTkLabel(self.tetris_side, text="SCORE", font=("Arial", 14), text_color="gray").pack()
        ctk.CTkLabel(self.tetris_side, textvariable=self.tetris_score, font=("Arial", 50, "bold"), text_color="white").pack()
        self.game_container = ctk.CTkFrame(self.tetris_hub, fg_color="transparent")
        self.game_container.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)
        self.t_cols, self.t_rows = 10, 20
        self.cell_size = 35
        self.tetris_canvas = tk.Canvas(self.game_container, bg=COLORS["tetris_grid"], highlightthickness=1, highlightbackground=COLORS["neon_purple"], width=self.t_cols*self.cell_size, height=self.t_rows*self.cell_size)
        self.tetris_canvas.place(relx=0.45, rely=0.5, anchor="center")
        self.next_panel = ctk.CTkFrame(self.game_container, width=200, height=300, fg_color=COLORS["card_dark"], corner_radius=15)
        self.next_panel.place(relx=0.75, rely=0.4, anchor="center")
        ctk.CTkLabel(self.next_panel, text="NEXT SHAPE", font=("Arial", 16, "bold"), text_color=COLORS["neon_purple"]).pack(pady=10)
        self.next_canvas = tk.Canvas(self.next_panel, bg=COLORS["card_dark"], highlightthickness=0, width=120, height=120)
        self.next_canvas.pack(pady=10)
        self.shapes = [[[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]], [[1, 1, 0], [0, 1, 1]], [[0, 1, 1], [1, 1, 0]], [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]]]
        self.shape_colors = ["#00f0f0", "#f0f000", "#a000f0", "#00f000", "#f00000", "#0000f0", "#f0a000"]
        self.grid = [[0 for _ in range(self.t_cols)] for _ in range(self.t_rows)]
        self.next_piece_idx = random.randint(0, len(self.shapes)-1)
        self.tetris_running = True
        self.bind_all("<Left>", lambda e: self.move_piece(-1, 0))
        self.bind_all("<Right>", lambda e: self.move_piece(1, 0))
        self.bind_all("<Down>", lambda e: self.move_piece(0, 1))
        self.bind_all("<Up>", lambda e: self.rotate_piece())
        self.spawn_piece()
        self.tetris_loop()

    def spawn_piece(self):
        idx = self.next_piece_idx
        self.current_piece = {'shape': self.shapes[idx], 'color': self.shape_colors[idx], 'x': self.t_cols // 2 - len(self.shapes[idx][0]) // 2, 'y': 0}
        self.next_piece_idx = random.randint(0, len(self.shapes)-1)
        self.draw_next_shape()
        if self.check_collision(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape']): self.tetris_running = False

    def draw_next_shape(self):
        self.next_canvas.delete("all")
        shape = self.shapes[self.next_piece_idx]
        color = self.shape_colors[self.next_piece_idx]
        s = 25
        ox, oy = (120-len(shape[0])*s)/2, (120-len(shape)*s)/2
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val: self.next_canvas.create_rectangle(ox+c*s, oy+r*s, ox+(c+1)*s, oy+(r+1)*s, fill=color, outline="white")

    def check_collision(self, x, y, shape):
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    if x+c < 0 or x+c >= self.t_cols or y+r >= self.t_rows or self.grid[y+r][x+c]: return True
        return False

    def move_piece(self, dx, dy):
        if not self.tetris_running: return
        if not self.check_collision(self.current_piece['x']+dx, self.current_piece['y']+dy, self.current_piece['shape']):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
            self.draw_tetris()
            return True
        elif dy > 0:
            self.lock_piece()
            self.spawn_piece()
        return False

    def rotate_piece(self):
        s = self.current_piece['shape']
        new_s = [[s[y][x] for y in range(len(s)-1, -1, -1)] for x in range(len(s[0]))]
        if not self.check_collision(self.current_piece['x'], self.current_piece['y'], new_s):
            self.current_piece['shape'] = new_s
            self.draw_tetris()

    def lock_piece(self):
        for r, row in enumerate(self.current_piece['shape']):
            for c, val in enumerate(row):
                if val: self.grid[self.current_piece['y']+r][self.current_piece['x']+c] = self.current_piece['color']
        self.clear_lines()

    def clear_lines(self):
        lines = 0
        for r in range(self.t_rows):
            if all(self.grid[r]):
                del self.grid[r]
                self.grid.insert(0, [0 for _ in range(self.t_cols)])
                lines += 1
        if lines: self.tetris_score.set(self.tetris_score.get() + (lines * 100))

    def draw_tetris(self):
        self.tetris_canvas.delete("all")
        for r, row in enumerate(self.grid):
            for c, val in enumerate(row):
                if val: self.tetris_canvas.create_rectangle(c*self.cell_size, r*self.cell_size, (c+1)*self.cell_size, (r+1)*self.cell_size, fill=val, outline="#222")
        for r, row in enumerate(self.current_piece['shape']):
            for c, val in enumerate(row):
                if val:
                    x, y = (self.current_piece['x']+c)*self.cell_size, (self.current_piece['y']+r)*self.cell_size
                    self.tetris_canvas.create_rectangle(x, y, x+self.cell_size, y+self.cell_size, fill=self.current_piece['color'], outline="white")

    def tetris_loop(self):
        if not self.tetris_running:
            self.tetris_canvas.create_text(self.t_cols*self.cell_size/2, self.t_rows*self.cell_size/2, text="GAME OVER", font=("Impact", 40), fill="red")
            return
        self.move_piece(0, 1)
        self.after(500, self.tetris_loop)

    def close_tetris(self):
        self.tetris_running = False
        self.tetris_hub.destroy()
        self.main_container.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = GamingArenaPro()
    app.mainloop()