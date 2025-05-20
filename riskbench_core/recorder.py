# riskbench_core/recorder.py

import time
import json
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.events import (
    AbstractEventListener,
    EventFiringWebDriver,
)
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Any


class ActionListener(AbstractEventListener):
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self._step = 0

    def _record(self, action: str, data: Dict[str, Any]):
        entry = {
            "step": self._step,
            "timestamp": time.time(),
            "action": action,
            **data,
        }
        self.events.append(entry)
        self._step += 1

    def before_navigate_to(self, url: str, driver: Chrome):
        self._record("navigate", {"url": url})

    def before_click(self, element: WebElement, driver: Chrome):
        selector = element.get_attribute("outerHTML")
        self._record("click", {"selector": selector})

    def before_change_value_of(self, element: WebElement, driver: Chrome):
        selector = element.get_attribute("outerHTML")
        self._record("type", {"selector": selector, "value": element.get_attribute("value")})


def record_session(start_url: str, out_path: str, headless: bool = False, timeout: int = 300):
    """
    Launches a browser, records user actions (navigate, click, type),
    and writes to out_path in JSONL format when the browser closes or timeout expires.
    """
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    driver = Chrome(options=options)
    listener = ActionListener()
    ef_driver = EventFiringWebDriver(driver, listener)

    try:
        ef_driver.get(start_url)
        # keep the session alive until window is closed or timeout
        start = time.time()
        while True:
            if time.time() - start > timeout:
                break
            if not ef_driver.window_handles:
                break
            time.sleep(0.5)
    finally:
        ef_driver.quit()

    # dump events to JSONL
    with open(out_path, "w", encoding="utf-8") as f:
        for event in listener.events:
            f.write(json.dumps(event) + "\n")
