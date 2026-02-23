/**
 * Custom preload script to prevent students in exam mode from opening an assignment
 * in multiple tabs or windows. If a notebook is already open in another tab or window,
 * an alert message will be shown and the current tab/window will be redirected to a blank page.
 * It does also prevent unintentional navigation to different pages via links or forwards- / back-buttons.
 */

console.log("Custom preload script for exam mode loaded!");

const ALERT_MESSAGE = 'This notebook is already open in another tab or window!\nGo there and save us all a lot of trouble!';

window.addEventListener('beforeunload', event => event.preventDefault()); //catch unintentional navigation to different pages

if (window.location.href.endsWith(".ipynb")) {
    initializeBroadcastChannel();
}

function initializeBroadcastChannel() {
    const channel = new BroadcastChannel(window.location.href);
    let isOriginal = true;

    // Notify other tabs that this tab is open
    channel.postMessage('another-tab');

    // Listen for messages from other tabs
    channel.addEventListener('message', (msg) => {
        handleBroadcastMessage(msg, channel, isOriginal);
    });
}

function handleBroadcastMessage(msg, channel, isOriginal) {
    if (msg.data === 'another-tab' && isOriginal) {
        // Notify new tabs that the website is already open
        channel.postMessage('already-open');
    }

    if (msg.data === 'already-open') {
        isOriginal = false;
        // Alert the user and redirect to a blank page
        alert(ALERT_MESSAGE);
        window.location = "about:blank";
    }
}
