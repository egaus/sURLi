import sURLi as surlilib
import argparse
import os
import datetime
import shutil

def main():
    parser = argparse.ArgumentParser(description="Simple tool to pull back contents of a url")
    parser.add_argument('-u', '--url', help='url to retrieve, remember a url includes "http" or "https"')
    parser.add_argument('-t', '--tag', help='(Optional) tag that will be added to saved content pulled from the url')
    parser.add_argument('-l', '--time_limit', help='(Optional) time limit for analysis (in seconds).  Default is 60')
    parser.add_argument('-o', '--output_dir', help='(Optional) directory where results are saved.  Default is /surli/results')
    parser.add_argument('-s', '--staging_dir', help='(Optional) directory where temporary results are saved, ideally this location is not scanned by anti-virus products.  Default is /surli/temp')
    args = parser.parse_args()

    # Handle time limit
    if args.time_limit:
        try:
            time_limit = int(args.time_limit)
        except Exception as e:
            print("\n--time_limit must be an integer e.g. 30\n")
            parser.print_help()
            exit(0)
    else:
        time_limit = 60

    # Ensure URL is provided
    if not args.url:
        print("\nMust supply a url\n")
        parser.print_help()
        exit(0)

    # Setup output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = '/surli/results'

    # Setup temporary staging directory
    if args.staging_dir:
        temp_dir = args.staging_dir
    else:
        temp_dir = '/surli/temp'

    try:
        surli = surlilib.sURLi(temp_dir=temp_dir, output_dir=output_dir)
        surli.get_url_contents(args.url, tag=args.tag, timeout_seconds=time_limit)
    except Exception as e:
        print("Error: {}".format(e))
        print("Cleaning up temporary location: {}".format(temp_dir))
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()
