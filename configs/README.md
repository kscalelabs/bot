# Configs

Defines the configuration files for the project.

## Usage

To build a single config file, run:

```bash
python configs/build.py <local/dev/prod>
```

## Environment Variables

The following environment variables are required to build the config files:

```bash
GOOGLE_CLIENT_ID="your google client id"
SMTP_HOST="your smtp host"
SMTP_EMAIL="your smtp email"
SMTP_PASSWORD="your smtp password"
```

Additionally, the following environment variables are required when building the production config file:

```bash
HF_HUB_TOKEN="your huggingface hub token"
SITE_HOMEPAGE="site homepage url"
SITE_BACKEND="site backend url"
<DEV/PROD>_DB_WRITE_HOST="your db write host"
<DEV/PROD>_DB_READ_HOST="your db read host"
<DEV/PROD>_DB_USERNAME="your db username"
<DEV/PROD>_DB_PASSWORD="your db password"
```

When developing locally, you should set the following environment variables:

```bash
DATA_DIR="path to your data directory"
```
