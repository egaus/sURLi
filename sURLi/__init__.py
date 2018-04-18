#! /usr/bin/env python

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import os
import urllib
import codecs
import argparse
from subprocess import call
import datetime
import hashlib
import shutil
import time
import json

class sURLi:
    def __init__(self, temp_dir='./temp_results', output_dir='./results', useragent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0'):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        ensure_directory(self.output_dir)
        ensure_directory(self.temp_dir)

        print("Invoking Firefox webdriver")
        window_size = '1920,1080'
        options = Options()
        options.add_argument("--headless")
        options.add_argument("user-agent={}".format(useragent))
        options.add_argument("--window-size={}".format(window_size))
        self.driver = webdriver.Firefox(firefox_options=options)
        #self.driver.wait = WebDriverWait(self.driver, 5)


    def get_url_contents(self, url, tag=None, timeout_seconds=60, images=False):
        '''
        Retrieves content from URL, zips content and stores in self.output_dir, uses self.temp_dir to stage intermediate
        results.
        :param url: URL of the website to get
        :param tag: optional tag to include in the saved results directory path
        :param timeout_seconds: max time to spend requesting the url
        :param images: boolean value, specifying whether or not to download page images
        :return: Nothing, all results and logs saved to self.output_dir
        '''
        print("\nRetrieving contents of url {}".format(url))
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join(self.output_dir, date_str)
        ensure_directory(output_dir)
        log = {'original_url' : url}
        log['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Set timeouts
        self.driver.implicitly_wait(timeout_seconds)
        self.driver.set_page_load_timeout(timeout_seconds)
        self.driver.set_script_timeout(timeout_seconds)

        url_md5_str = hashlib.md5(url.encode('utf-8')).hexdigest()

        try:
            # Get URL
            now = time.time()
            self.driver.get(url)

            # Content of page and hash of content
            page = self.driver.page_source
            md5 = hashlib.md5(page.encode('utf-8'))
            md5_str = md5.hexdigest()
            if tag is None:
                tag = datetime.datetime.now().strftime('%Y%m%d_%H%m%S')

            output_dir = os.path.join(output_dir, '{}/{}'.format(tag, url_md5_str))
            output_dir = check_duplicate_directory(output_dir)

            later = time.time()
            difference = str(round(float(later - now), 3))
            log['request_duration_secs'] = difference
            log['final_url'] = self.driver.current_url
            log['final_url_title'] = self.driver.title
            log['page_content_char_cnt'] = len(page)

            # working_dir = datetime.datetime.now().strftime('%Y%m%d_%H%m%S_{}'.format(tag))
            file_path_page_content = os.path.join(self.temp_dir, '{}.page.content'.format(md5_str))
            file_object = codecs.open(file_path_page_content, 'w', 'utf-8')
            file_object.write(page)

            # Screenshot of page
            print("Saving screenshot")
            self.driver.save_screenshot(os.path.join(output_dir, '{}.screenshot.png'.format(tag)))

            # Images on page
            if images:
                images = self.driver.find_elements_by_tag_name('img')
                idx = 0
                for image in images:
                    src = image.get_attribute("src")
                    if src:
                        try:
                            image_filepath = os.path.join(self.temp_dir, 'images', "img_{}".format(idx))
                            urllib.urlretrieve(src, image_filepath)
                        except:
                            print("Failed retrieving image: {}".format(src))
                    idx += 1
            archive_path = os.path.join(output_dir, 'page_content.zip')
            zip_path = os.path.join(self.temp_dir, "*")

            print("Zipping results\n\n")
            self.zip_results(archive_path, zip_path, self.temp_dir)

        except Exception as e:
            log['error'] = str(e)
            print("Error retrieving url: {}".format(str(e)))

        log_path = os.path.join(output_dir, 'logs.json')
        self.write_logs(log, log_path)


    def write_logs(self, log, path):
        '''
        Dumps logs to disk
        :param log: dictionary with log key / value pairs
        :param path: full path with filename of where to save logs
        :return: None
        '''
        with open(path, 'w') as fp:
            json.dump(log, fp)


    def zip_results(self, archive_name, contents_to_zip, delete_path):
        '''
        Zips the contents stored in the specified path to create the provided archive_name, encrypted with the
        password "infected".  The contents in the delete_path is deleted after the zip completes.
        :param archive_name: Name of the password protected archive to create
        :param contents_to_zip: Path to content to zip
        :param delete_path: Delete these contents when done
        :return: Nothing
        '''
        try:
            call(["7z","a", "-pinfected", "-tzip", archive_name, contents_to_zip])
            os.chmod(archive_name, mode=0o664)
        except Exception as e:
            print("Error zipping contents: {}".format(str(e)))
        shutil.rmtree(delete_path)


def check_duplicate_directory(directory):
    '''
    Checks if the directory already exists, if it does, finds another name not already taken by appending an integer
    at the end.
    :param directory: directory to check for existence
    :return: same or new unique directory name
    '''
    # Check if it already exists
    idx = 0
    temp_name = directory
    while True:
        # if exists, then try another directory
        try:
            os.stat(temp_name)
            temp_name = directory + '_{}'.format(idx)
            idx += 1
        except:
            ensure_directory(temp_name)
            return temp_name
    return temp_name


def ensure_directory(directory):
    '''
    Ensures the provided directory path exists, creates it if it doesn't exist
    :param directory: directory path to ensure is created
    :return: True if the directory path exists or was created, False on error.
    '''
    # Check if it already exists
    try:
        os.stat(directory)
        return True
    except:
        print("Output directory {} did not exist, creating it.".format(directory))

    # Didn't exist, let's create it
    try:
        os.makedirs(directory, exist_ok=True)
        os.chmod(directory, mode=0o755)
        return True
    except Exception as e:
        print("Error creating directory: {}".format(e))

    return False
