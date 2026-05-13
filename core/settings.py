import json
from pathlib import Path

class SettingsManager:
    DEFAULT_PPI = 96.0

    def __init__(self, profiles_file):
        self.profiles_file = Path(profiles_file)
        self.profiles = {"Default": self.DEFAULT_PPI}
        self.load_profiles()

    def load_profiles(self):
        """Loads PPI profiles from the disk."""
        if self.profiles_file.exists():
            try:
                with self.profiles_file.open('r') as f:
                    stored = json.load(f)
                    self.profiles.update(stored)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load profiles from {self.profiles_file}")

    def save_profile(self, name, ppi):
        """Saves a new or existing PPI profile."""
        if not name or name.lower() == "default":
            return False
        
        self.profiles[name] = float(ppi)
        
        # Save only non-default profiles to disk
        to_save = {k: v for k, v in self.profiles.items() if k != "Default"}
        try:
            with self.profiles_file.open('w') as f:
                json.dump(to_save, f)
            return True
        except IOError:
            return False

    def get_profile_names(self):
        """Returns a sorted list of profile names."""
        return sorted(list(self.profiles.keys()))

    def get_ppi(self, name):
        """Returns the PPI value for a given profile name."""
        return self.profiles.get(name, self.DEFAULT_PPI)
