# 🛠 dotfiles/.zshrc

A cross-platform `.zshrc` configuration that works seamlessly across **macOS** and **Linux**, with support for:

- ✅ [Oh My Zsh](https://ohmyz.sh/) and custom plugins
- ✅ [Homebrew](https://brew.sh/) on both platforms
- ✅ [Miniforge](https://github.com/conda-forge/miniforge) / [Mamba](https://github.com/mamba-org/mamba) environment management
- ✅ Shell PATH toggling via `perseus` and `medusa`
- ✅ Per-machine overrides via `.zshrc.local`

---

## 🚀 Features

| Feature                  | Details                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| Platform detection       | Automatically detects macOS or Linux via `uname`                       |
| Homebrew paths           | Dynamically sets `$HOMEBREW_PREFIX` and `$PATH`                        |
| Miniforge / Mamba        | Initializes conda/mamba and activates `craigdev` if it exists          |
| `perseus` / `medusa`     | Functions to safely toggle Miniforge off/on for Homebrew compatibility |
| GitHub-friendly          | Versioned `.zshrc`, with private `.zshrc.local` ignored                |

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone git@github.com:yourusername/dotfiles.git ~/dotfiles
```

### 2. Link the `.zshrc` to your home directory

```bash
ln -sf ~/dotfiles/.zshrc ~/.zshrc
```

### 3. (Optional) Add machine-specific config

Create a `.zshrc.local` file for secrets or overrides:

```bash
touch ~/.zshrc.local
```

Example contents:

```zsh
export EDITOR=nvim
export SSH_AUTH_SOCK="$HOME/.1password/agent.sock"
```

This file is ignored from GitHub via `.gitignore`.

---

## 🧠 Tips

- `perseus`: Removes Miniforge from PATH — use this before running `brew install`
- `medusa`: Restores Miniforge/Mamba into PATH after Homebrew actions
- `.zshrc.local`: Use this for anything specific to your system or secret (like auth tokens)

---

## 🍺 Brewfile Management

Homebrew’s **Brewfile** lets you specify taps, formulae, and casks in a single file, with OS‐specific blocks.

### Generating a Brewfile

To dump your current setup (taps, formulae, casks) into `~/dotfiles/Brewfile`, run:

```bash
brew bundle dump   --file=~/dotfiles/Brewfile   --force   --describe
```

> **Note**: The `--no-lock` option isn’t valid for `brew bundle dump`. This command will also produce a `Brewfile.lock.json`. If you don’t want to track the lock file, add:

```bash
echo "Brewfile.lock.json" >> ~/dotfiles/.gitignore
```

You can wrap entries in `if OS.mac?` and `if OS.linux?` blocks to handle platform differences in a single Brewfile.

### Installing from a Brewfile

On any machine with Homebrew installed, run:

```bash
brew bundle --file=~/dotfiles/Brewfile
```

This will install exactly the taps, formulae, and casks listed, skipping those already present.

---

## 🐍 Mamba Integration

If you use [Mamba](https://github.com/mamba-org/mamba), and the environment `craigdev` exists, it will be auto-activated on shell startup.

To create it:

```bash
mamba create -n craigdev python=3.11
```

#### 🔄 Updating Mamba to the Latest Version

If you encounter errors about commands like `mamba shell hook` or see messages such as:

```
invalid choice: 'shell'
or
Run 'mamba init' to be able to run mamba activate/deactivate
```

you may be running an older Mamba build. Ensure you have the latest Mamba in your `base` environment:

```bash
~/miniforge3/bin/conda install -n base -c conda-forge mamba
```

Then verify the version:

```bash
~/miniforge3/bin/mamba --version
```

After updating, restart your shell to load the new functionality:

```bash
exec zsh
```

---

## 🔄 Mamba Environment Sync

To share or version-control your Mamba environment (e.g., `craigdev`), follow these steps:

1. **Export** your environment to YAML:

   ```bash
   mamba activate craigdev
   mkdir -p ~/dotfiles/envs
   mamba env export --from-history --name craigdev > ~/dotfiles/envs/craigdev.yml
   ```

   > `--from-history` ensures only explicitly installed packages are included in the file.

2. **Commit** the YAML file:

   ```bash
   cd ~/dotfiles
   git add envs/craigdev.yml
   git commit -m "📦 Export craigdev environment"
   git push
   ```

3. **Recreate** the environment on another machine:

   ```bash
   cd ~/dotfiles
   mamba env create --file envs/craigdev.yml
   ```

4. **Updating** your environment:

   - Edit `envs/craigdev.yml` to add, remove, or change package specifications.
   - Then run:

     ```bash
     mamba env update --name craigdev --file envs/craigdev.yml
     ```

   - Finally, restart your shell or re-activate:

     ```bash
     mamba activate craigdev
     ```

By tracking your `envs/*.yml` files in Git alongside your dotfiles, all machines can spin up and maintain identical development environments.

---

## 🖥 iTerm2 Preferences Sync

If you’ve made changes to your iTerm2 profiles (colors, key mappings, window arrangements, etc.) on one Mac, follow these steps to propagate them to all your machines:

1. **Ensure iTerm2 is pointed to your dotfiles folder**:
   - Open **iTerm2 → Preferences → General → Preferences**
   - Verify **“Load preferences from a custom folder or URL”** is set to `~/dotfiles/iterm2`
   - Enable **“Save changes to folder when iTerm2 quits”** (or **“Automatically save changes”**).

2. **Save and export your current settings**:
   - Either click **“Save Settings to Folder”** in that pane, or quit iTerm2 (`Cmd+Q`) to auto-export.

3. **Commit & push** the updated prefs:

   ```bash
   cd ~/dotfiles/iterm2
   git add .
   git commit -m "🖥 Update iTerm2 preferences"
   git push
   ```

4. **On each other Mac**, pull and restart:

   ```bash
   cd ~/dotfiles
   git pull
   killall iTerm2; open -a Iterm2
   ```

### Automatic Profile Switching

To have iTerm2 automatically swap color schemes based on the remote host:

1. **Create profiles** in iTerm2 for each host:
   - **iTerm2 → Preferences → Profiles → +** to add a profile (e.g. “server-db”).
   - In **Colors**, choose a distinct preset.

2. **Add an Automatic Profile Switching rule**:
   - In the profile’s **Advanced** tab, under **Automatic Profile Switching**, click **Add**.
   - Select **“Host Name matches”** and enter the hostname or regex (e.g. `^db-server\.example\.com$`).

3. **SSH to the host**:

   ```bash
   ssh db-server.example.com
   ```

   iTerm2 will detect the hostname and apply the matching profile automatically.

### Escape-Sequence Method

If you prefer switching profiles from the remote side, add this to the remote host’s `~/.zshrc`:

```zsh
# Switch iTerm2 on login to MyRemoteProfile
if [ -n "$ITERM_SESSION_ID" ]; then
  printf '\033]50;SetProfile=MyRemoteProfile\a'
fi
```

- Ensure a local profile named **MyRemoteProfile** exists in `~/dotfiles/iterm2`.
- On SSH login, iTerm2 receives the escape code and switches to that profile.

---

## 🐚 iTerm2 Shell Integration

To enable advanced iTerm2 features (automatic cwd sync, bracketed paste, enhanced key-bindings):

1. **Install the integration script** (one-time per machine):

   - **Via iTerm2 UI**:
     **Preferences → General → Advanced → Install Shell Integration**

   - **Manually**:
     ```zsh
     curl -L https://iterm2.com/shell_integration/zsh        -o ~/.iterm2_shell_integration.zsh
     ```

2. **Source the script** in your `~/.zshrc` (already included in this repo):
   ```zsh
   if [ -f "${HOME}/.iterm2_shell_integration.zsh" ]; then
     source "${HOME}/.iterm2_shell_integration.zsh"
   fi
   ```

3. **Restart your shell**:
   ```zsh
   exec zsh
   # or quit & reopen iTerm2
   ```

4. **Verify** by running:
   ```bash
   type __iterm2_print_user_vars
   echo $ITERM_SESSION_ID
   ```

---

## 🔐 SSH Access to GitHub

If pushing to GitHub fails with `Permission denied (publickey)`:

1. Generate a key (if needed):
   ```bash
   ssh-keygen -t ed25519 -C "you@example.com"
   ```
2. Add your public key to GitHub: <https://github.com/settings/keys>
3. Test:
   ```bash
   ssh -T git@github.com
   ```

---

## 📥 Installing Miniforge3 & Mamba

To bootstrap a fresh macOS or Linux machine with Miniforge3 (and Mamba), do the following:

1. **Download the appropriate installer** from the latest Miniforge3 releases:
   - **macOS (ARM64)**:
     ```zsh
     curl -L -o Miniforge3-MacOSX-arm64.sh        https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
     ```
   - **macOS (x86_64)**:
     ```zsh
     curl -L -o Miniforge3-MacOSX-x86_64.sh        https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
     ```
   - **Linux (x86_64)**:
     ```zsh
     curl -L -o Miniforge3-Linux-x86_64.sh        https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
     ```
2. **Run the installer**:
   ```zsh
   zsh Miniforge3-*.sh
   ```
   Accept the license, choose the default install location (`~/miniforge3`), and allow it to initialize your shell.
3. **Restart your shell**:
   ```zsh
   exec zsh
   ```
4. **Install or update Mamba** in the `base` environment:
   ```zsh
   conda install -n base -c conda-forge mamba
   ```
5. **Verify** that Mamba is correctly installed:
   ```bash
   mamba --version
   ```

---

## ✨ License

MIT License — customize, share, and reuse freely.
---

# Anki Pipeline Tooling (canonical MD → HTML → TSV → Anki)

This repo includes a repeatable, scriptable workflow for taking **canonical Markdown** sources, converting them to **HTML**, extracting **AFTER** answers into TSV, merging with a `base.tsv`, and updating existing notes via **AnkiConnect**.

## Requirements

- Anki desktop running
- AnkiConnect installed and enabled (default URL: `http://127.0.0.1:8765`)
- One of:
  - MultiMarkdown 6 (`multimarkdown` CLI), **or**
  - Pandoc (`pandoc` CLI)

## File layout (per dataset “slug”)

For a slug like `systems-electrical`, the canonical and generated files are:

- Canonical source:
  - `domains/<domain>/anki/sources/<slug>__canonical.md`
- Generated:
  - `domains/<domain>/anki/generated/<slug>__canonical.html`
- Exports (TSV):
  - `domains/<domain>/anki/exports/<slug>__canonical__after_html.tsv`
  - `domains/<domain>/anki/exports/<slug>__canonical__import_html.tsv`

`__after_html.tsv` contains `note_id` + HTML extracted from each `### AFTER` block.
`__import_html.tsv` is the merge of base note metadata with the new HTML answer.

## Canonical Markdown conventions

Canonical source files are structured as repeated blocks:

- `## <note_id>`
- `### BEFORE` (reference / legacy)
- `### AFTER` (**the authoritative answer**)
- `---` as a block separator

Within `### AFTER`, prefer normal Markdown:

- Paragraphs separated by blank lines
- Lists use `- ` (hyphen + space)
- Avoid Unicode bullets like `•`

## Validator

To lint (and optionally fix) canonical Markdown:

```bash
python3 tools/anki/validate_canonical_md.py --in domains/b737/anki/sources/systems-electrical__canonical.md
# optional:
python3 tools/anki/validate_canonical_md.py --in ... --fix
```

## End-to-end pipeline (recommended)

The orchestrator is `tools/anki/pipeline.py`.

Example (B737 electrical):

```bash
# 1) canonical.md → canonical.html
python3 tools/anki/pipeline.py --slug systems-electrical html --engine multimarkdown

# 2) canonical.html → after_html.tsv
python3 tools/anki/pipeline.py --slug systems-electrical after-html

# 3) base.tsv + after_html.tsv → import_html.tsv
python3 tools/anki/pipeline.py --slug systems-electrical merge-html

# 4) import_html.tsv → update notes in Anki (dry-run first!)
python3 tools/anki/pipeline.py --slug systems-electrical update-html --dry-run
python3 tools/anki/pipeline.py --slug systems-electrical update-html
```

### Updating a different domain/location

All directory roots are configurable:

```bash
python3 tools/anki/pipeline.py \
  --slug my-topic \
  --sources domains/mydomain/anki/sources \
  --generated domains/mydomain/anki/generated \
  --exports domains/mydomain/anki/exports \
  html --engine pandoc
```

## Low-level scripts

These are useful for debugging or composing custom workflows:

- `tools/anki/md_to_html.py` — Markdown/MMD → HTML (`--engine multimarkdown|pandoc`)
- `tools/anki/html_after_to_tsv.py` — extract AFTER blocks from HTML → TSV
- `tools/anki/merge_base_and_after.py` — merge base.tsv with after.tsv by `note_id`
- `tools/anki/update_notes_from_tsv.py` — apply TSV updates to Anki via AnkiConnect

Notes:
- `updateNoteFields` is called **per note** for compatibility with AnkiConnect v6.
- HTML payloads must contain **real newlines**, not the two-character sequence `\n`. (The updater normalizes this.)

## Git hygiene

Generated artifacts are intended to be reproducible; prefer committing only:
- canonical sources (`domains/**/anki/sources/*.md`)
- tooling (`tools/anki/*.py`)
- docs

Exports/generated outputs should typically be ignored via `.gitignore`.

