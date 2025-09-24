"""
Script to download data from FOXSI server.
"""

import urllib.request
import os, cmd, sys
from enum import Enum
import inquirer

from bs4 import BeautifulSoup as bs
from astropy.io import fits

import pprint

remote = "http://foxsi.space.umn.edu/data/response/response-components/"
local_prefix = 'response-information'
area_files = [
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/foxsi4_telescope-0_BASIC_mirror_effective_area_v1.fits",
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/foxsi4_telescope-1_BASIC_mirror_effective_area_v1.fits",
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/nagoya_hxt_onaxis_measurement_v1.txt",
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/nagoya_sxt_onaxis_measurement_v1.txt",
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/FOXSI4_Module_MSFC_HiRes_EA_with_models_v1.txt",
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/foxsi4_telescope-0_BASIC_TELESCOPE_RESPONSE_V25APR13.fits",
    "http://foxsi.space.umn.edu/data/response/response-components/effective-area-data/foxsi4_telescope-1_BASIC_TELESCOPE_RESPONSE_V25APR13.fits"
]

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


if __name__ == "__main__":
    DownloadPrompt()
    # pprint.pprint(answers)

    # if answers["query"] == ""


    # for file in area_files:
    #     url_suffix = os.path.join(os.path.split(file)[-2], os.path.split(file)[-1])
    #     url_dir_prefix, url_file = os.path.split(file)
    #     _, url_dir = os.path.split(url_dir_prefix)

    #     local_dest = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..', local_prefix, url_dir, url_file))
    #     if os.path.isfile(local_dest):
    #         print_red('\talready have local copy of ' + url_file + ', skipping.')
    #         continue

    #     local_name, local_ext = os.path.splitext(local_dest)
    #     local_ver = local_name.rsplit('v', 1)

    #     print('found new file: ' + local_dest)
    #     print_green('\tfound version: ' + local_ver[-1])
    #     print_green('\t' + local_dest)

    #     fname, head = urllib.request.urlretrieve(file, local_dest)
    #     # d = f.read()

    #     if os.path.splitext(fname) == '.fits':
    #         with fits.open(fname) as hdul:
    #             print(hdul.info())
    #     elif os.path.splitext(fname) == '.csv':
    #         print('a csv...')



    # f = urllib.request.urlopen(remote)
    # d = f.read()

    # soup = bs(d, 'html.parser')
    # print('reading page:', '\033[92m' + soup.title.string + '\033[0m ...')

    # links = soup.find_all('a')  # select all HTML <a> tags
    # print('found links:')
    # for link in links:          # check each link
    #     h = link.get('href')    # get the hyperref
    #     if h[-1] == '/':        # find folders (end in `/`)
    #         if h not in ignore_urls:    # ignore the ignorables
    #             print_green('\t' + h)
