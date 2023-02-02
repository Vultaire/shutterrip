"""shutterrip.py: A Shutterfly share sites downloading script.
Copyright (C) 2023 Paul Goins

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import json
import os
import shutil
import tempfile
import time
from urllib.parse import urlparse

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException


MAX_SCRIPT_RETRIES = 10
ELEMENT_FIND_TIMEOUT = 15
NTFS_UNALLOWED_CHARACTERS = '/\:*"?<>|'
CONFIG_PATH = "config.yaml"


def main():
    with open(CONFIG_PATH) as infile:
        config = yaml.safe_load(infile)
    for i in range(MAX_SCRIPT_RETRIES):
        try:
            _main(config)
        except Exception:
            pass
        else:
            break


def _main(config):
    tmpdir = tempfile.mkdtemp()
    try:
        service = Service(executable_path=config["chromedriver_path"])
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {"download.default_directory": tmpdir})
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.maximize_window()
            log_in(driver, config)
            site_links = config["site_links"]
            for site_link in site_links:
                download_site(driver, tmpdir, site_link)
        finally:
            driver.close()
    finally:
        shutil.rmtree(tmpdir)


def download_site(driver, tmpdir, site_link):
    if is_downloaded(site_link):
        print(f"Skipping site: {site_link}")
        return

    print(f"Finding albums in site: {site_link}")
    # Open the site page
    driver.get(site_link)

    # Click to show all (if available)
    click_all_link(driver, type="album")

    # Wait until at least one of these is rendered...
    find_element(driver, "div.pic-album-hdr a.pic-album-title")
    # And give more time for remaining ones to render...
    time.sleep(5)

    # Get all album links
    links = [element.get_attribute("href") for element in
             driver.find_elements(By.CSS_SELECTOR, "div.pic-album-hdr a.pic-album-title")]
    parsed_site_link = urlparse(site_link)
    site_name = sanitize_name(parsed_site_link.netloc + parsed_site_link.path)
    for album_index, album_link in enumerate(links):
        download_album(driver, tmpdir, site_name, album_index, album_link)

    mark_downloaded(site_link)


def download_album(driver, tmpdir, site_name, album_index, album_link):
    if is_downloaded(album_link):
        print(f"Skipping album link: {album_link}")
        return

    # Open the album page
    print(f"Opening album link: {album_link}")
    driver.get(album_link)

    # Get title content
    album_title = find_element(driver, "span.title-text").text
    album_title = sanitize_name(f'[{album_index+1}]_{album_title}')
    print("Album name:", album_title)

    # Is it empty?  If so, ignore.
    try:
        find_element(driver, "img.pic-img", timeout=5)
    except TimeoutException:
        print(f'Album is empty; skipping')
        mark_downloaded(album_link)
        return

    # Is there an "all" option?  If so, click it.
    click_all_link(driver, type="picture")

    # Wait until at least one of these is rendered...
    find_element(driver, "a:has(img.pic-img)")
    # And give more time for remaining ones to render...
    time.sleep(5)

    # Get all picture page links
    links = [element.get_attribute("href") for element in
             driver.find_elements(By.CSS_SELECTOR, "a:has(img.pic-img)")]

    for picture_index, picture_link in enumerate(links):
        download_picture(driver, tmpdir, site_name, album_title, picture_index, picture_link)

    mark_downloaded(album_link)


def download_picture(driver, tmpdir, site_name, album_title, picture_index, picture_link):
    if is_downloaded(picture_link):
        print(f"Skipping picture link: {picture_link}")
        return

    # Open the album page
    print(f"Opening picture link: {picture_link}")
    driver.get(picture_link)

    # Pull important metadata
    metadata = find_element(driver, "div.pic-img-text.detail-footer-bottom").text
    file_name = f'[{picture_index+1}]_{sanitize_name(metadata)}.jpg'

    click_download_menu(driver)
    wait_for_download(tmpdir)
    move_downloaded_file(tmpdir, site_name, album_title, file_name)

    mark_downloaded(picture_link)


def click_download_menu(driver):
    # Download the picture to the temp dir
    e = find_element(driver, 'img.detail-img', timeout=5)
    ActionChains(driver).move_to_element(e).context_click(e).perform()
    e = find_element(driver, 'div.i-download', timeout=5)
    ActionChains(driver).move_to_element(e).click(e).perform()


def wait_for_download(tmpdir, timeout=30):
    start_ts = time.time()
    while time.time() < start_ts + 30:
        files = os.listdir(tmpdir)
        if files and any(files[0].lower().endswith(ext) for ext in ('.jpg', '.jpeg')):
            break
        time.sleep(0.1)
    else:
        raise RuntimeError('Download timeout exceeded')

    # Sometimes the files are blank...
    # We'll do a hard-coded 5 second wait for each one.  (i.e. try to do this overnight.)
    time.sleep(5)


def move_downloaded_file(tmpdir, site_name, album_title, file_name):
    # Rename and move the picture to the intended target dir
    tmp_filename = os.path.join(tmpdir, os.listdir(tmpdir)[0])
    dst_filename = os.path.join(os.getcwd(), site_name, album_title, file_name)

    os.makedirs(os.path.dirname(dst_filename), exist_ok=True)
    if os.path.exists(dst_filename):
        os.unlink(dst_filename)
    os.rename(tmp_filename, dst_filename)

    # THINK ABOUT: Writing a metadata file.
    # Hopefully not needed...


def sanitize_name(name):
    for c in NTFS_UNALLOWED_CHARACTERS:
        name = name.replace(c, '_')
    return name


def mark_downloaded(link):
    state = load_state()
    state[link] = True
    write_state(state)


def is_downloaded(link):
    return link in load_state()


def load_state():
    state = {}
    if os.path.exists('.state'):
        with open('.state') as infile:
            state = json.load(infile)
    return state


def write_state(state):
    with open('.state', 'w') as outfile:
        json.dump(state, outfile)


def log_in(driver, config):
    driver.get("https://accounts.shutterfly.com/")
    send_keys(driver, "input#email", config["email"])
    send_keys(driver, "input#password", config["password"])
    click(driver, "button#signInButton")
    find_element(driver, "span.title", timeout=10)
    print("Logged in")



def find_element(driver, selector, timeout=ELEMENT_FIND_TIMEOUT):
    return WebDriverWait(driver, timeout=timeout).until(lambda d: d.find_element(By.CSS_SELECTOR, selector))


def send_keys(driver, selector, keys, timeout=ELEMENT_FIND_TIMEOUT):
    find_element(driver, selector, timeout=timeout).send_keys(keys)


def click(driver, selector, timeout=ELEMENT_FIND_TIMEOUT):
    find_element(driver, selector, timeout=timeout).click()


def click_all_link(driver, type):
    try:
        click(driver, f'div.pic-controls div.navbar-right a[aria-label="Show all {type} per page"]', timeout=5)
    except TimeoutException:
        pass


if __name__ == "__main__":
    main()
