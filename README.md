# 477 Final Project
---

This is an [Observable Framework](https://observablehq.com/framework/) app. To install the required dependencies, run:

```
npm install
```

Then, to start the local preview server, run:

```
npm run dev
```

Then visit <http://localhost:3000> to preview your app.

For more, see <https://observablehq.com/framework/getting-started>.

## Project structure

```ini
.
├─ src
│  ├─ data
│  │  ├─ processed/            # transformed datasets used in visualizations
│  │  │  ├─ us_coastal_cities.csv
│  │  │  ├─ us_projections.json
│  │  │  └─ us-states-10m.json
│  │  ├─ raw/                  # original downloaded datasets
│  │  │  ├─ locations.lst
│  │  │  └─ ar6-regional-confidence/
│  │  ├─ archived/             # historical datasets not currently used
│  │  └─ README.md             # data documentation
│  ├─ scripts
│  │  ├─ extract_us_projections.py  # data processing script
│  │  └─ README.md
│  ├─ pages
│  │  ├─ sea-level-rise.md          # main visualization page
│  │  ├─ data-documentation.md      # technical documentation
│  │  └─ README.md
│  ├─ docs
│  │  └─ project_proposal.md        # original project proposal
│  ├─ components/                   # reusable JS modules
│  ├─ index.md                      # home page
│  └─ observable.png                # favicon
├─ .gitignore
├─ observablehq.config.js           # app config file
├─ package.json
└─ README.md
```

**`src`** - This is the “source root” — where your source files live. Pages go here. Each page is a Markdown file. Observable Framework uses [file-based routing](https://observablehq.com/framework/project-structure#routing), which means that the name of the file controls where the page is served. You can create as many pages as you like. Use folders to organize your pages.

**`src/index.md`** - This is the home page for your app. You can have as many additional pages as you’d like, but you should always have a home page, too.

**`src/data`** - You can put [data loaders](https://observablehq.com/framework/data-loaders) or static data files anywhere in your source root, but we recommend putting them here.

**`src/components`** - You can put shared [JavaScript modules](https://observablehq.com/framework/imports) anywhere in your source root, but we recommend putting them here. This helps you pull code out of Markdown files and into JavaScript modules, making it easier to reuse code across pages, write tests and run linters, and even share code with vanilla web applications.

**`observablehq.config.js`** - This is the [app configuration](https://observablehq.com/framework/config) file, such as the pages and sections in the sidebar navigation, and the app’s title.

## Command reference

| Command           | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `npm install`            | Install or reinstall dependencies                        |
| `npm run dev`        | Start local preview server                               |
| `npm run build`      | Build your static site, generating `./dist`              |
| `npm run deploy`     | Deploy your app to Observable                            |
| `npm run clean`      | Clear the local data loader cache                        |
| `npm run observable` | Run commands like `observable help`                      |
