from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from PIL import Image
import os
import codecs
from subprocess import call
import datetime
import hashlib
import shutil
import time
import json

class sURLi:
    def __init__(self, temp_dir='./temp_results', output_dir='./results', useragent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")  # Needed to run in docker
        options.add_argument("user-agent={}".format(useragent))

        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance' : 'ALL'}
        self.driver = webdriver.Chrome(chrome_options=options, desired_capabilities=caps)
        # self.driver.wait = WebDriverWait(self.driver, 5)

        self.temp_dir = temp_dir
        self.output_dir = output_dir
        ensure_directory(self.output_dir)
        ensure_directory(self.temp_dir)


    def pad_image(self, imagename, desired_size=1280):
        '''
        sourceglob is a glob patterns e.g. "./images/*.png"
        destdir is a directory location e.g. "./images_resized/"
        '''
        try:
            img = Image.open(imagename)
            old_size = img.size
            ratio = float(desired_size) / max(old_size)
            new_size = tuple([int(x * ratio) for x in old_size])
            img = img.resize(new_size, Image.ANTIALIAS)
            new_img = Image.new("RGB", (desired_size, desired_size))
            new_img.paste(img, ((desired_size - new_size[0]) // 2, (desired_size - new_size[1]) // 2))
            new_img.save(imagename)
        except Exception as e:
            print("error processing: {} - {}".format(imagename, str(e)))

    def write_new_to_json(self, entries, log_file_name):
        with open(log_file_name, 'a') as outfile:
            for entry in entries:
                json.dump(entry, outfile)
                outfile.write('\n')

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

        # Set timeouts
        self.driver.implicitly_wait(timeout_seconds)
        self.driver.set_page_load_timeout(timeout_seconds)
        self.driver.set_script_timeout(timeout_seconds)

        if tag is None:
            tag = datetime.datetime.now().strftime('%Y%m%d_%H%m%S')

        url_md5_str = hashlib.md5(url.encode('utf-8')).hexdigest()
        log = {'original_url': url}
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join(self.output_dir, '{}/{}'.format(tag, date_str))
        ensure_directory(output_dir)
        log['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        try:
            # Get URL
            now = time.time()
            self.driver.get(url)

            # Content of page and hash of content
            page = self.driver.page_source
            md5 = hashlib.md5(page.encode('utf-8'))
            md5_str = md5.hexdigest()

            output_dir = os.path.join(output_dir, url_md5_str)
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

            # Save Performance Logs
            perf_log_entries = []
            for entry in self.driver.get_log('performance'):
                perf_log_entries.append(entry)
            perf_log_filename = os.path.join(output_dir, 'browser_logs.json')
            self.write_new_to_json(perf_log_entries, perf_log_filename)

            # Screenshot of page
            print("Saving screenshot")
            #self.driver.set_window_position(0, 0)
            image_size = 1280
            self.driver.set_window_size(image_size, image_size)
            screenshot_filename = os.path.join(output_dir, '{}.screenshot.png'.format(tag))
            self.driver.save_screenshot(screenshot_filename)
            self.pad_image(screenshot_filename, desired_size=image_size)

            print("done")
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

if __name__ == '__main__':
    url = 'https://stackoverflow.com/questions/8255929/running-selenium-webdriver-python-bindings-in-chrome?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa'
    url = 'http://liveresults.be/2016/ifam-outdoor/schedule.html'
    #url = 'http://wiki.c2.com/?GoodVariableNames'
    #url = 'http://google.com'
    url = 'http://somenonesensethatdoesnotexistbutwethoughtitdid.com'
    url = 'invalid.stuffasdfsd'

    temp_dir = './temp'
    output_dir = './output'

    surli = sURLi(temp_dir=temp_dir, output_dir=output_dir)
    surli.get_url_contents(url, tag='whocares', timeout_seconds=60)
