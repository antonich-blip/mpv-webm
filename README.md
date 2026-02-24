# mpv-webm Development Environment

Isolated development environment for the mpv-webm plugin (https://github.com/ekisu/mpv-webm).

## Structure

```
~/dev/mpv-webm/          # Cloned plugin repository (source code)
~/.config/mpv-dev/       # Isolated mpv configuration
  ├── mpv.conf           # Dev-specific mpv config
  ├── scripts/
  │   └── webm.lua       # Symlink to built plugin
  └── script-opts/
      └── webm.conf      # Plugin configuration
~/.local/bin/mpv-dev     # Wrapper script for isolated mpv
```

## Setup Steps Completed

1. **Cloned repository**: `~/dev/mpv-webm/`
2. **Built plugin**: Run `make` in `~/dev/mpv-webm/` with moonscript
3. **Created isolated config**: `~/.config/mpv-dev/`
4. **Created wrapper script**: `~/.local/bin/mpv-dev`

## Usage

### Running Isolated mpv

```bash
# Add to PATH (add to ~/.bashrc or ~/.config/fish/config.fish)
export PATH="$HOME/.local/bin:$PATH"

# Run mpv with isolated config
mpv-dev /path/to/video.mp4
mpv-dev https://example.com/video.mp4
```

### Rebuilding the Plugin

After making changes to the plugin source code:

```bash
# Option 1: Rebuild then run
mpv-dev --rebuild /path/to/video.mp4

# Option 2: Just rebuild
cd ~/dev/mpv-webm
nix-shell -p luaPackages.moonscript --run "make"

# Then update symlink
ln -sf ~/dev/mpv-webm/build/webm.lua ~/.config/mpv-dev/scripts/webm.lua
```

### Development Workflow

1. Edit source files in `~/dev/mpv-webm/src/`
2. Rebuild with `mpv-dev --rebuild` or manually:
   ```bash
   cd ~/dev/mpv-webm && nix-shell -p luaPackages.moonscript --run "make"
   ln -sf ~/dev/mpv-webm/build/webm.lua ~/.config/mpv-dev/scripts/webm.lua
   ```
3. Test with `mpv-dev /path/to/test/video.mp4`

### Custom mpv Binary

To use a custom mpv binary (e.g., a custom-built version):

```bash
MPV_DEV_MPV=/path/to/custom/mpv mpv-dev /path/to/video.mp4
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MPV_DEV_MPV` | Custom mpv binary path | `mpv` (system) |

## Notes

- The isolated config uses `--no-config` and `--config-dir` to prevent loading any external configuration
- Log file is written to `~/.config/mpv-dev/mpv-dev.log`
- Debug messages are enabled by default in the dev config

## Troubleshooting

### Plugin not loading
- Check log file: `cat ~/.config/mpv-dev/mpv-dev.log`
- Verify symlink: `ls -la ~/.config/mpv-dev/scripts/webm.lua`
- Rebuild: `mpv-dev --rebuild`

### "moonc not found"
- Use nix-shell: `nix-shell -p luaPackages.moonscript --run "make"`
