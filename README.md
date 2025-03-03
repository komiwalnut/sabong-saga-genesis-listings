# sabong-saga-genesis-listings
A script that tracks Sabong Saga Genesis NFT listings on Mavis Market and posts real-time updates to the "💰｜listings" channel.

<img src="images/sample2.png">
<img src="images/sample.png">

# Prerequisites
Ensure you have the following installed on your Linux system:
- Python 3 (Recommended: Python 3.8+)
- pip (Python package manager)
- virtualenv (Install using `pip install virtualenv` if not installed)
- pm2 (Process manager for Node.js, install using `npm install -g pm2`)

# Create Your Sky Mavis API Key
1. Visit the Sky Mavis Developer Console:
   -  Open your browser and navigate to: https://developers.skymavis.com/console/applications/
2. Sign In / Sign Up:
   - If you don’t already have an account, sign up for one.
   - Log in with your credentials.
3. Create a New Application:
   - Once logged in, locate the option to create a new application (often labeled "Create Application" or similar).
   - Fill in the required details (Application Name) for your application.
   - After submitting the form, your application will be created, and you should be provided with an API key.
4. Copy Your API Key

# Setting Up Environment Variables
Create a .env file in the project directory and add the following:
```bash
DISCORD_WEBHOOK_URL=your_webhook_url_here
SM_KEY=your_api_key
```

# Setting Up the Virtual Environment
1. Open a terminal and navigate to the project directory:
   ```bash
   cd Sabungan-listings
   ```
3. Create a virtual environment named sabungan-venv:
   ```bash
   python3 -m venv sabungan-venv
   ```
5. Activate the virtual environment:
   ```bash
   source sabungan-venv/bin/activate
   ```

# Installing Dependencies
Once the virtual environment is activated, install the required dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

# Running the Application with PM2
1. Ensure pm2 is installed globally:
   ```bash
   npm install -g pm2
   ```
2. Start the application using pm2:
   ```bash
   pm2 start ecosystem.config.js
   ```
3. To check the status of the application:
   ```bash
   pm2 list
   ```
4. To restart the application if needed:
   ```bash
   pm2 restart ssg-listings-tracker
   ```
5. To stop the application:
    ```bash
   pm2 stop ssg-listings-tracker
   ```
6. To remove the application from pm2:
   ```bash
   pm2 delete ssg-listings-tracker
   ```
   
# Keeping PM2 Running After Reboot
To ensure pm2 restarts the application after a system reboot:
   ```bash
   pm2 startup
   pm2 save
   ```
