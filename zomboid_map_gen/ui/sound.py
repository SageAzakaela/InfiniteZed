from pathlib import Path

class SoundPlayer:
    """
    Looks for WAV files at <project_root>/assets/sound/{click,bubblepop,tada,oops}.wav
    Uses winsound on Windows; no-ops quietly elsewhere or if files are missing.
    """
    def __init__(self, project_root: Path):
        self.paths = {
            "click": project_root / "assets" / "sound" / "click.wav",
            "bubble": project_root / "assets" / "sound" / "bubblepop.wav",
            "tada":  project_root / "assets" / "sound" / "tada.wav",
            "oops":  project_root / "assets" / "sound" / "oops.wav",
        }
        self.win = None
        try:
            import winsound  # type: ignore
            self.win = winsound
        except Exception:
            pass

    def _play(self, key: str):
        if self.win is None: return
        p = self.paths.get(key)
        if not p or not p.exists(): return
        try:
            self.win.PlaySound(str(p), self.win.SND_FILENAME | self.win.SND_ASYNC)
        except Exception:
            pass

    def click(self): self._play("click")
    def bubble(self): self._play("bubble")
    def tada(self): self._play("tada")
    def oops(self): self._play("oops")
