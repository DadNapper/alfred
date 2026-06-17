module.exports = {
  apps: [
    {
      name: "hermes",
      cwd: "/home/alfred/.hermes/hermes-agent",
      script: "/home/alfred/.hermes/hermes-agent/venv/bin/python",
      args: "-m hermes_cli.main gateway run --replace",
      interpreter: "none",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      kill_timeout: 210000,
      out_file: "/home/alfred/maintenance/logs/pm2-hermes-out.log",
      error_file: "/home/alfred/maintenance/logs/pm2-hermes-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      env: {
        HOME: "/home/alfred",
        USER: "alfred",
        LOGNAME: "alfred",
        HERMES_HOME: "/home/alfred/.hermes",
        VIRTUAL_ENV: "/home/alfred/.hermes/hermes-agent/venv",
        PATH: "/home/alfred/.hermes/hermes-agent/venv/bin:/home/alfred/.hermes/hermes-agent/node_modules/.bin:/home/alfred/.hermes/node/bin:/home/alfred/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      }
    }
  ]
};
