# Urlwatch Hooks

Custom hooks for [urlwatch](https://github.com/LowieHuyghe/urlwatch).

Featured hooks:
* Reporters
  - `custom-slack`: Improved output for Slack
  - `custom-stdout`: Improved output for stdout
* Filters
  - `ah`: Custom filter for Albert Heijn pages


## Installation

```bash
cd /YOUR/PROJECTS/FOLDER
git clone git@github.com:LowieHuyghe/urlwatch-hooks.git
cd urlwatch-hooks
python3 -m virtualenv venv
./venv/bin/pip install -r requirements.txt
```

Add the bin-folder to your bash/zsh-profile to start using urlwatch

```bash
export PATH="$PATH:/YOUR/PROJECTS/FOLDER/urlwatch-hooks/bin"
```

## Usage

```bash
urlwatch --urls "/PATH/TO/YOUR/urls.yaml" --config "/PATH/TO/YOUR/config.yaml"
```

See [urlwatch-documentation](https://github.com/LowieHuyghe/urlwatch).

### Example urls.yaml

```yaml
name: "AH - Afwasmiddel"
kind: "browser"
navigate: "https://www.ah.be/producten/huishouden-huisdier/vaatwas-afwasmiddel/afwasmiddel/bonus"
filter: ah
max_tries: 5
options:
  waitUntil: networkidle0
---
name: "AH - Vaatwastabletten - Dreft"
kind: "browser"
navigate: "https://www.ah.be/producten/huishouden-huisdier/vaatwas-afwasmiddel/vaatwas/vaatwas-tabletten/merk=Dreft/bonus"
filter: ah
max_tries: 5
options:
  waitUntil: networkidle0
---
name: "AH - Wasverzachter - Silan"
kind: "browser"
navigate: "https://www.ah.be/producten/huishouden-huisdier/wasmiddelen-wasverzachters/wasverzachters/wasverzachters-geconcentreerd/merk=Silan/bonus"
filter: ah
max_tries: 5
options:
  waitUntil: networkidle0
```

### Example config.yaml

```yaml
display:
  error: true
  new: true
  unchanged: false
job_defaults:
  all: {}
  browser: {}
  shell: {}
  url: {}
report:
  html:
    diff: unified
  custom-slack:
    enabled: true
    webhook_url: 'https://hooks.slack.com/services/YOUR/SLACK/HOOK'
  stdout:
    enabled: false
  custom-stdout:
    color: true
    enabled: true
  text:
    details: true
    footer: false
    line_length: 75
    minimal: false
```
