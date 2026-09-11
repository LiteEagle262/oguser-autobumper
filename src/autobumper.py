import requests
import datetime
import os
import random
import time
import re

from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import seleniumbase.config as sb_config
from seleniumbase import Driver

from bs4 import BeautifulSoup

import pyotp

from config import username, password, secret

class Autobumper(ABC):

    def __init__(self, headless) -> None:
        if not username or not password:
            raise SystemExit('Missing credentials. Set OGU_USERNAME and OGU_PASSWORD env vars.')
        self.main_url = "https://oguser.com/"
        self.username = username
        self.headless = headless
        self.bump_interval = float(os.getenv("BUMP_INTERVAL_HOURS", "2")) * 3600
        if not hasattr(sb_config, 'headless'):
            sb_config.headless = headless
        self.driver = Driver(uc=True, headless=headless)
        self.wait = WebDriverWait(self.driver, 25)

        self.login()
        self.update_post_key()

    def is_driver_alive(self):
        try:
            _ = self.driver.title
            return True
        except Exception:
            return False

    def restart_driver(self):
        try:
            self.driver.quit()
        except Exception:
            pass
        self.driver = Driver(uc=True, headless=self.headless)
        self.wait = WebDriverWait(self.driver, 25)

    @abstractmethod
    def bumper(self):
        pass

    def get_post_key(self):
        self.driver.get(self.main_url + "Thread-RIP-OGFLIP")
        html = self.driver.page_source
        post_key = re.search(r'my_post_key=([a-f0-9]{32})', html).group(1)
        return post_key

    def update_post_key(self):
        post_key = self.get_post_key()
        self.my_post_key = post_key

    def get_tid(self, link):
        if self.driver.current_url != link:
            self.driver.get(link)
        html = self.driver.page_source
        tid = re.search(r'name="tid" value="([^"]+)"', html).group(1)
        return tid

    def get_title(self, link):
        if self.driver.current_url != link:
            self.driver.get(link)
        title_xpath = '/html/body/div[8]/div/div[1]/span'
        title_element = self.wait.until(ec.visibility_of_element_located((By.XPATH, title_xpath)))

        title = self.driver.execute_script(
            "return Array.from(arguments[0].childNodes)"
            ".filter(n => n.nodeType === 3).map(n => n.textContent).join('');",
            title_element
        )
        return title.replace('\xa0', ' ').strip().upper()

    def get_tid_and_title(self, link):
        tid = self.get_tid(link)
        title = self.get_title(link)
        return tid, title

    def is_logged_in(self):
        self.driver.get(self.main_url)
        try:
            short_wait = WebDriverWait(self.driver, 5)
            short_wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="dropdown-profile-mobile"]')))
            return True
        except Exception:
            return False

    def bypass_cloudflare(self):
        for _ in range(12):
            try:
                if 'just a moment' not in (self.driver.title or '').lower():
                    return
                info = self.driver.execute_script("""
                    const el = document.elementFromPoint(innerWidth/2, innerHeight*0.545);
                    const r = el ? el.getBoundingClientRect() : null;
                    return {rect: r ? {x: r.x, y: r.y, w: r.width, h: r.height} : null,
                            innerW: innerWidth, innerH: innerHeight};
                """)
                wr = self.driver.get_window_rect()
                chrome_h = wr['height'] - info['innerH']
                r = info['rect']
                if r and 200 <= r['w'] <= 400 and 40 <= r['h'] <= 100:
                    vx, vy = r['x'] + 22, r['y'] + r['h'] / 2
                else:
                    vx, vy = info['innerW'] / 2 - 130, info['innerH'] * 0.545
                self.driver.uc_gui_click_x_y(wr['x'] + vx, wr['y'] + chrome_h + vy)
            except Exception:
                pass
            time.sleep(5)

    def login(self):
        try:
            self.driver.get('https://google.com')
            time.sleep(3)
            self.driver.get(self.main_url)
            time.sleep(7)
            self.bypass_cloudflare()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.get(self.main_url + 'login')
            time.sleep(5)
            self.bypass_cloudflare()
            self.wait.until(ec.presence_of_element_located((By.NAME, 'username')))
            forms = self.driver.find_elements(By.XPATH, '//form[.//input[@name="2facode"]]')
            if not forms:
                forms = self.driver.find_elements(By.XPATH, '//form[.//input[@name="username"] and .//input[@name="password"]]')
            form = next((f for f in forms if f.is_displayed()), forms[-1])
            form.find_element(By.NAME, 'username').send_keys(username)
            form.find_element(By.NAME, 'password').send_keys(password)
            if secret:
                totp = pyotp.TOTP(secret)
                time_remaining = totp.interval - datetime.datetime.now().timestamp() % totp.interval
                time.sleep(time_remaining + 1)
                form.find_element(By.NAME, '2facode').send_keys(totp.now())
            submit = form.find_elements(By.XPATH, './/input[@type="submit"] | .//button[@type="submit"]')
            if submit:
                submit[0].click()
            else:
                form.submit()
            self.wait.until(lambda d: 'action=logout' in d.page_source
                            or d.find_elements(By.XPATH, '//*[@id="dropdown-profile-mobile"]'))
            print("STATUS: Logged in.")
        except Exception:
            raise Exception('Login failed. Consider running the script with `--headless=False`.')

    def newreply(self, tid, message):
        message = f"{message} {random.randint(10000, 99999)}"
        cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}

        data = {
            "my_post_key": self.my_post_key,
            "subject": 0,
            "action": "do_newreply",
            "posthash": 0,
            "quoted_ids": "",
            "lastpid": 0,
            "from_page": "1",
            "tid": tid,
            "method": "quickreply",
            "message": message,
        }

        response = requests.post(
            f"{self.main_url}/newreply.php?tid={tid}&processed=1",
            data=data,
            cookies=cookies,
            headers={"User-Agent": self.driver.execute_script("return navigator.userAgent")}
        )

        if not response.ok:
            raise Exception(f'Could not send message {message}. Status code {response.status_code}.')

        soup = BeautifulSoup(response.text, "html.parser")
        error_div = soup.find("div", class_="error")

        if error_div:
            error_messages = [li.get_text(strip=True) for li in error_div.find_all("li")]
            error_text = "; ".join(error_messages) if error_messages else error_div.get_text(strip=True)
            raise Exception(f'Forum rejected message "{message}": {error_text}')

        print(f'SENT: {message}')
