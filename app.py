import os
import requests
import random
import uuid
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
# Flask ko messages flash karne ke liye secret key ki zaroorat hoti hai
app.config['SECRET_KEY'] = os.urandom(24)

# Aapke bot ka GitHub repository URL
SOURCE_REPO_URL = "https://github.com/Qadeer-bhai/TOFAN-MD"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # --- Step 1: User se form data lena ---
        session_id = request.form.get('session_id')
        owner_number = request.form.get('owner_number')
        owner_name = request.form.get('owner_name')
        bot_name = request.form.get('bot_name')

        # Check karein ke zaroori fields khali na hon
        if not all([session_id, owner_number, owner_name, bot_name]):
            flash("Error: Tamam zaroori fields fill karna laazmi hai.", "danger")
            return redirect(url_for('index'))

        # --- Step 2: Heroku API Keys ko handle karna ---
        # Environment variable se comma-separated keys ko get karein
        heroku_api_keys_str = os.environ.get('HEROKU_API_KEYS')
        if not heroku_api_keys_str:
            flash("Error: Panel configuration mein Heroku API keys set nahi hain. Admin se rabta karein.", "danger")
            return redirect(url_for('index'))
        
        # Keys ko list mein split karein aur randomly aik select karein
        heroku_keys_list = [key.strip() for key in heroku_api_keys_str.split(',')]
        selected_api_key = random.choice(heroku_keys_list)

        # --- Step 3: Random Heroku App Name generate karna ---
        # 'tofan-md-' ke baad 12 random characters ka naam banayega
        random_suffix = uuid.uuid4().hex[:12]
        app_name = f"tofan-md-{random_suffix}"

        # --- Step 4: Heroku API ke liye payload tayyar karna ---
        # Yeh aapke app.json se li gayi tamam default values hain
        config_vars = {
            "SESSION_ID": session_id,
            "NUMERO_OWNER": owner_number,
            "OWNER_NAME": owner_name,
            "BOT_NAME": bot_name,
            "HEROKU_APP_NAME": app_name,
            "HEROKU_API_KEY": selected_api_key,
            # Neeche di gayi tamam values aapke app.json se li gayi hain
            "PREFIX": ".",
            "AUTO_READ_STATUS": "yes",
            "AUDIO_REPLY": "yes",
            "AUTO_REPLY": "no",
            "AUTO_REACT_STATUS": "yes",
            "AUTO_BIO": "yes",
            "AUTO_SAVE_CONTACTS": "no",
            "AUTO_DOWNLOAD_STATUS": "no",
            "PM_PERMIT": "yes",
            "AUTO_STATUS_TEXT": "viewed ✅✅",
            "AUTO_STATUS_REPLY": "no",
            "ANTI_CALL_TEXT": "My owner don't receive any call now because it's busy",
            "PUBLIC_MODE": "yes",
            "URL": "https://qu.ax/CAJVF.png",
            "AUTO_READ_MESSAGES": "no",
            "WARN_COUNT": "5",
            "STARTING_BOT_MESSAGE": "no",
            "PRESENCE": "1",
            "ANTI_DELETE_MESSAGE": "no",
            "ANTI_CALL": "yes",
            "AUTO_BLOCK": "no",
            "AUTO_REACTION": "no"
        }

        # API call ke liye mukammal payload
        payload = {
            "app": {
                "name": app_name,
                "stack": "container" # Aapke app.json se
            },
            "source_blob": {
                "url": f"{SOURCE_REPO_URL}/tarball/main/",
            },
            "overrides": {
                "config_vars": config_vars
            },
             "addons": [
                {"plan": "heroku-postgresql:essential-0"}
            ]
        }
        
        headers = {
            'Accept': 'application/vnd.heroku+json; version=3.formation',
            'Authorization': f'Bearer {selected_api_key}',
            'Content-Type': 'application/json',
        }

        # --- Step 5: Heroku API ko call karke app deploy karna ---
        try:
            response = requests.post('https://api.heroku.com/app-setups', json=payload, headers=headers)
            response.raise_for_status() # Agar error ho to exception raise karega

            data = response.json()
            success_message = f"🎉 Mubarak ho! Aapka bot deploy hona shuru ho gaya hai. App Name: {data.get('app', {}).get('name')}"
            flash(success_message, "success")
            flash(f"Deployment status check karne ke liye is link par jayen: {data.get('resolved_success_url')}", "info")

        except requests.exceptions.RequestException as e:
            error_message = f"Deployment mein masla aa gaya hai: {e.response.text if e.response else str(e)}"
            flash(error_message, "danger")

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
