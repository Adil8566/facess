# Deploy Face Tracking Mode to Render

## Files required at repository root
- `web_app.py`
- `requirements.txt`
- `.python-version`
- `haarcascade_frontalface_default.xml`
- `haarcascade_eye.xml`
- `templates/index.html`
- `static/app.js`
- `static/style.css`

The repository also includes `render.yaml` for Render Blueprint deployment.

## Deploy with Render Dashboard
1. Push the contents of this project folder to a GitHub repository. Put the project files directly at the repository root (do not leave them inside an extra nested folder).
2. In Render, select **New + > Web Service** and connect the GitHub repository.
3. Set:
   - Runtime / Language: Python 3
   - Branch: `main` (or the branch you uploaded)
   - Root Directory: leave blank when the project files are at repository root
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT web_app:app`
   - Instance Type: Free (for testing)
4. Create the Web Service and wait for the deploy logs to show that the service is live.
5. Open the generated `https://<service-name>.onrender.com` URL.
6. On an Android/iPhone browser, allow camera permission when asked and tap Start Camera.

## Important
- The camera is accessed by the browser on the user's phone. The server receives small frames for OpenCV analysis; the phone's live preview is displayed locally in the browser.
- Use the HTTPS `onrender.com` URL so the browser can request camera permission.
- Free Render services can sleep after 15 minutes without inbound traffic and may take about a minute to wake up. The free plan has limited CPU/RAM and is suitable for demos, not guaranteed smooth real-time analysis.
- Files written to the service's local filesystem are ephemeral on the free plan. Do not use it for permanent user uploads or database storage.
- The local `run_web.bat` file is for Windows testing only; Render uses the Start Command above.
