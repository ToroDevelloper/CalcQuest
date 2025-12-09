class UserProgress:
    def __init__(self):
        self.xp = 0
        self.current_streak = 0
        self.currency = 0
        self.level = 1
        self._xp_per_level = 100

    def add_xp(self, amount: int):
        self.xp += amount
        self._check_level_up()

    def _check_level_up(self):
        # Simple logic: level up every 100 XP (cumulative)
        # Level 1: 0-99, Level 2: 100-199, etc.
        self.level = 1 + (self.xp // self._xp_per_level)

    def increment_streak(self):
        self.current_streak += 1

    def reset_streak(self):
        self.current_streak = 0

    def add_currency(self, amount: int):
        self.currency += amount

    def spend_currency(self, amount: int):
        if amount > self.currency:
            raise ValueError("Not enough currency")
        self.currency -= amount