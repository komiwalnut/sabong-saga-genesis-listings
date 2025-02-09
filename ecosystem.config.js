module.exports = {
    apps: [
      {
        name: "ssg-listings-tracker",
        script: "./main.py",
        interpreter: "./sabungan-venv/bin/python3",
        watch: false,
        autorestart: true
      }
    ]
  };
  
