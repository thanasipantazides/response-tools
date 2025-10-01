"""
Script to download data from FOXSI server.
"""

import os, cmd, sys
import pprint
# from pathlib import PureWindowsPath, PurePosixPath

from bs4 import BeautifulSoup
from enum import Enum
import inquirer
import requests
from tqdm import tqdm
import urllib.request
from urllib.parse import urljoin

from response_tools.io.load_yaml import load_response_context

local_prefix = 'response-information'

ignore_urls = ['@eaDir/']

DEBUG = True

def print_green(txt:str):
    print('\033[92m' + txt + '\033[0m')
def print_red(txt:str):
    print('\033[91m' + txt + '\033[0m')

class DownloadType(Enum):
    latest = 1
    historical = 2
    component = 3
    telescope = 4
    file = 5



class DownloadPrompt:
    def __init__(self):
        self.remote = "http://foxsi.space.umn.edu/data/response/response-components/"
        self.local_prefix = 'response-information'
        self.start_prompt = [
            inquirer.List(
                "query",
                message="Which data products would you like to download?",
                choices=[
                    ("Get all latest products",                 DownloadType.latest),
                    ("Get all historical products",             DownloadType.historical),
                    ("Get specific response components",        DownloadType.component),
                    ("Get response components for telescope",   DownloadType.telescope),
                    ("Get specific file",                       DownloadType.file)
                ]
            )
        ]
        self.theme = inquirer.themes.load_theme_from_dict({
            "Question": {
                "mark_color": "blue",
                "brackets_color": "normal"
            },
            "List":{
                "selection_color": "bold_green",
                "selection_cursor": ">"
            }
        })
        self.prompt_machine = {
            DownloadType.latest:        self._fetch_latest,
            DownloadType.historical:    self._fetch_historical,
            DownloadType.component:     self._prompt_component,
            DownloadType.telescope:     self._prompt_telecope,
            DownloadType.file:          self._prompt_file
        }

        answers = inquirer.prompt(self.start_prompt, theme=self.theme)

        self._handle_prompt(answers["query"])

    def _handle_prompt(self, reply:DownloadType):
        if reply in self.prompt_machine.keys():
            self.prompt_machine[reply]()
        else:
            raise KeyError("Unimplemented user selection: " + reply)

    def _fetch_latest(self):
        print("latest")
    def _fetch_historical(self):
        print("historical")
    def _prompt_component(self):
        component_prompt = [
            inquirer.Checkbox(
                "component",
                message="Which response component(s) would you like to download?",
                choices=["detector response", "attenuation", "effective area", "quantum efficiency"]
            )
        ]
        answers = inquirer.prompt(component_prompt, theme=self.theme)


    def _prompt_telecope(self):
        telescope_prompt = [
            inquirer.Checkbox(
                "telescope",
                message="Which telescope's products would you like to download?",
                choices=[
                    ("P0 - CMOS detector,    2-shell optic", 0),
                    ("P1 - CMOS detector,    1-shell optic", 1),
                    ("P2 - CdTe detector,   10-shell optic", 2),
                    ("P3 - CdTe detector,    2-shell optic", 3),
                    ("P4 - CdTe detector,    1-shell optic", 4),
                    ("P5 - CdTe detector,   10-shell optic", 5),
                    ("P6 - Timepix detector, 2-shell optic", 6)
                ]
            )
        ]
        answers = inquirer.prompt(telescope_prompt, theme=self.theme)

    def _prompt_file(self):
        file_prompt = [
            inquirer.Text(
                "file",
                message="Provide the URL to download"
            )
        ]
        answers = inquirer.prompt(file_prompt, theme=self.theme)
        print(answers["file"])



def green_str(text:str):
    return "\033[92m" + text + "\033[0m"

def foxsi4_download_required(replace_existing=False, verbose=False):
    """Download all response component files specified in `response-information/info.yaml`.

        Download data products from a remote server to the local filesystem. Retrieves server
        URL and all local paths for saving data from a config file:
        `response-tools/response-information/info.yaml`. All downloaded response data will be
        saved under `response-tools/response-information`.
    
        Parameters
        ----------
        replace_existing : `bool`
            Whether to replace local files with newer versions, if newer versions are
            downloaded. Currently throws `NotImplementedError`.  

        verbose : `bool`
            Toggle for printing verbosely. If `True`, download progress indicators and
            filenames are displayed. If `False`, nothing is printed at all.

        Returns
        -------    
        : `downloaded`
            A dict of downloaded data. Keys are the same file identifiers from the YAML
            source. Values are the absolute paths on the local filesystem to the downloaded
            file. Files which were already existed in the local filesystem (required no
            downloaded) are not included in the return value.
    """

    if replace_existing == True:
        raise NotImplementedError("No support yet for replacement of old file versions.")
    
    # print if the verbose flag is set:
    def verbose_print(*something):
        if verbose:
            print(*something)

    req = load_response_context()
    server_url = req["remote_server"]
    
    # for urllib.parse.urljoin to work correctly, server path prefix must end in `/`:
    if server_url[-1] != "/":
        server_url += "/"
    
    # directory on local filesystem for saving data:
    local_info_dir = os.path.abspath(os.path.join(__file__, "..", "..", "response-information"))
    verbose_print("Retrieving response products from:", green_str(server_url))
    verbose_print("Saving response products to:", green_str(local_info_dir))

    # record which files already exist on-disk (don't waste time downloading):
    existing_files = []
    for r,_,fs in os.walk(local_info_dir):
        for f in fs:
            existing_files.append(os.path.join(r,f))

    desired_files = []      # list of the files to download
    destination_path = []   # local path to save them to
    source_name = []        # identifier of the file (YAML key)
    do_get = []             # flag whether to download (if the file already exists locally)
    
    for comp_name in req["files"].keys():
        for f_name, suffix in req["files"][comp_name].items():
            desired_files.append(urljoin(server_url, suffix))
            dest = os.path.join(local_info_dir, suffix)
            destination_path.append(dest)
            source_name.append(f_name)

            if os.path.exists(dest):
                do_get.append(False)
            else:
                do_get.append(True)

    downloaded = {}
    if any(do_get):
        verbose_print("Retrieving files...")
        for (k, f) in enumerate(tqdm(desired_files, disable=not verbose)):

            if do_get[k]:
                try:
                    # create the folders along the save path, if needed
                    os.makedirs(os.path.dirname(destination_path[k]))
                except:
                    pass

                # check if the URL ends in "/" which indicates a folder
                if f.endswith("/"):
                    # get the contents of the folder
                    page = requests.get(f).text
                    soup = BeautifulSoup(page, 'html.parser')
                    # make sure we extract all the hrefs then check the link has a "." in it for an extension
                    linked_files = [node.get('href') for node in soup.find_all('a') if ("." in node.get('href'))]
                    # just download the folder contents
                    for link in linked_files:
                        urllib.request.urlretrieve(f+link, os.path.join(destination_path[k], link))
                    downloaded[source_name[k]] = f
                    green_name = f
                else:
                    # download the file:
                    fname, head = urllib.request.urlretrieve(f, destination_path[k])
                    green_name = os.path.basename(fname)
                # record the identifier and path of the downloaded file:
                downloaded[source_name[k]] = fname
                if verbose:
                    tqdm.write("Downloaded " + green_str(green_name))
    else:
        verbose_print("Found nothing new to download")
    return downloaded

if __name__ == "__main__":
    # DownloadPrompt()

    downloaded = foxsi4_download_required(verbose=True)
    pprint.pprint(downloaded)