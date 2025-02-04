module.exports = {
    apps: [
      {
        name: "sabong-saga-genesis-listings-tracker",
        script: "./main.py",
        interpreter: "./sabungan-venv/bin/python3",
        watch: false,
        autorestart: true
      }
    ]
  };
  