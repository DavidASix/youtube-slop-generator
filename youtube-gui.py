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

YouTube puts a soft 10 video limit per 24 hours for new accounts. To bypass this, you need to upload ID, a video of yourself (lame), or use the account for months.

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
        print(f"\t\tRunning command {action} on {selector}")
        # Returns true if successful and false if not
        successful = self.tab.Runtime.evaluate(expression=script)
        if not successful:
            print(f"Failed to {action} on {selector}")
            exit(1)

    def upload_flow(self):
        # Click the Create button
        print('Opening create dropdown')
        self.dom_action('button.ytcp-button-shape-impl[aria-label="Create"]', 'click()')
        wait(1, 2)
        
        # Click the button to bring up the upload dialog
        print('Opening upload dialog')
        self.dom_action('tp-yt-paper-item[test-id="upload-beta"]', 'click()')
        wait(1, 2)

        # Set the file upload data 
        print('Setting file upload data')
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
        print('Upload successful, waiting for video details to load')
        wait(8, 12)

        # Get the x, y screen location of the element
        element_info = self.tab.DOM.querySelector(
            nodeId=document['root']['nodeId'],
            selector='div#textbox[contenteditable="true"]'
        )
        
        element_box = self.tab.DOM.getBoxModel(nodeId=element_info['nodeId'])
        x, y = element_box['model']['content'][0], element_box['model']['content'][1]
        
        # Get the height of the PC's screen and the browser viewport to calculate the title section height
        # This assumes that the browser is maximized
        screen_height = pyautogui.size().height
        viewport_height = self.tab.Runtime.evaluate(expression="Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)")["result"]["value"]
        title_section_height = screen_height - viewport_height
        
        # Add padding to ensure access of div
        x += 15
        y += title_section_height + 15
        
        print(f"Element location: x={x}, y={y}")
        pyautogui.moveTo(x, y)
        pyautogui.click()

        pyautogui.hotkey('ctrl', 'a')
        for l in 'Hello World!!':
            pyautogui.press(l)
            wait(0.1, 0.2)
        
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
