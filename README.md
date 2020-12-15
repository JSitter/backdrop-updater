# Backdrop CMS 1.x Core Updater 
## Version 0.92 Beta
Easily install or update Backdrop Core using the command line. 

## Usage
Run `./backdrop-updater.py` in the terminal to see a list of all available features.

**Flags**

`-d`, `--download` Download version from the internet. Defaults to the most recent version if not specified.

`-f LOCAL_PATH`, `--file=LOCAL_PATH` Install from specified zip file.

`--replace-all` Replace all files with those from installation package. **WARNING** This will overwrite any custom modules, .htaccess files, themes, user uploads etc. Use with extreme caution.

`-l`, `--list` List all versions of Backdrop available for installation.

`i INSTALLATION_LOCATION`, `--install=INSTALLATION_LOCATION` Specify location of backdrop installation.

## Version History

### 0.92 Beta
- Adds download progress feedback.

### 0.91 Beta
- Adds the option to retry the download if it initially fails.
- Clearer feedback.

### 0.9 Beta
- Allows updating or installation of Backdrop CMS from the command line.

## MIT License
Copyright 2020 Justin Sitter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
