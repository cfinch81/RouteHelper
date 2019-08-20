import sys, csv

import Tkinter as tk
import tkFileDialog
import myNotebook as nb
from config import config

import pyperclip

this = sys.modules[__name__]    # For holding module globals


def plugin_start(plugin_dir):
    """
    Load this plugin into EDMC
    """
    # Initialze module globals
    this.current_system = None
    this.systems = []


    load_systems()

    print "Route Helper loaded! My plugin folder is {}".format(plugin_dir.encode("utf-8"))
    return "Route Helper"

def plugin_stop():
    """
    EDMC is closing
    """
    print "Route Helper exiting!"

def journal_entry(cmdr, is_beta, system, station, entry, state):
    if entry['event'] == 'FSDJump' or entry['event'] == 'Location' or entry['event'] == 'StartUp':
        # We have just started up or arrived at a new system!
        this.current_system = entry['StarSystem']
        if this.current_system in this.systems:
            copy_next_system(this.current_system)

def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    PADX = 5
    PADY = 2

    this.route_file_location_setting = tk.StringVar(value=config.get("RouteHelperPlugin_RouteFileLocationSetting"))   # Retrieve saved value from config

    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    def select_csv_file():
        file_selection = tkFileDialog.askopenfilename(filetypes=[("Supported files","*.csv *.txt"),("CSV files","*.csv"),("Text files","*.txt"),("All files","*.*")])
        if file_selection:
            this.route_file_location_setting.set(file_selection)

    def clear_csv_file():
        this.route_file_location_setting.set("")

    nb.Label(frame, text="Route File Location: ").grid(row=0, padx=PADX, pady=PADY, sticky=tk.E)
    nb.Entry(frame, textvariable=this.route_file_location_setting).grid(row=0, column=1, columnspan=2, sticky=tk.EW)
    nb.Button(frame, text="Select Route File", command=select_csv_file).grid(row=0, column=3, padx=PADX, pady=PADY, sticky=tk.EW)
    nb.Button(frame, text="Clear Route File", command=clear_csv_file).grid(row=1, column=3, padx=PADX, pady=PADY, sticky=tk.EW)

    return frame

def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('RouteHelperPlugin_RouteFileLocationSetting', this.route_file_location_setting.get())   # Store new value in config
    load_systems()
    if this.current_system and this.current_system in this.systems:
        copy_next_system(this.current_system)

def load_systems():
    """
    Make a list of systems to visit from the csv or text file specified in the config (if specified)
    """
    route_filename = config.get('RouteHelperPlugin_RouteFileLocationSetting')
    known_list_headers = [
        "System Name",
        ]

    try:
        with open(route_filename, "r") as route_file:
            csvreader = csv.reader(route_file)
            this.systems = [row[0] for row in csvreader if row[0] not in known_list_headers]
            print "Route Helper - load_systems() loaded systems from \"{}\"".format(route_filename)
            print "Route: " + ", ".join(this.systems)
    except:
        this.systems = []
        print "Route Helper - load_systems() failed to load systems from \"{}\"".format(route_filename)

def copy_next_system(current_system):
    """
    Copy the next system to the clipboard if we're currently in a system in the systems list
    """
    try:
        system_index = this.systems.index(current_system)
        pyperclip.copy(this.systems[system_index+1])
        print "Route Helper - copy_next_system(\"{}\") copied \"{}\" to clipboard".format(current_system, this.systems[system_index+1])
    except:
        print "Route Helper - copy_next_system(\"{}\") failed".format(current_system)
