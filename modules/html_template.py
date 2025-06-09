# HTML templates
SUCCESS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Wi-Fi Connected</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #2ecc71, #27ae60); padding: 20px; }
        .container { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); max-width: 400px; width: 100%; text-align: center; }
        h1 { color: #333; margin-bottom: 1.5rem; }
        .ip-address { background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0; color: #2c3e50; font-size: 1.1rem; word-break: break-all; }
        .status { color: #666; font-size: 0.9rem; margin-top: 1rem; }
        .link { margin-top: 1rem; display: block; color: #2c3e50; text-decoration: none; padding: 0.5rem; border-radius: 5px; transition: background 0.3s; }
        .link:hover { background: #f0f0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wi-Fi Connected!</h1>
        <div class="ip-address">IP Address: {{ ip_address }}</div>
        <div class="status">Your Pico W is now connected to the network</div>
        <a href="/status" class="link">Check System Status</a>
        <a href="/config" class="link">Change Wi-Fi Configuration</a>
        <a href="/control" class="link">Control Dash Board</a>
    </div>
</body>
</html>"""

CONFIG_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Wi-Fi Setup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; }
        .container { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); max-width: 400px; width: 100%; }
        h1 { color: #333; text-align: center; margin-bottom: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #555; }
        input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 0.8rem; background: #667eea; border: none; border-radius: 5px; color: white; font-size: 1rem; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #764ba2; }
        .status { text-align: center; margin-top: 1rem; color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wi-Fi Setup</h1>
        <form method="POST" action="/config">
            <div class="form-group">
                <label for="ssid">Wi-Fi Name (SSID)</label>
                <input type="text" list="ssid-list" id="ssid" name="ssid" required>
                <datalist id="ssid-list">
                    {{ ssid }}
                </datalist>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Save and Connect</button>
            
        </form>
        <div class="status">{{ status_message }}
        <a href="/control" class="link">Control Dash Board</a>
        </div>
    </div>
</body>
</html>"""

STATUS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Status</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #3498db, #2980b9); padding: 20px; }
        .container { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); max-width: 400px; width: 100%; text-align: center; }
        h1 { color: #333; margin-bottom: 1.5rem; }
        .info { background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0; color: #2c3e50; font-size: 1.1rem; word-break: break-all; }
        .link { margin-top: 1rem; display: block; color: #2c3e50; text-decoration: none; padding: 0.5rem; border-radius: 5px; transition: background 0.3s; }
        .link:hover { background: #f0f0f0; }
        button { width: 100%; padding: 0.8rem; background: #667eea; border: none; border-radius: 5px; color: white; font-size: 1rem; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #764ba2; }
        fieldset{border-radius:10px;.link{margin-top:0;cursor:pointer;}}
        legend{padding-left:10px;padding-right:10px;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Device Status</h1>
        <div class="info">IP Address: {{ ip_address }}</div>
        <div class="info">Wi-Fi SSID: {{ ssid }}</div>
        <div class="info">Connection Status: {{ status }}</div>
        <div class="info">Connection Status: {{ status }}</div>
        <div id="update-status" class="info">
            <button id="check-update">Check Update</button>
            <div id="update-info" style="cursor:pointer;">{{ version }}</div>
        </div>
        <a href="/" class="link">Back to Home</a>
        <a href="/config" class="link">Change Wi-Fi Configuration</a>
        <a href="/control" class="link">Control Dash Board</a>
        <fieldset>
            <legend>Advance Setting</legend>
            <div class="link" id="reset" >Reset Device</div>
            <div class="link" id="no_auto_run" >No Auto Run Next Reboot</div>
        </fieldset>
    </div>
    <script>
    document.querySelector('#check-update').addEventListener('click', (e) => {
        e.preventDefault();
        fetch('/system?action=check_update', { method: 'GET' })
            .then(response=>response.text())
            .then(text=>{
            document.querySelector('#update-info').innerHTML=text;
            })
    });
    
    document.querySelector('#reset').addEventListener('click', (e) => {
        e.preventDefault();
        let userInput = prompt('Please type "RESET" to update the machine');
        
        if (userInput!=='RESET') return;
        
        fetch('/system?action=reset', { method: 'GET' })
            .then(response=>response.text())
            .then(text=>{
                alert('Machine will be reset shortly')
            })
    });
    
    document.querySelector('#no_auto_run').addEventListener('click', (e) => {
        e.preventDefault();
        let userInput = prompt('The machine will not auto run next time, and it will only be accessible via USB cable. Please type "NO AUTO" to continue.');
        
        if (userInput!=='NO AUTO') return;
        
        fetch('/system?action=no_auto_run', { method: 'GET' })
            .then(response=>response.text())
            .then(text=>{
                alert('Machine will not auto run next time.')
            })
    });
    
    document.querySelector('#update-info').addEventListener('click', (e) => {
        let force_update='';
        if (document.querySelector('#update-info').innerText.includes('No new')){
            force_update='FORCE';
        }
        let userInput = prompt(`Please type "UPDATE" to ${force_update} update the machine`);
        
        if (userInput=="UPDATE"){
            fetch('/system?action=to_be_updated', { method: 'GET' })
                .then(response=>response.text())
                .then(text=>{
                    console.log(text);
                    fetch('/system?action=reset', { method: 'GET' })
                        .then(response=>response.text())
                        .then(text=>{
                            console.log('Machine will be reset.');
                        })
                })
            
        }else{
            alert('Machine will not be updated')
        };
    });
    </script>
</body>
</html>"""

CONTROL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Wi-Fi Setup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #f6a821, #f97316); padding: 20px; }
        .container { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); max-width: 400px; width: 100%; }
        h1 { color: #333; text-align: center; margin-bottom: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #555; }
        input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 0.8rem; background: #667eea; border: none; border-radius: 5px; color: white; font-size: 1rem; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #764ba2; }
        .status { text-align: center; margin-top: 1rem; color: #666; font-size: 0.9rem; }
        .link { text-align: center; margin-top: 1rem; display: block; color: #2c3e50; text-decoration: none; padding: 0.5rem; border-radius: 5px; transition: background 0.3s; }
        .link:hover { background: #f0f0f0; }
        .status { text-align: center; margin-top: 1rem; color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Control Dashboard</h1>
        <form method="POST" action="/config">
            <div class="form-group">
                <button id="activate" name="activate">Activate Led Gradient</button>
                <div id="activate-status" style="position:relative;" class="status">
                </div>
            </div>
        </form>
        <a href="/" class="link">Back to Home</a>
        <a href="/config" class="link">Change Wi-Fi Configuration</a>
        <a href="/status" class="link">Check System Status</a>
    </div>
    
    <script>
        let intervalId = null;
        document.querySelector('#activate').addEventListener('click', (e) => {
            e.preventDefault();
            fetch('/control', { method: 'POST' })
                .then(response => response.text())
                .then(text => {
                    document.getElementById('activate-status').innerText = 'Status: ' + text;
                    if (text.includes('started')){
                        if (intervalId === null) {
                            intervalId = setInterval(() => {
                                fetch('/control?attribute=current_rgb')
                                    .then(response => response.text())
                                    .then(text => {
                                        document.getElementById('activate-status').innerHTML=`
                                        ${document.getElementById('activate-status').innerText}
                                        <span id="current-rgb" style="position:absolute;width:25px;height:25px;right:30px; background-color: ${text};"></span>
                                        `;
                                    })
                                    .catch(error => {
                                        console.error('Error:', error);
                                        document.getElementById('activate-status').innerText = 'Status: Error occurred';
                                        clearInterval(intervalId);
                                        intervalId = null;
                                    });
                            }, 4000);
                        }
                    }else{
                        if (intervalId !== null) {
                            clearInterval(intervalId);
                            intervalId = null;
                            document.getElementById('activate-status').innerText = 'Status: Stopped checking';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('activate-status').innerText = 'Status: Error occurred';
                });
        });
    </script>
</body>
</html>"""
