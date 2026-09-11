# OGU Bumper (Working  09/2026)
A lightweight Autobumper and Awardfarmer (Events) for [oguser.com](https://oguser.com) written in Python with Selenium. It offers three [modes](#modes) to bump threads via profile, a link list, or an event thread. Since its latest release, OGU Bumper supports logging in with 2FA enabled.

## Preview:

![preview image](images/preview.png)

## Modes:
[1] Bumps all threads from 'Market' section on user profile with 2 hour interval.  
[2] Bumps all threads by links (env `THREAD_URLS` or [threads.txt](threads.txt)) every 2 hours.  
[3] Spams random messages in thread by input link. Useful for farming awards during events.  

## Docker (recommended)

Everything is configured through environment variables — no files to edit:

```bash
cp .env.example .env   # fill in your credentials + threads
docker compose up -d --build
```

| Env var | Description |
|---|---|
| `OGU_USERNAME` | Account username |
| `OGU_PASSWORD` | Account password |
| `OGU_2FA_SECRET` | Base32 TOTP secret, only if 2FA is enabled |
| `MODE` | `1` = profile threads, `2` = `THREAD_URLS` list, `3` = award farmer |
| `THREAD_URLS` | Comma-separated thread links for mode 2 |
| `THREAD` | Single thread link for mode 3 |
| `BUMP_INTERVAL_HOURS` | Hours between bump cycles (default `2`) |
| `HEADLESS` | `true`/`false` (default `true`) |

## Requirements (manual run)
To install and run the Autobumper you will need [Git](https://git-scm.com/downloads), [Python](https://www.python.org/downloads/) and [Google Chrome](https://www.google.com/chrome/).

## Setup:

### Unix (Linux / macOS)
```bash
git clone https://github.com/EdlZitrone/oguser-autobumper.git
cd oguser-autobumper

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Windows
```bat
git clone https://github.com/EdlZitrone/oguser-autobumper.git
cd oguser-autobumper

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

Set `OGU_USERNAME` and `OGU_PASSWORD` in your environment (or a `.env` file).  
If you have 2FA enabled also set `OGU_2FA_SECRET`, which was shown when initialising the 2FA.  
To see the 2FA secret you might have to reset your 2FA and it will show below the QR code.  
In case you want to use the Autobumper by links, set `MODE=2` and put the urls in `THREAD_URLS` (comma-separated) or [threads.txt](threads.txt).

Run the following command inside the `oguser-autobumper` directory:

**Unix (Linux / macOS):**
```
python3 main.py
```

**Windows:**
```
python main.py
```

## Help

Please leave a star on the repository if it is useful to you.  
If you need any help with the script feel free to reach out.  
Discord: [edlzitrone](https://discord.com/users/565016982768844800)    -    Telegram: [beamertaken](https://t.me/beamertaken) - OGU: [mf](https://oguser.com/mf)
