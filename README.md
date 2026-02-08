# Deye Solar Dashboard

A web dashboard for monitoring Deye solar inverters in real-time. Displays solar production, battery status, grid power, home consumption, weather conditions, and power outage schedules.

![Dashboard Preview](docs/preview.png)

## Features

- **Real-time monitoring** — solar production, battery SOC, grid power, and load consumption
- **3-phase load analytics** — per-phase power distribution with daily statistics
- **Weather** — current conditions and forecast via Open-Meteo API
- **Outage schedule** — upcoming power outage windows (Lvivoblenergo or Yasno providers)
- **Grid outage detection** — voice alerts and browser notifications when power goes out
- **Outage history** — track and review past power outages
- **Telegram bot** — battery reports, inverter status, and Ukrainian weather poems
- **Fullscreen mode** — kiosk-friendly display with weather, grid, and battery banners
- **Responsive design** — works on desktop and mobile

## Requirements

- Python 3.7+
- Deye inverter with Solarman Wi-Fi logger
- Network access to the inverter

## Quick Start

```bash
git clone https://github.com/ivanursul/deye-dashboard.git
cd deye-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from the example and fill in your values:

```bash
cp .env.example .env
# Edit .env with your inverter IP, logger serial, etc.
```

Run the dashboard:

```bash
python app.py
```

Open http://localhost:8080 in your browser.

## Configuration

All configuration is done via environment variables, typically set in a `.env` file. See `.env.example` for a complete template.

### Inverter (required)

| Variable | Description | Example |
|----------|-------------|---------|
| `INVERTER_IP` | IP address of your Deye inverter on the local network | `192.168.1.100` |
| `LOGGER_SERIAL` | Serial number of the Solarman Wi-Fi logger (printed on the stick or found in the Solarman app) | `1234567890` |

### Inverter Capabilities (optional)

These are auto-detected at startup. Set them only if auto-detection doesn't work for your model.

| Variable | Description | Default |
|----------|-------------|---------|
| `INVERTER_PHASES` | Number of phases (`1` or `3`) | auto-detected |
| `INVERTER_HAS_BATTERY` | Whether a battery is connected (`true` / `false`) | auto-detected |
| `INVERTER_PV_STRINGS` | Number of PV strings (`1` or `2`) | auto-detected |

### Weather

| Variable | Description | Default |
|----------|-------------|---------|
| `WEATHER_LATITUDE` | Latitude for weather forecast | `50.4501` |
| `WEATHER_LONGITUDE` | Longitude for weather forecast | `30.5234` |

Coordinates are used to fetch weather data from the [Open-Meteo API](https://open-meteo.com/). Find your coordinates on [latlong.net](https://www.latlong.net/).

### Outage Schedule

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTAGE_PROVIDER` | Provider name: `lvivoblenergo`, `yasno`, or `none` | `none` |
| `OUTAGE_GROUP` | Your outage queue/group number (e.g. `1.1`, `2.2`) | — |

**Yasno-specific settings** (only when `OUTAGE_PROVIDER=yasno`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTAGE_REGION_ID` | Yasno region ID (e.g. `25` for Kyiv) | — |
| `OUTAGE_DSO_ID` | Yasno DSO ID (e.g. `902` for DTEK Kyiv) | — |

### Telegram Bot (optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_ENABLED` | Enable the Telegram bot (`true` / `false`) | `false` |
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) | — |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated list of allowed Telegram user IDs | — |

### Data Files (optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTAGE_HISTORY_FILE` | Path to outage history JSON file | `outage_history.json` |
| `PHASE_STATS_FILE` | Path to phase statistics JSON file | `phase_stats.json` |
| `PHASE_HISTORY_FILE` | Path to phase history JSON file | `phase_history.json` |

### Deployment (used by `deploy.sh`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DEPLOY_HOST` | Remote server IP or hostname | `192.168.1.50` |
| `DEPLOY_USER` | SSH user on the remote server | `pi` |
| `DEPLOY_DIR` | Installation directory on the remote server | `/home/pi/deye-dashboard` |
| `DEPLOY_SERVICE_NAME` | Systemd service name | `deye-dashboard` |

## Local Development

Use `deploy_local.sh` to run the dashboard locally with Telegram bot disabled:

```bash
chmod +x deploy_local.sh
./deploy_local.sh
```

This sources your `.env`, disables the Telegram bot, activates the virtual environment, and starts the app.

## Deploying to a Remote Server

`deploy.sh` deploys the dashboard to a remote Linux server over SSH and sets it up as a systemd service.

### First-time deploy

If no `.env` file exists, the script runs an interactive setup wizard that prompts for all settings and generates `.env` for you:

```bash
chmod +x deploy.sh
./deploy.sh
```

You'll be prompted for:
1. Inverter IP and logger serial
2. Remote server connection details (host, user, directory)
3. Weather coordinates
4. Outage schedule provider and group
5. Telegram bot configuration

After answering all prompts, the script writes `.env`, shows a summary, and asks for confirmation before deploying.

### Subsequent deploys

When `.env` already exists, the script skips all prompts and deploys immediately:

```bash
./deploy.sh
```

### What the deploy script does

1. Copies application files to the remote server via `rsync`
2. Creates a Python virtual environment and installs dependencies
3. Creates and enables a systemd service
4. Restarts the service

### Managing the remote service

```bash
# Check status
ssh user@host 'sudo systemctl status deye-dashboard'

# View live logs
ssh user@host 'sudo journalctl -u deye-dashboard -f'

# Restart
ssh user@host 'sudo systemctl restart deye-dashboard'
```

## Finding Your Inverter Details

### Inverter IP

Check your router's connected devices list or scan your network:

```bash
nmap -sP 192.168.1.0/24
```

### Logger Serial Number

The serial number is printed on the Solarman Wi-Fi logger stick, or can be found in the Solarman app under device settings.

## Utility Scripts

```bash
# Test inverter connection
python test_connection.py

# Scan for battery voltage register
python scan_battery.py

# Scan for phase-related registers
python scan_phases.py

# Scan all available registers
python scan_registers.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data` | GET | Current inverter readings |
| `/api/weather` | GET | Current weather and forecast |
| `/api/outage_schedule` | GET | Upcoming outage windows |
| `/api/phase-stats` | GET | Daily phase statistics |
| `/api/phase-history` | GET | Phase power history |
| `/api/outages` | GET | Outage history |
| `/api/outages` | POST | Record outage event |
| `/api/outages/clear` | POST | Clear outage history |
| `/api/phase-stats/clear` | POST | Clear phase statistics |

## License

MIT License
