#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bahis / İddia Simülatörü (pygame)
- 20 Süper Lig takımı ile rastgele eşleşmeler (10 maç)
- Her maç için rastgele oranlar (ev sahibi / berabere / deplasman)
- Oranlara göre olasılık hesaplama ve skor simülasyonu
- Basit pygame arayüzü: maçları görüntüleme, tek tek veya tümünü simüle etme, maçları yeniden oluşturma
- Amaç: bahis bağımlılığı konusunda farkındalık yaratan, eğitici bir simülatör

Çalıştırma: Python 3.8+ ve pygame gerektirir.
"""

import pygame
import random
import sys
import math
import os
import time
import json
import csv
import io
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# plotting (matplotlib Agg backend for rendering to surface)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Konfigürasyon ---
WIDTH, HEIGHT = 980, 720
FPS = 30
FONT_NAME = None  # default

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
LIGHT_GRAY = (245, 245, 245)
BLUE = (40, 120, 220)
GREEN = (48, 180, 80)
RED = (220, 60, 60)
DARK = (40, 40, 40)

# 20 Süper Lig takımı (örnek liste, güncellenebilir)
TEAMS = [
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir",
    "Sivasspor", "Antalyaspor", "Konyaspor", "Kasımpaşa", "Kayserispor",
    "Göztepe", "Alanyaspor", "Hatayspor", "Gaziantep FK", "Adana Demirspor",
    "Çaykur Rizespor", "İstanbulspor", "Ankaragücü", "BB Erzurumspor", "Gençlerbirliği"
]

# --- Model ---

@dataclass
class Match:
    home: str
    away: str
    home_odd: float = field(default_factory=lambda: 2.0)
    draw_odd: float = field(default_factory=lambda: 3.2)
    away_odd: float = field(default_factory=lambda: 2.8)
    result: Optional[Tuple[int, int]] = None
    simulated: bool = False
    # team strengths included for more sophisticated model
    home_strength: float = 1.0
    away_strength: float = 1.0

    def generate_random_odds(self):
        # Oranları daha gerçekçi dağıtmak için ev sahibi avantajı olasılığına göre dağıt
        base_home = random.uniform(1.4, 2.8)
        base_away = random.uniform(1.6, 3.2)
        draw = random.uniform(2.4, 4.0)
        # Bazen ev sahibi daha yüksek favori olur
        if random.random() < 0.55:
            self.home_odd = round(base_home, 2)
            self.away_odd = round(base_away, 2)
        else:
            self.home_odd = round(base_away, 2)
            self.away_odd = round(base_home, 2)
        self.draw_odd = round(draw, 2)
        # küçük düzeltme: oranlar çok yakınsa hafifçe ayarla
        if abs(self.home_odd - self.away_odd) < 0.15:
            self.home_odd = round(self.home_odd + random.choice([-0.15, 0.15]), 2)

    def set_strengths(self, home_s: float, away_s: float):
        self.home_strength = home_s
        self.away_strength = away_s

    def implied_probabilities(self) -> Tuple[float, float, float]:
        # Onluk oranlardan tersine çevir ve normalize et
        inv_h = 1.0 / max(0.01, self.home_odd)
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-
        """
        Süper Lig İddia / Bahis Simülatörü - pygame
        Geliştirilmiş sürüm:
        - Bankroll / kupon (bet slip) ve stake
        - Bahis yerleştirme, sonuçlarda çözümleme
        - Maç istatistikleri CSV/JSON olarak kaydetme
        - Basit istatistik grafiği (matplotlib, opsiyonel)
        - Daha gerçekçi Poisson tabanlı skor modeli + takım gücü
        - Basit UI: maç listesi, seçim (H/D/A), Simulate All, Regenerate, Reset, Place Bet, Show Plot

        Not: matplotlib yüklü değilse plot özelliği devre dışı kalır.
        """

        import pygame
        import random
        import sys
        import math
        import os
        import time
        import json
        import csv
        import io
        from dataclasses import dataclass, field
        from typing import List, Optional, Tuple, Dict

        # Try to import matplotlib; plotting is optional
        _HAS_MATPLOTLIB = True
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except Exception:
            _HAS_MATPLOTLIB = False

        # --- Konfigürasyon ---
        WIDTH, HEIGHT = 980, 720
        FPS = 30
        FONT_NAME = None  # default

        # Renkler
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (220, 220, 220)
        LIGHT_GRAY = (245, 245, 245)
        BLUE = (40, 120, 220)
        GREEN = (48, 180, 80)
        RED = (220, 60, 60)
        DARK = (40, 40, 40)

        # 20 Süper Lig takımı (örnek liste, güncellenebilir)
        TEAMS = [
            "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir",
            "Sivasspor", "Antalyaspor", "Konyaspor", "Kasımpaşa", "Kayserispor",
            "Göztepe", "Alanyaspor", "Hatayspor", "Gaziantep FK", "Adana Demirspor",
            "Çaykur Rizespor", "İstanbulspor", "Ankaragücü", "BB Erzurumspor", "Gençlerbirliği"
        ]

        # --- Model ---

        @dataclass
        class Match:
            home: str
            away: str
            home_odd: float = field(default_factory=lambda: 2.0)
            draw_odd: float = field(default_factory=lambda: 3.2)
            away_odd: float = field(default_factory=lambda: 2.8)
            result: Optional[Tuple[int, int]] = None
            simulated: bool = False
            home_strength: float = 1.0
            away_strength: float = 1.0

            def generate_random_odds(self):
                base_home = random.uniform(1.4, 2.8)
                base_away = random.uniform(1.6, 3.2)
                draw = random.uniform(2.4, 4.0)
                if random.random() < 0.55:
                    self.home_odd = round(base_home, 2)
                    self.away_odd = round(base_away, 2)
                else:
                    self.home_odd = round(base_away, 2)
                    self.away_odd = round(base_home, 2)
                self.draw_odd = round(draw, 2)
                if abs(self.home_odd - self.away_odd) < 0.15:
                    self.home_odd = round(self.home_odd + random.choice([-0.15, 0.15]), 2)

            def set_strengths(self, home_s: float, away_s: float):
                self.home_strength = home_s
                self.away_strength = away_s

            def implied_probabilities(self) -> Tuple[float, float, float]:
                inv_h = 1.0 / max(0.01, self.home_odd)
                inv_d = 1.0 / max(0.01, self.draw_odd)
                inv_a = 1.0 / max(0.01, self.away_odd)
                total = inv_h + inv_d + inv_a
                return (inv_h / total, inv_d / total, inv_a / total)

            def simulate(self):
                p_home, p_draw, p_away = self.implied_probabilities()
                r = random.random()
                if r < p_home:
                    outcome = 'H'
                elif r < p_home + p_draw:
                    outcome = 'D'
                else:
                    outcome = 'A'
                base = 0.9
                if outcome == 'H':
                    mean_home = max(0.2, base * self.home_strength + (p_home * 2.4))
                    mean_away = max(0.1, base * self.away_strength + (p_away * 0.9))
                elif outcome == 'A':
                    mean_away = max(0.2, base * self.away_strength + (p_away * 2.4))
                    mean_home = max(0.1, base * self.home_strength + (p_home * 0.9))
                else:
                    mean_home = max(0.2, base * self.home_strength + (p_home * 1.4))
                    mean_away = max(0.2, base * self.away_strength + (p_away * 1.4))
                home_goals = self._sample_goals(mean_home)
                away_goals = self._sample_goals(mean_away)
                if outcome == 'H' and home_goals <= away_goals:
                    home_goals = away_goals + random.randint(1, 2)
                if outcome == 'A' and away_goals <= home_goals:
                    away_goals = home_goals + random.randint(1, 2)
                if outcome == 'D' and home_goals != away_goals:
                    match_score = random.choice([home_goals, away_goals])
                    home_goals = match_score
                    away_goals = match_score
                self.result = (home_goals, away_goals)
                self.simulated = True

            @staticmethod
            def _sample_goals(mean: float) -> int:
                lam = max(0.2, min(mean, 7.0))
                L = math.exp(-lam)
                k = 0
                p = 1.0
                while p > L and k < 20:
                    k += 1
                    p *= random.random()
                return max(0, k - 1)


        # --- UI helper ---
        class Button:
            def __init__(self, rect: pygame.Rect, text: str, color=BLUE, fg=WHITE):
                self.rect = rect
                self.text = text
                self.color = color
                self.fg = fg

            def draw(self, surf, font):
                pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
                txt = font.render(self.text, True, self.fg)
                tx = self.rect.x + (self.rect.w - txt.get_width()) // 2
                ty = self.rect.y + (self.rect.h - txt.get_height()) // 2
                surf.blit(txt, (tx, ty))

            def is_clicked(self, pos) -> bool:
                return self.rect.collidepoint(pos)


        # --- App ---
        class SimulatorApp:
            def __init__(self):
                pygame.init()
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                pygame.display.set_caption("İddia / Bahis Simülatörü")
                self.clock = pygame.time.Clock()
                self.font = pygame.font.SysFont(FONT_NAME, 18)
                self.header_font = pygame.font.SysFont(FONT_NAME, 22, bold=True)
                self.small_font = pygame.font.SysFont(FONT_NAME, 14)

                # state
                self.matches: List[Match] = []
                self.generate_matches()
                self.bankroll = 1000.0
                self.stake = 10.0
                self.bet_slip: List[Dict] = []
                self.log_dir = os.path.join(os.path.dirname(__file__), "logs")
                os.makedirs(self.log_dir, exist_ok=True)

                # buttons
                self.btn_simulate = Button(pygame.Rect(WIDTH - 220, 20, 200, 40), "Simulate All")
                self.btn_regen = Button(pygame.Rect(WIDTH - 220, 70, 200, 34), "Regenerate Matches", color=GREEN)
                self.btn_reset = Button(pygame.Rect(WIDTH - 220, 110, 200, 34), "Reset Results", color=GRAY, fg=DARK)
                self.btn_place_bet = Button(pygame.Rect(WIDTH - 220, 150, 200, 34), "Place Bet", color=BLUE)
                self.btn_plot = Button(pygame.Rect(WIDTH - 220, 190, 200, 34), "Show Stats Plot", color=GREEN)

                # layout
                self.list_area = pygame.Rect(20, 90, WIDTH - 260, HEIGHT - 120)

            def generate_matches(self):
                pool = TEAMS.copy()
                random.shuffle(pool)
                self.matches = []
                for i in range(0, len(pool), 2):
                    m = Match(pool[i], pool[i+1])
                    # give simple random strength values
                    m.set_strengths(random.uniform(0.8, 1.4), random.uniform(0.8, 1.4))
                    m.generate_random_odds()
                    self.matches.append(m)

            def reset_results(self):
                for m in self.matches:
                    m.result = None
                    m.simulated = False
                self.bet_slip.clear()

            def simulate_all(self):
                for m in self.matches:
                    m.simulate()
                self._settle_bets()
                self._write_match_log()

            def run(self):
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            pos = event.pos
                            if self.btn_simulate.is_clicked(pos):
                                self.simulate_all()
                            elif self.btn_regen.is_clicked(pos):
                                self.generate_matches()
                            elif self.btn_reset.is_clicked(pos):
                                self.reset_results()
                            elif self.btn_place_bet.is_clicked(pos):
                                self._place_bet_on_selected()
                            elif self.btn_plot.is_clicked(pos):
                                self._render_stats_plot()
                            else:
                                clicked_idx = self._match_index_at(pos)
                                if clicked_idx is not None:
                                    self._toggle_selection(clicked_idx)

                    self._draw()
                    pygame.display.flip()
                    self.clock.tick(FPS)
                pygame.quit()

            def _match_index_at(self, pos) -> Optional[int]:
                x, y = pos
                if not self.list_area.collidepoint(pos):
                    return None
                row_h = 48
                rel_y = y - self.list_area.y
                idx = rel_y // row_h
                if 0 <= idx < len(self.matches):
                    return int(idx)
                return None

            def _draw(self):
                self.screen.fill(LIGHT_GRAY)
                # Header
                pygame.draw.rect(self.screen, WHITE, (10, 10, WIDTH - 240, 70), border_radius=6)
                hdr = self.header_font.render("Süper Lig İddia Simülatörü", True, DARK)
                self.screen.blit(hdr, (22, 18))
                info = self.small_font.render("Takımlar rastgele eşleştirildi. Her satıra tıklayarak tek maç simüle edilebilir.", True, DARK)
                self.screen.blit(info, (22, 44))

                # Buttons
                self.btn_simulate.draw(self.screen, self.font)
                self.btn_regen.draw(self.screen, self.small_font)
                self.btn_reset.draw(self.screen, self.small_font)
                self.btn_place_bet.draw(self.screen, self.small_font)
                self.btn_plot.draw(self.screen, self.small_font)

                # List background
                pygame.draw.rect(self.screen, WHITE, self.list_area, border_radius=6)
                # Column titles
                col_x = self.list_area.x + 12
                y = self.list_area.y + 10
                # Draw matches
                row_h = 48
                for i, m in enumerate(self.matches):
                    ry = self.list_area.y + 10 + i * row_h
                    row_rect = pygame.Rect(self.list_area.x + 6, ry - 4, self.list_area.w - 12, row_h - 6)
                    pygame.draw.rect(self.screen, LIGHT_GRAY if i % 2 == 0 else WHITE, row_rect)
                    x = col_x
                    # team + odds
                    self.screen.blit(self.font.render(m.home, True, DARK), (x, ry))
                    x += 170
                    self.screen.blit(self.font.render(f"{m.home_odd:.2f}", True, DARK), (x, ry))
                    x += 60
                    self.screen.blit(self.font.render(f"{m.draw_odd:.2f}", True, DARK), (x, ry))
                    x += 72
                    self.screen.blit(self.font.render(f"{m.away_odd:.2f}", True, DARK), (x, ry))
                    x += 80
                    self.screen.blit(self.font.render(m.away, True, DARK), (x, ry))
                    x += 150
                    # probabilities bar
                    p_h, p_d, p_a = m.implied_probabilities()
                    bar_w = 140
                    bx = x
                    by = ry + 6
                    pygame.draw.rect(self.screen, GRAY, (bx, by, bar_w, 12), border_radius=6)
                    pygame.draw.rect(self.screen, BLUE, (bx, by, max(1, int(bar_w * p_h)), 12))
                    pygame.draw.rect(self.screen, GRAY, (bx + int(bar_w * p_h), by, max(1, int(bar_w * p_d)), 12))
                    pygame.draw.rect(self.screen, RED, (bx + int(bar_w * (p_h + p_d)), by, max(1, int(bar_w * p_a)), 12))
                    self.screen.blit(self.small_font.render(f"H:{p_h*100:.0f}% D:{p_d*100:.0f}% A:{p_a*100:.0f}%", True, DARK), (bx + bar_w + 6, ry + 2))
                    # score
                    score_text = f"{m.result[0]} - {m.result[1]}" if m.result else "-"
                    self.screen.blit(self.header_font.render(score_text, True, DARK if m.result else GRAY), (bx + bar_w + 110, ry - 4))
                    # selection marker
                    sel = next((b for b in self.bet_slip if b['match_idx'] == i), None)
                    if sel:
                        self.screen.blit(self.small_font.render(sel['selection'], True, RED), (self.list_area.x + 6, ry))

                # Footer
                footer_rect = pygame.Rect(10, HEIGHT - 80, WIDTH - 20, 70)
                pygame.draw.rect(self.screen, WHITE, footer_rect, border_radius=6)
                msg1 = "Bu uygulama eğitim amaçlıdır. Gerçek bahis bağımlılığına karşı yardım için profesyonel destek alın."
                msg2 = "Simülasyonlarda kaybetme riski vardır — sorumlu olun."
                self.screen.blit(self.small_font.render(msg1, True, DARK), (20, HEIGHT - 68))
                self.screen.blit(self.small_font.render(msg2, True, DARK), (20, HEIGHT - 48))
                bb = f"Bankroll: {self.bankroll:.2f}  Stake: {self.stake:.2f}  Slip items: {len(self.bet_slip)}"
                self.screen.blit(self.small_font.render(bb, True, DARK), (WIDTH - 420, HEIGHT - 52))

            # Betting helpers
            def _toggle_selection(self, match_idx: int):
                existing = next((b for b in self.bet_slip if b['match_idx'] == match_idx), None)
                order = [None, 'H', 'D', 'A']
                if not existing:
                    sel = 'H'
                    odd = self.matches[match_idx].home_odd
                    self.bet_slip.append({'match_idx': match_idx, 'selection': sel, 'odd': odd})
                    return
                cur = existing['selection']
                idx = order.index(cur) if cur in order else 0
                new_idx = (idx + 1) % len(order)
                new_sel = order[new_idx]
                if new_sel is None:
                    self.bet_slip = [b for b in self.bet_slip if b['match_idx'] != match_idx]
                else:
                    existing['selection'] = new_sel
                    if new_sel == 'H':
                        existing['odd'] = self.matches[match_idx].home_odd
                    elif new_sel == 'D':
                        existing['odd'] = self.matches[match_idx].draw_odd
                    else:
                        existing['odd'] = self.matches[match_idx].away_odd

            def _place_bet_on_selected(self):
                if not self.bet_slip:
                    return
                total_stake = self.stake
                combined_odd = 1.0
                for b in self.bet_slip:
                    combined_odd *= max(1.01, b['odd'])
                if total_stake > self.bankroll:
                    return
                self.bankroll -= total_stake
                bet_record = {'time': time.time(), 'stake': total_stake, 'combined_odd': combined_odd, 'items': list(self.bet_slip), 'settled': False}
                self._append_json_log('bets.json', bet_record)

            def _settle_bets(self):
                path = os.path.join(self.log_dir, 'bets.json')
                if not os.path.exists(path):
                    return
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        bets = json.load(f)
                except Exception:
                    return
                changed = False
                for b in bets:
                    if b.get('settled'):
                        continue
                    won = True
                    for item in b['items']:
                        m = self.matches[item['match_idx']]
                        if not m.result:
                            won = False
                            break
                        h, a = m.result
                        sel = item['selection']
                        if sel == 'H' and h <= a:
                            won = False
                        if sel == 'A' and a <= h:
                            won = False
                        if sel == 'D' and h != a:
                            won = False
                    if won:
                        payout = b['stake'] * b['combined_odd']
                        self.bankroll += payout
                        b['payout'] = payout
                    else:
                        b['payout'] = 0.0
                    b['settled'] = True
                    changed = True
                if changed:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(bets, f, ensure_ascii=False, indent=2)

            def _append_json_log(self, filename: str, record: dict):
                path = os.path.join(self.log_dir, filename)
                arr = []
                if os.path.exists(path):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            arr = json.load(f)
                    except Exception:
                        arr = []
                arr.append(record)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(arr, f, ensure_ascii=False, indent=2)

            def _write_match_log(self):
                ts = int(time.time())
                csv_path = os.path.join(self.log_dir, f'matches_{ts}.csv')
                json_path = os.path.join(self.log_dir, f'matches_{ts}.json')
                with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
                    w = csv.writer(cf)
                    w.writerow(['home', 'away', 'home_odd', 'draw_odd', 'away_odd', 'home_goals', 'away_goals'])
                    for m in self.matches:
                        h, a = (m.result if m.result else (None, None))
                        w.writerow([m.home, m.away, m.home_odd, m.draw_odd, m.away_odd, h, a])
                with open(json_path, 'w', encoding='utf-8') as jf:
                    out = []
                    for m in self.matches:
                        out.append({'home': m.home, 'away': m.away, 'home_odd': m.home_odd, 'draw_odd': m.draw_odd, 'away_odd': m.away_odd, 'result': m.result})
                    json.dump(out, jf, ensure_ascii=False, indent=2)

            def _render_stats_plot(self):
                if not _HAS_MATPLOTLIB:
                    return
                files = sorted([f for f in os.listdir(self.log_dir) if f.startswith('matches_') and f.endswith('.csv')])
                if not files:
                    return
                latest = os.path.join(self.log_dir, files[-1])
                goals = []
                with open(latest, 'r', encoding='utf-8') as cf:
                    r = csv.DictReader(cf)
                    for row in r:
                        try:
                            if row['home_goals']:
                                goals.append(int(row['home_goals']))
                            if row['away_goals']:
                                goals.append(int(row['away_goals']))
                        except Exception:
                            pass
                if not goals:
                    return
                plt.figure(figsize=(4,2.5))
                plt.hist(goals, bins=range(0,8), align='left', color='#3b82f6')
                plt.title('Goals distribution')
                plt.xlabel('Goals')
                plt.ylabel('Count')
                buf = io.BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)
                try:
                    img = pygame.image.load(buf, 'plot.png')
                except Exception:
                    return
                popup = pygame.Surface((img.get_width()+20, img.get_height()+60))
                popup.fill(WHITE)
                popup.blit(img, (10,10))
                self.screen.blit(popup, (WIDTH//2 - popup.get_width()//2, HEIGHT//2 - popup.get_height()//2))


        if __name__ == '__main__':
            app = SimulatorApp()
            app.run()
