from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
import time

from process_image import process_image

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
driver = webdriver.Chrome()

driver.get("https://www.apple.com/store")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "body")))

# Note: added box shadow to inside, since borders get clipped by overflow
js_script = """
var elements = document.querySelectorAll('a, button');
for (var i = 0; i < elements.length; i++) {
    elements[i].style.boxShadow = '0px 0px 0px 2px red inset';
}
"""

driver.execute_script(js_script)

js_script_visible = """
return Array.from(document.querySelectorAll('a, button')).filter(function(el) {
    var rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}).map(function(el) {
    var rect = el.getBoundingClientRect();
    return {
        element: el,
        boundingBox: {
            top: rect.top,
            left: rect.left,
            bottom: rect.bottom,
            right: rect.right,
            width: rect.width,
            height: rect.height
        }
    };
});
"""

visible_clickable_elements = driver.execute_script(js_script_visible)

element_count = 0
false_positives = 0

actual_elements = []

for element_data in visible_clickable_elements:
    element = element_data['element']
    bounding_box = element_data['boundingBox']

    element_type = element.tag_name
    element_text = element.text.strip(
    ) if element.text.strip() else "[No visible text]"
    element_href = element.get_attribute(
        'href') if element_type == 'a' else "[Not applicable]"

    if not all(value == 0 for value in bounding_box.values()) and element_text != "[No visible text]":
        element_count += 1

        # print(f"Visible Element {element_count}:")
        # print(f"  Type: {element_type}")
        # print(f"  Text: {element_text}")
        # print(f"  Link: {element_href}")
        # print(f"  Bounding Box:")
        # print(f"    Top: {bounding_box['top']:.2f}")
        # print(f"    Left: {bounding_box['left']:.2f}")
        # print(f"    Bottom: {bounding_box['bottom']:.2f}")
        # print(f"    Right: {bounding_box['right']:.2f}")
        # print(f"    Width: {bounding_box['width']:.2f}")
        # print(f"    Height: {bounding_box['height']:.2f}")
        # print()

        actual_elements.append({
            "index": element_count,
            "type": element_type,
            "text": element_text,
            "link": element_href,
            "bounding_box": bounding_box
        })

    else:
        false_positives += 1

print(f"Actual Elements: {len(actual_elements)}")
print(f"False Positives: {false_positives}")

# Add red text labels for each actual element
for element in actual_elements:
    index = element['index']
    bounding_box = element['bounding_box']

    # JavaScript to add the label
    js_add_label = f"""
    (function() {{
        var label = document.createElement('div');
        label.textContent = '{index}';
        label.style.position = 'fixed';
        label.style.left = '{bounding_box["left"] - 20}px';
        label.style.top = '{bounding_box["top"]}px';
        label.style.color = 'red';
        label.style.fontWeight = 'bold';
        label.style.fontSize = '12px';
        label.style.zIndex = '10000';
        document.body.appendChild(label);
    }})();
    """

    # Execute the JavaScript to add the label
    driver.execute_script(js_add_label)

# Allow time for labels to be added before taking the screenshot
time.sleep(1)


timestamp = datetime.now().timestamp()
screenshot_filename = f"screenshot_{timestamp}.png"
screenshot_path = os.path.join("screenshots", screenshot_filename)
os.makedirs("screenshots", exist_ok=True)
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved as: {screenshot_path}")


# description = process_image(client, screenshot_path)

# print(description)

input("Enter to close")

driver.quit()
