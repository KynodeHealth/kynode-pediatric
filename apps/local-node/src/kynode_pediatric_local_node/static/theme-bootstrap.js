// Copyright 2026 KYNODE
// Licensed under the Apache License, Version 2.0.
//
// Inline-loaded ASAP in <head> to set the theme before first paint.
// Avoids "flash of light theme" for users who chose dark.

(function bootstrapTheme() {
  try {
    // Shared key across both surfaces (local-node app and static demo) so a
    // user who picks dark in one sees dark in the other.
    const STORAGE_KEY = "kynode-pediatric-theme";
    const stored = localStorage.getItem(STORAGE_KEY);
    let theme = stored;
    if (!theme) {
      theme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    document.documentElement.setAttribute("data-theme", theme);
  } catch (_err) {
    // localStorage may be blocked in some sandboxes — default to light.
    document.documentElement.setAttribute("data-theme", "light");
  }
})();
