# VoM Tarot

A three-card tarot reader built from the cards of VoM. Visitors shuffle, choose three
cards, and get a reading written for their spread by Claude.

## What's in this folder

| Path | What it is |
| --- | --- |
| `index.html` | The reading page: shuffle, choose, reveal, reading |
| `how-to-read.html` | The instructions page |
| `styles.css` | Styles shared by both pages |
| `cards.json` | Every card: game text, omen, meanings, keywords, type, tier |
| `tarot_cards/` | The finished card images, 2 per card (upright and reversed) |
| `images/` | The original card art from the game |
| `netlify/functions/reading.mjs` | Writes the AI reading (runs on Netlify, not in the browser) |
| `netlify.toml` | Netlify settings |
| `tools/bake_cards.py` | Rebuilds `tarot_cards/` from `images/` and `cards.json` |
| `tools/download_images.py` | Downloads the original art from Google Drive |

## Trying it on your computer

Pages that load other files can't be opened by double-clicking, so run a tiny local server.
In a terminal, inside this folder:

    python -m http.server 8000

Then open http://localhost:8000 in your browser. Press Ctrl+C in the terminal to stop it.

The AI reading only runs once the site is on Netlify. Locally, the page falls back to the
built-in reading that stitches the three card meanings together, so everything else can be tested.

## Changing cards or readings

1. Edit `cards.json` (omen, upright, reversed, keywords, tier).
2. From this folder, run `python tools/bake_cards.py` to rebuild the card images.
3. Commit and push. Netlify republishes the site within a minute or two.

To change the voice or length of the AI reading, edit the `SYSTEM` text at the top of
`netlify/functions/reading.mjs`.

## Putting it online

### 1. Put the code on GitHub
1. Make a GitHub account at https://github.com if you don't have one.
2. Install GitHub Desktop: https://desktop.github.com
3. In GitHub Desktop: File > Add local repository, choose this folder, and accept the offer
   to create a repository. Name it `vom-tarot`.
4. Click "Publish repository". It can stay private.

### 2. Get a Claude API key
1. Sign in to the Claude Console at https://platform.claude.com and add a payment method.
2. Create an API key and copy it. You'll only see it once.
3. Set a monthly spend limit in the Console's billing settings, so a traffic spike can't
   run up a surprise bill. Each reading uses a small fast model and costs a fraction of a cent.

### 3. Publish with Netlify
1. Sign up at https://www.netlify.com using your GitHub account.
2. Add new site > Import an existing project > GitHub, and pick `vom-tarot`.
3. Leave the build settings as they are and click Deploy.
4. Go to Site configuration > Environment variables, add a variable named
   `ANTHROPIC_API_KEY` with your key as its value, then redeploy (Deploys > Trigger deploy).

The site is now live at an address like `vom-tarot.netlify.app`, and every push to GitHub
updates it automatically.

### 4. Point your subdomain at it
1. In Netlify: Domain management > Add a domain, and enter the subdomain,
   for example `tarot.yourgame.com`.
2. Where your domain's DNS is managed (your registrar or Cloudflare), add a record:
   - Type: `CNAME`
   - Name: `tarot` (the part before your domain)
   - Value: your Netlify address, such as `vom-tarot.netlify.app`
3. DNS can take from a few minutes to a few hours to update. Netlify then turns on HTTPS
   automatically.
