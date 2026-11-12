# The shared site (optional)

`pairtalk serve` keeps feedback on the author's computer. When coauthors elsewhere should comment, the talk can also live on
the author's own Cloudflare Pages site: anyone with the link and the passcode opens the talk, comments on any slide and click
(with a box or screenshots) and edits the script; the agent reads that feedback with `--remote`. The site is the author's:
their account, their database, their passcode. PairTalk has no server of its own.

## What it is

- `cloudflare/functions/_middleware.js`: a passcode gate (a signed, HttpOnly session cookie), then the talk and its API:
  `GET/POST /__comments`, `GET /__comments/img`, `GET/POST /__script`. Comments and script edits keep the writer's name.
- `cloudflare/schema.sql`: three D1 tables, `comments`, `comment_images` and `script_edits`.
- `pairtalk publish` bundles the talk into one HTML file and stages it with the middleware in the data home
  (`projects/<talk>/site-build/`), never in the code folder, then deploys with Wrangler.
- `node cloudflare/tests/smoke.mjs` tests the middleware offline.

## Set it up once (the author does this; it needs their account)

1. Install Wrangler next to PairTalk and sign in: `npm install wrangler@4` in the PairTalk folder, then
   `npx wrangler login`.
2. Create the Pages project and the database (choose your own names):

   ```sh
   npx wrangler pages project create your-pages-project --production-branch main
   cp cloudflare/wrangler.toml ~/.pairtalk/wrangler.user.toml
   npx wrangler d1 create pairtalk-comments --config ~/.pairtalk/wrangler.user.toml
   ```

   In `~/.pairtalk/wrangler.user.toml`, set `name` to the Pages project and add the printed `database_id` under
   `[[d1_databases]]`. Keep `binding = "COMMENTS_DB"`. This file holds your ids: it stays in your data home (git ignores it).
3. Set the two secrets; each command asks for the value: a passcode to share with coauthors, and a long random cookie secret
   (`openssl rand -hex 32`).

   ```sh
   npx wrangler pages secret put PASSCODE --project-name your-pages-project
   npx wrangler pages secret put COOKIE_SECRET --project-name your-pages-project
   ```

4. Point the talk at it and publish, creating the tables the first time:

   ```sh
   pairtalk remote mytalk --config ~/.pairtalk/wrangler.user.toml --pages-project your-pages-project
   pairtalk publish mytalk --init-db
   ```

Share the link Wrangler prints and the passcode. Ask coauthors to fill in their name in the comment panel.

Never type the passcode, the cookie secret or a token into chat, a file the agent writes, a URL or a command line: Wrangler
asks for them itself.

## The loop with the shared site

The same as on the author's computer, with `--remote`:

```sh
pairtalk watch mytalk --remote          # waits for comments and script edits on the site (every 20 s), prints a batch, exits
pairtalk script apply mytalk --remote   # writes the site's script edits into the slides
pairtalk snapshot mytalk
pairtalk publish mytalk                 # the fix goes live before the reply
pairtalk resolve mytalk <id> "reply" --remote
```

On the site, an unnamed comment counts as a coauthor's: only comments and edits under the owner's name are style evidence.

## Try it on your computer first

`pairtalk publish mytalk --dev` stages the talk, creates the tables in a local D1 and runs the site at
`http://127.0.0.1:8788` with a passcode it generates and prints (kept in `site-build/.dev.vars`). Without `--config`,
`pairtalk watch mytalk --remote` and the other `--remote` commands read that local database.

## Limits

- Everyone with the passcode has the same access; names in the panel are what people type, not accounts.
- `--remote` reads go through `wrangler d1 execute`, so each check takes a few seconds; the watcher polls every 20 s.
- PairTalk's tests run the middleware offline and the `--remote` commands against a stand-in for Wrangler and D1 (sqlite);
  a real deploy depends on your Cloudflare account.
