# PyStudio

A lightweight browser-based Python editor built with HTML, CSS and JavaScript. Python execution is powered by [Pyodide](https://pyodide.org/) and runs in the browser.

## Run locally
Open `index.html` in a modern browser with an internet connection.

## Deploy
Import this repository into Vercel. It is a static site; no build command or framework preset is required. The included `vercel.json` configures clean URLs.

## Notes
- The first run downloads the Python runtime from the Pyodide CDN.
- Python `input()` uses a browser prompt.
- Do not paste secrets or passwords into code you share.
