# Renders docs/demo.gif with charmbracelet/vhs (needs vhs, ttyd and ffmpeg on PATH).
# Run from the repo root, with the deps installed in .venv:  vhs docs/demo.tape
# Follows DEMO.md: offline tests -> make demo on the bundled mock target -> the report banner and failures.
Output docs/demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 700
Set Padding 24
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful
Set TypingSpeed 40ms

Hide
Type "VIRTUAL_ENV_DISABLE_PROMPT=1 source .venv/bin/activate"
Enter
Wait@120s
Type "rm -rf out"
Enter
Wait@120s
Type "clear"
Enter
Wait@120s
Show
Sleep 500ms

Type "make test"
Sleep 400ms
Enter
Wait@120s
Sleep 2s

Type "make demo | head -2"
Sleep 400ms
Enter
Wait@120s
Sleep 3s

Hide
Type "clear"
Enter
Sleep 200ms
Show
Type "sed -n '1,7p' out/report.md"
Sleep 400ms
Enter
Wait@120s
Sleep 3s

Type "grep -E '^\| FAIL' out/report.md | cut -c1-100"
Sleep 400ms
Enter
Wait@120s
Sleep 4.5s

Sleep 1s
