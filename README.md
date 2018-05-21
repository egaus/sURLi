## Suspicious URL Investigator (sURLi)

Simple tool used to grab a screenshot and download content from URLs.

Features:
 - Organizes downloaded conent by date, tag, and hash of website content
 - Provides a screenshot of the site
 - Logs the chrome network traffic logs to a json file
 - Zip encrypts the page content with the password "infected"

Requirements:
 - Must have docker installed and Internet access to build the image

Installation and Setup:
```
$ git clone <this repo>
$ cd sURLi
$ mkdir data
$ docker build -t="surli" .
$ docker run --rm -v ${PWD}/data:/surli/results -it surli

Must supply a url

usage: surli_cli.py [-h] [-u URL] [-t TAG] [-l TIME_LIMIT] [-o OUTPUT_DIR]
                    [-s STAGING_DIR]

Simple tool to pull back contents of a url

optional arguments:
  -h, --help            show this help message and exit
   ...
```

Usage:
```
$ docker run --rm -v ${PWD}/data:/surli/results -it surli -u https://www.google.com
Output directory /surli/temp did not exist, creating it.
Invoking Firefox webdriver

Retrieving contents of url https://www.google.com
...
Everything is Ok
$ tree data/
data/
`-- 20180521_110537
    `-- 20180521
        `-- 8ffdefbdec956b595d257f0aaeefd623
            |-- 20180521_110537.screenshot.png
            |-- browser_logs.json
            |-- logs.json
            `-- page_content.zip

4 directories, 2 files
```

After running the example above, the downloaded results will be in ./data

Note: The downloaded files in the data directory will have permissions set to not allow write access to the directory.  Either copy the zip file out and inflate it or use chmod to change permissions.
