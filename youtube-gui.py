import subprocess
import time
import pychrome
import random
import socket
import pyautogui


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def wait(start=4, end=8):
    time.sleep(random.uniform(start, end))

"""
Selenium, Pyppter, Playwright, all have ot detection in their browser, so you can't use them to upload videos to youtube.

This class uses your installed chromium browser to upload videos
# Pre-requisites
    - Chromium installed
    - Logged into YouTube in Chromium
    
"""
class Uploader:
    def __init__(self):
        # Launch Chromium with remote debugging
        if not is_port_in_use(9222):
            subprocess.Popen(
                ["chromium", "--remote-debugging-port=9222"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(5)
        try:
            self.browser = pychrome.Browser(url="http://127.0.0.1:9222")
        except Exception as e:
            print("Error:", e)
            print("Please make sure Chromium is running with remote debugging enabled")
            exit(1)
        self.tab = self.browser.new_tab()
        self.tab.start()
        self.tab.Page.navigate(url="https://studio.youtube.com")
        # Wait for the page to load
        wait(2,4)
        self.logged_in = (
            "studio.youtube.com"
            in self.tab.Runtime.evaluate(expression="window.location.href")["result"][
                "value"
            ]
        )
        print("Not logged in" if not self.logged_in else "Logged in and set up!")

        self.file_path = "/home/davidasix/Code/youtube-shorts-slop-generator/build/output/d17920ea-4fdf-4125-9ec2-3a47f9c2eb38.mp4"
        self.title = "Test Title"
        self.description = "Test Description"

    def dom_action(self, selector, action):
        script = f"""
            (function() {{
                var element = document.querySelector('{selector}');
                if (element) {{
                    element.{action};
                    return true;
                }} 
                return false;
            }})();
        """
        print('Attempting to run script', script)
        # Returns true if successful and false if not
        successful = self.tab.Runtime.evaluate(expression=script)
        if not successful:
            print(f"Failed to {action} on {selector}")
            exit(1)

    def upload_flow(self):
        # Click the Create button
        self.dom_action('button.ytcp-button-shape-impl[aria-label="Create"]', 'click()')
        wait(1, 2)
        
        # Click the button to bring up the upload dialog
        self.dom_action('tp-yt-paper-item[test-id="upload-beta"]', 'click()')
        wait(1, 2)

        # Set the file upload data 
        self.tab.DOM.enable()
        
        document = self.tab.DOM.getDocument()
        input_node = self.tab.DOM.querySelector(
            nodeId=document['root']['nodeId'],
            selector='input[type="file"][name="Filedata"]'
        )
        
        self.tab.DOM.setFileInputFiles(
            nodeId=input_node['nodeId'],
            files=[self.file_path]
        )
        # This auto brings you to the next step, video detail entry, but it takes a bit.
        wait(8, 12)
        
        # Set the title value./
        self.dom_action('div#textbox[contenteditable="true"]', 'click()')
        pyautogui.write("Hello World", interval=0.1)
        
        # Set the description value
        self.dom_action('div#textbox[aria-label="Tell viewers about your video (type @ to mention a channel)"]', f'innerText = "{self.title}"')
        
    def close_browser(self):
        print("Closing Browser")
        # Kill the chromium instance that (hopefully) we spawned
        subprocess.Popen(
            ["pkill", "-f", "--", "chromium.*--remote-debugging-port=9222"]
        )


uploader = Uploader()
# uploader.wait()
uploader.upload_flow()
# uploader.close_browser()
