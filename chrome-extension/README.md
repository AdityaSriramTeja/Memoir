## Load the Extension in Chrome
1. Open Google Chrome and go to chrome://extensions/.
2. Enable Developer mode (toggle switch in the top right).
3. Click "Load unpacked".
4. Select the "chrome-extension" folder inside your project directory where the manifest.json is stored.
5. Your extension should now be visible in the extensions list.
6. Configure Keyboard shortcuts by in the keyboard shortcuts tab in Manage Extensions

## Troubleshooting
On the manage extensions page you can click on the service worker link to open a console for the extension to keep an eye on debug messages pushed to the console

"Uncaught (in promise) Error: Could not establish connection. Receiving end does not exist."
This error is seen when the content script has not been injected into the website so background.js
cannot establish a connection to the content script. This issue should not exist in production but
since we are loading unpacked and reloading/disrupting the extension this error is seen more often.
To resolve the error just reload the page and the content script should be injected.