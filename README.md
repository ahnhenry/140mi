# 140mi

> Artemis II was NASA's first crewed Artemis flight, a stepping stone in a campaign that leads to the first human footsteps on Mars. That mission to Mars is what 140mi is named for.

140mi is a full-stack web application for exploring NASA's image library. Search and browse space photography from Mars rovers, missions, and beyond — all powered by NASA's public API.

---

## Features

- **Search NASA's image library** — search thousands of real NASA photos by keyword (e.g. "curiosity rover", "Mars landscape", "Artemis")
- **Photo grid** — results displayed in a clean, responsive grid
- **Lightbox viewer** — click any photo to view it full size
- **User accounts** — register, log in, and log out
- **Favorites** — save photos to your account 

---

## What You Need Before Starting

You don't need to be a developer to run this app locally, but you will need a few things installed on your computer:

| Tool | What it is | Download |
|------|-----------|---------|
| Python 3 | The programming language the app runs on | [python.org](https://python.org) |
| pip | Python's package installer (comes with Python) | included |
| Git | For cloning the repo | [git-scm.com](https://git-scm.com) |

---

## Setup Instructions

### 1. Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/yourusername/140mi.git
cd 140mi
```

### 2. Create a virtual environment

A virtual environment keeps this project's dependencies separate from the rest of your computer.

```bash
python3 -m venv venv
source venv/bin/activate
```

> On Windows, use `venv\Scripts\activate` instead.

You'll know it's active when you see `(venv)` at the start of your terminal prompt.

### 3. Install dependencies

```bash
pip install flask python-dotenv requests 'urllib3<2'
```

### 4. Get a NASA API key

1. Go to [https://api.nasa.gov](https://api.nasa.gov)
2. Fill out the short form with your name and email
3. Your API key will appear on the page immediately and be emailed to you

The key is free and gives you up to 1,000 requests per hour.

### 5. Create your API key file

In the root of the project, create a file called `api.env`:

```
NASA_API_KEY=your_key_here
```

Replace `your_key_here` with the key you just got from NASA. This file is listed in `.gitignore` so it will never be accidentally committed to GitHub.

### 6. Set up the database

```bash
python3 -c "import sqlite3; conn = sqlite3.connect('database.db'); conn.close()"
```

### 7. Run the app

```bash
python3 main.py
```

Then open your browser and go to:

```
http://localhost:8080
```

---

## How to Use

1. **Search** — type any space-related keyword into the search bar on the Rovers page and hit Search. Try "mars surface", "perseverance", or "apollo".
2. **Browse** — scroll through the photo grid to explore results.
3. **View full size** — click any photo to open it in a lightbox overlay. Click anywhere outside the photo or the X button to close it.
4. **Register / Log in** — create an account using the Register link in the navigation bar.

---

## API Information

This app uses two NASA APIs:

### NASA Image and Video Library
- **Base URL:** `https://images-api.nasa.gov`
- **Endpoint used:** `/search`
- **Requires API key:** No
- **Documentation:** [images.nasa.gov/docs](https://images.nasa.gov/docs)

Example request:
```
https://images-api.nasa.gov/search?q=curiosity+rover&media_type=image
```

### NASA APOD (Astronomy Picture of the Day)
- **Base URL:** `https://api.nasa.gov`
- **Endpoint used:** `/planetary/apod`
- **Requires API key:** Yes
- **Documentation:** [api.nasa.gov](https://api.nasa.gov)

Example request:
```
https://api.nasa.gov/planetary/apod?api_key=YOUR_KEY
```

Both APIs are free and publicly available. No payment or special access is required.

---

## Project Structure

```
140mi/
├── main.py              # Flask app — all routes and backend logic
├── database.db          # SQLite database — user accounts
├── api.env              # Your API key (not committed to GitHub)
├── api.env.example      # Template showing what api.env should look like
├── .gitignore           # Files excluded from version control
├── static/
│   ├── index.css        # Styles for the home page
│   ├── rovers.css       # Styles for the rovers/search page
│   └── 140mi-logo.png   # Site logo
└── templates/
    ├── index.html       # Home page
    ├── rovers.html      # Search and photo grid page
    ├── login.html       # Login page
    ├── signup.html      # Registration page
    └── about.html       # About page
```

---

## Full Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| API | NASA Image and Video Library, NASA APOD |
| Auth | Flask sessions |

---

## License

This project is open source. All NASA imagery is in the public domain per [NASA's media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/).
