#! /usr/bin/env python3
'''
    Backdrop CMS CLI Updater v0.92 Beta
    Copyright 2020 by Justin Sitter

    Permission is hereby granted, free of charge, to any person 
    obtaining a copy of this software and associated documentation 
    files (the "Software"), to deal in the Software without 
    restriction, including without limitation the rights to use, 
    copy, modify, merge, publish, distribute, sublicense, and/or 
    sell copies of the Software, and to permit persons to whom the 
    Software is furnished to do so, subject to the following 
    conditions:

The above copyright notice and this permission notice shall be 
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS 
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN 
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
'''
import hashlib
import math
from optparse import OptionParser
import os
import os.path as path
import shutil
import sys
import time
import zipfile
import urllib.request as req
import xml.etree.ElementTree as ET

backdrop_server_address = 'https://updates.backdropcms.org/release-history/backdrop/1.x'
home_directory = os.path.dirname(os.path.realpath(__file__))
temp_dir = home_directory + '/.tempdir'

forbidden_folders = {'files', 'layouts', 'modules', 'sites', 'themes'}
forbidden_files = {'.htaccess', 'settings.php', 'sites.php'}

def check_dir(directory):
    if not path.exists(directory):
        os.mkdir(directory)

def remove_directory(source):
    print("Removing {} directory".format(source))
    shutil.rmtree(source)

def remove_file(source):
    print("Removing {}".format(source))
    os.remove(source)

def replace_item(source, destination):
    if path.isdir(destination):
        file_format = "directory"
        remove_directory(destination)
    else:
        file_format = ""
        remove_file(destination)
    print("Replacing {} {}".format(destination, file_format))
    shutil.move(source, destination)

def update_file(temp_location, file, destination, replace=False):
    file_destination = "{}/{}".format(destination, file)
    temp_file_location = "{}/{}".format(temp_location, file)

    if not path.exists(file_destination):
        print("Installing {}".format(file))
        shutil.move(temp_file_location, destination)
    elif replace:
        replace_item(temp_file_location, file_destination)
    else:
        if file in forbidden_folders:
            print("Skipping {}. Directory already exists.".format(file))
        elif file in forbidden_files:
            print("Skipping {}. File already exists.".format(file))
        else:
            try:
                replace_item(temp_file_location, file_destination)
            except:
                print("{} locked".format(file))

def download_report_hook(count, chunk_size, total_size):
    global start_time
    global download_amount

    cur_time = time.time()
    if count == 0:
        download_amount = chunk_size
        start_time = cur_time
        return
    else:
        download_amount += chunk_size

    duration = cur_time - start_time
    
    progress = download_amount
    speed = int(download_amount / (1024 * duration))

    # Toggle between MB/s and KB/s depending on download speed
    if speed > 799:
        speed = speed / 1000
        speed_scale = "MB/s"
    else:
        speed_scale = "KB/s"

    percent = progress * 100 / total_size
    progress_mb = progress / (1024 * 1024)
    percent_scale = int(math.floor(percent)/4)
    vis_downloaded = "=" * percent_scale
    vis_remaining = "." * (25 - percent_scale)

    CURSOR_UP = '\x1b[1A'
    CLEAR_LINE = '\x1b[2k'

    # Display download progress bar
    sys.stdout.write("{}{}\r{}>{}|            \n".format(CURSOR_UP, CLEAR_LINE, vis_downloaded, vis_remaining))
    # Display Download progress information
    sys.stdout.write("\r{}{} {:.2f}% -- {:.2f}MB out of {:.2f}MB {:.0f}s          ".format(speed, speed_scale, percent, progress_mb, total_size/1000000, duration))
    sys.stdout.flush()

def unpack_zip_into(source, destination, replace=False):
    zipReference = zipfile.ZipFile(source, 'r')
    allfiles = zipReference.namelist()

    temp_source_dir = "{}/{}".format(temp_dir, allfiles[0].split('/')[0])

    check_dir(temp_dir)
    check_dir(destination)
    
    zipReference = zipfile.ZipFile(source, 'r')
    zipReference.extractall(temp_dir)
    files = os.listdir(temp_source_dir)

    for file in files:
        update_file(temp_source_dir, file, destination, replace)

    shutil.rmtree(temp_source_dir)
    
    zipReference.close()
    print("Done")

def verifyFileSize(source_location, size):
    if path.exists(source_location):
        source_size = path.getsize(source_location)
        if str(size) != str(source_size):
            keep_bad_file = input("Local installation file incomplete. Keep anyway? [Y/n]")
            if keep_bad_file != "Y":
                remove_file(source_location)

def download_backdrop_package(download_url, filename, version="", source_hash=None, size=None):
    check_dir(temp_dir)
    destination = "{}/{}".format(temp_dir, version+filename)
    retry = True
    while retry:
        retry = False
        if source_hash == None and size is not None:
            verifyFileSize(destination, size)
            
        if not path.exists(destination):
            try:
                print("Downloading Backdrop {}\nConnecting to download server...".format(version))
                req.urlretrieve(download_url, destination, download_report_hook)
                # sys.write('\rDownload Complete')
                # sys.flush()
            except:
                user_retry = input("Failed to complete download. Retry? [Y/n]")
                if user_retry == "Y" or user_retry == "y":
                    retry = True
                else:
                    sys.exit(1)

                if size is not None:
                    verifyFileSize(destination, size)
            else:
                sys.stdout.write("\rDownload Complete.                                    \n")
                sys.stdout.flush()
        else:
            print("Using local file.")
    
    f = open(destination, 'rb')

    if source_hash is not None:
        print("Verifying package authenticity.")
        file_hash = hashlib.md5(f.read()).hexdigest()

        if file_hash != source_hash:
            print("Warning! Hash Mismatch")
            remove_file(destination)
        else:
            print("Package authenticity established")
    f.close()

def get_xml_urllib(url):
    res = req.urlopen(url)
    xml = res.read()
    return ET.fromstring(xml)

def get_backdrop_versions(num_of_versions=None):
    root = get_xml_urllib(backdrop_server_address)
    # debug from saved xml data
    # with open('drupalxml.xml', 'wb') as f:
    #     f.write(response.content)
    # root = ET.parse('drupalxml.xml').getroot()

    release_order = []

    release_dict = {}
    releases = root.findall('releases/release')
    for release in releases:
        release_types = release.findall("terms/term")
        security = None
        release_type = None
        for release_typ in release_types:
            try:
                release_type = release_typ.find('value').text
                if release_type == "Insecure":
                    security = release_type
            except:
                release_type = ""
        
        release_name = release.find("name").text
        release_version = release.find("version").text
        try:
            release_url = release.find("download_link").text
        except:
            break
        release_size = release.find("filesize").text
        try:
            release_hash = release.find("mdhash").text
        except:
            release_hash = None

        release_version = release.find("version").text
        release_order.append(release_version)
        cur_release = {"name": release_name, 
                        "type": release_type, 
                        "url": release_url, 
                        "hash": release_hash,
                        "filename": release_url.split("/")[-1],
                        "filesize": release_size,
                        "version": release_version,
                        "security": security}

        release_dict[release_version] = cur_release
    if num_of_versions is not None and num_of_versions < len(release_order):
        release_dict["order"] = release_order[:num_of_versions]
    else:
        release_dict["order"] = release_order
    return release_dict

if __name__ == "__main__":
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--download",
                        help="Download specified version from Backdrop.org. If no version is specified most recent version will be chosen",
                        action="store_true",
                        dest="download")

    parser.add_option("-f", "--file",
                        help="Use local installation package. (Must be zip file)",
                        dest="local_path")

    parser.add_option("--replace-all",
                        help="Replace all existing files when installing. **WARNING!** This will replace any custom modules, themes, and file uploads. Use with caution.",
                        action="store_true",
                        dest="replace")
    
    parser.add_option("-l", "--list",
                        help="List available versions of backdrop. Defaults to all versions but add optional argument to limit to most recent N versions.",
                        action="store_true",
                        dest="list")
    
    parser.add_option("-i", "--install",
                        help="Location of local backdrop installation",
                        dest="install")
    
    (options, args) = parser.parse_args()

    if options.list:
        if args:
            num_of_versions = int(args[0])
            versions = get_backdrop_versions(num_of_versions)
            print("Showing most recent {} versions".format(num_of_versions))
            for version in versions['order']:
                print(version)
        else:
            versions = get_backdrop_versions()
            print("{} available versions".format(len(versions['order'])))

            for version in versions['order']:
                print(version)

    elif options.download:
        versions = get_backdrop_versions()
        if args:
            if args[0] not in versions:
                print("Version not available")
                sys.exit(1)
            else:
                if versions[args[0]]['security'] == "Insecure":
                    user_choice = input("Version {} is insecure. Proceed anyway? [Y/n]")
                    if user_choice != 'Y':
                        print("Aborting Installation")
                        sys.exit(0)
                version = versions[args[0]]
        else:
            version = versions[versions["order"][0]]
        
        download_url = version['url']
        download_version = version['version']
        download_filename = version['filename']
        filesize = version['filesize']
        download_hash = version['hash']
        saved_filename = download_version + download_filename
        download_backdrop_package(download_url, download_filename, download_version, download_hash, size=filesize)

        if options.install:
            destination = options.install
        else:
            destination = input("Enter installation location: ")

        print("Installing in: {}".format(destination))
        source = "{}/{}".format(temp_dir, saved_filename)

        if options.replace:
            unpack_zip_into(source, destination, replace=True)
        else:
            unpack_zip_into(source, destination)

    elif options.local_path:
        if options.install:
            destination = options.install
        else:
            destination = input("Enter installation location: ")
        print("Installing into {}".format(destination))
        if options.replace:
            unpack_zip_into(options.local_path, destination, replace=True)
        else:
            unpack_zip_into(options.local_path, destination)

    else:
        parser.print_help()         
