"""Static safety checks for the JDSP hot-reload helper."""

from __future__ import annotations

import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "hot_reload_liveprog.sh"


class HotReloadLiveprogTests(unittest.TestCase):
    def test_preserves_qualified_limiter_threshold_after_preset_save(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        save_index = text.index('jamesdsp --save-preset "$preset_name"')
        restore_index = text.index('force_config master_limthreshold "$qualified_master_limthreshold"')
        preset_patch_index = text.index('sed -i "s/^master_limthreshold=')
        self.assertLess(save_index, preset_patch_index)
        self.assertLess(save_index, restore_index)
        self.assertIn('qualified_master_limthreshold="-1.0"', text)


if __name__ == "__main__":
    unittest.main()
