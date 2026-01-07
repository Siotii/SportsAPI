import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import io


def fetch_team_data(team_name):
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('teams', [])
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return []

def fetch_players(team_id):
    url = f"https://www.thesportsdb.com/api/v1/json/3/lookup_all_players.php?id={team_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('player', [])[:5]  
    except requests.RequestException as e:
        print(f"Error fetching players: {e}")
        return []


def load_image_from_url(url, size=(80, 80)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = Image.open(io.BytesIO(response.content))
        image_data = image_data.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image_data)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def display_team_info(team):
    global player_images 
    player_images = []  
    
    info = f"🏆 Team: {team.get('strTeam', 'N/A')}\n\n"
    info += f"🏟️ League: {team.get('strLeague', 'N/A')}\n\n"
    info += f"🏟️ Stadium: {team.get('strStadium', 'N/A')}\n\n"
    info += f"📖 Description: {team.get('strDescriptionEN', 'N/A')[:500]}..."
    
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, info)
    

    team_id = team.get('idTeam')
    if team_id:
        players = fetch_players(team_id)    
        for widget in players_frame.winfo_children():
            widget.destroy()
        
        if players:
            for player in players:
                player_frame = tk.Frame(players_frame, bg="#F3F4F6", bd=1, relief="solid")
                player_frame.pack(side="left", padx=5, pady=5, fill="y")
                
                
                thumb_url = player.get('strThumb')
                if thumb_url:
                    player_img = load_image_from_url(thumb_url)
                    if player_img:
                        player_images.append(player_img)  
                        img_label = tk.Label(player_frame, image=player_img, bg="#F3F4F6")
                        img_label.pack()
                    else:
                        tk.Label(player_frame, text="No Photo", font=("Roboto", 8), bg="#F3F4F6", fg="#1E3A8A").pack()
                else:
                    tk.Label(player_frame, text="No Photo", font=("Roboto", 8), bg="#F3F4F6", fg="#1E3A8A").pack()
                
                
                name_label = tk.Label(player_frame, text=player.get('strPlayer', 'N/A'), font=("Roboto", 9, "bold"), bg="#F3F4F6", fg="#1E3A8A", wraplength=80)
                name_label.pack(pady=2)
        else:
            tk.Label(players_frame, text="No players found.", font=("Roboto", 10), bg="#F3F4F6", fg="#1E3A8A").pack()
    else:
        tk.Label(players_frame, text="No team ID available for players.", font=("Roboto", 10), bg="#F3F4F6", fg="#1E3A8A").pack()


def update_team_combo(event=None):
    selected_sport = sport_combo.get()
    if selected_sport == "Soccer":
        team_combo['values'] = [
            "Arsenal", "Manchester United", "Manchester City", "Chelsea", "Liverpool",
            "Barcelona", "Real Madrid", "Atletico Madrid", "Bayern Munich", "Borussia Dortmund",
            "Juventus", "Inter Milan", "AC Milan",
        ]
    elif selected_sport == "Basketball":
        team_combo['values'] = [
            "Los Angeles Lakers", "Golden State Warriors", "Boston Celtics", "Miami Heat", "Chicago Bulls"
        ]
    elif selected_sport == "American Football":
        team_combo['values'] = [
            "New England Patriots", "Kansas City Chiefs", "Green Bay Packers", "Dallas Cowboys", "San Francisco 49ers"
        ]
    elif selected_sport == "Baseball":
        team_combo['values'] = [
            "New York Yankees", "Boston Red Sox", "Los Angeles Dodgers", "New York Mets", "Chicago Cubs"
        ]
    else:
        team_combo['values'] = []
    team_combo.set('')  


def search_team():
    team_name = team_combo.get().strip()
    if not team_name:
        messagebox.showwarning("Warning", "Please select or enter a team name.")
        return
    
    teams = fetch_team_data(team_name)
    if not teams:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No teams found. Try a different name.")
        
        for widget in players_frame.winfo_children():
            widget.destroy()
        return
    
    
    team = teams[0]
    display_team_info(team)


root = tk.Tk()
root.title("SportsDB Team Search")
root.geometry("1200x950")
root.configure(bg="#1E3A8A")
root.resizable(True, True)


style = ttk.Style()
style.configure("TButton", font=("Roboto", 14, "bold"), padding=12, background="#F59E0B", foreground="#1E3A8A")
style.configure("TLabel", font=("Roboto", 12), background="#1E3A8A", foreground="#F3F4F6")
style.configure("TCombobox", font=("Roboto", 12), padding=8)
style.map("TButton", background=[("active", "#D97706")])


main_frame = ttk.Frame(root, padding=25)
main_frame.pack(fill="both", expand=True)


title_label = ttk.Label(main_frame, text="⚽ Ultimate Sports Team Search", font=("Roboto", 24, "bold"), foreground="#F59E0B")
title_label.pack(pady=15)


subtitle_label = ttk.Label(main_frame, text="Select a sport, then choose or enter a team name:", wraplength=900, font=("Roboto", 11))
subtitle_label.pack(pady=8)


selection_frame = ttk.Frame(main_frame)
selection_frame.pack(pady=15, fill="x")


sport_label = ttk.Label(selection_frame, text="Sport:", font=("Roboto", 12))
sport_label.pack(side="left", padx=(0, 10))

sports = ["Soccer", "Basketball", "American Football", "Baseball"]
sport_combo = ttk.Combobox(selection_frame, values=sports, font=("Roboto", 12), width=20)
sport_combo.pack(side="left", padx=(0, 20))
sport_combo.bind("<<ComboboxSelected>>", update_team_combo)
sport_combo.set("Soccer")  


team_label = ttk.Label(selection_frame, text="Team:", font=("Roboto", 12))
team_label.pack(side="left", padx=(0, 10))

team_combo = ttk.Combobox(selection_frame, font=("Roboto", 12), width=40)
team_combo.pack(side="left", expand=True, fill="x", padx=(0, 15))


update_team_combo()

search_button = ttk.Button(selection_frame, text="🔎 Search Team", command=search_team)
search_button.pack(side="right")


team_combo.bind("<Return>", lambda event: search_team())


content_frame = ttk.Frame(main_frame)
content_frame.pack(fill="both", expand=True, pady=15)


text_frame = ttk.Frame(content_frame)
text_frame.pack(fill="both", expand=True)

result_label = ttk.Label(text_frame, text="📋 Team Details:", font=("Roboto", 16, "bold"), foreground="#F59E0B")
result_label.pack(anchor="w", pady=(0, 10))

text_scroll = tk.Scrollbar(text_frame)
text_scroll.pack(side="right", fill="y")

result_text = tk.Text(text_frame, height=15, wrap=tk.WORD, font=("Roboto", 11), bg="#F3F4F6", fg="#1E3A8A", bd=2, relief="solid", yscrollcommand=text_scroll.set, padx=10, pady=10)
result_text.pack(fill="both", expand=True)
text_scroll.config(command=result_text.yview)


players_frame = tk.Frame(main_frame, bg="#1E3A8A")
players_frame.pack(fill="x", pady=15)

players_title = ttk.Label(players_frame, text="👥 Key Players:", font=("Roboto", 16, "bold"), foreground="#F59E0B")
players_title.pack(anchor="w", pady=(0, 10))


player_cards_frame = tk.Frame(players_frame, bg="#1E3A8A")
player_cards_frame.pack(fill="x")


player_images = []


root.mainloop()