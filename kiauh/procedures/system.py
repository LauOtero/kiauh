# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from pathlib import Path
from subprocess import PIPE, CalledProcessError, run

from core.logger import DialogType, Logger
from utils.common import check_install_dependencies, get_current_date
from utils.fs_utils import check_file_exist
from utils.input_utils import get_confirm, get_string_input

from translate.i18n import _
import textwrap

def change_system_hostname() -> None:
    """
    Procedure to change the system hostname.
    :return:
    """

    Logger.print_dialog(
        DialogType.CUSTOM,
        [
            _("Changing the hostname of this system allows you to access an installed\n") +
            _("webinterface by simply typing the hostname like this in the browser:"),
            "\n\n",
            "http://<hostname>.local",
            "\n\n",
            _("Example: If you set your hostname to 'my-printer', you can access an\n") +
            _("installed webinterface by typing 'http://my-printer.local' in the\n") +
            _("browser."),
        ],
        custom_title=_("CHANGE SYSTEM HOSTNAME"),
    )
    if not get_confirm(_("Do you want to change the hostname?"), default_choice=False):
        return

    Logger.print_dialog(
        DialogType.CUSTOM,
        [
            _("Allowed characters: a-z, 0-9 and '-'"),
            _("The name must not contain the following:"),
            "\n\n",
            _("● Any special characters"),
            _("● No leading or trailing '-'"),
        ],
    )
    hostname = get_string_input(
        _("Enter the new hostname"),
        regex=r"^[a-z0-9]+([a-z0-9-]*[a-z0-9])?$",
    )
    if not get_confirm(_("Change the hostname to '{}'?").format(hostname), default_choice=False):
        Logger.print_info(_("Aborting hostname change ..."))
        return

    try:
        Logger.print_status(_("Changing hostname ..."))

        Logger.print_status(_("Checking for dependencies ..."))
        check_install_dependencies({"avahi-daemon"}, include_global=False)

        # create or backup hosts file
        Logger.print_status(_("Creating backup of hosts file ..."))
        hosts_file = Path("/etc/hosts")
        if not check_file_exist(hosts_file, True):
            cmd = ["sudo", "touch", hosts_file.as_posix()]
            run(cmd, stderr=PIPE, check=True)
        else:
            date_time = get_current_date()
            name = f"hosts.{date_time.get('date')}-{date_time.get('time')}.bak"
            hosts_file_backup = Path(f"/etc/{name}")
            cmd = [
                "sudo",
                "cp",
                hosts_file.as_posix(),
                hosts_file_backup.as_posix(),
            ]
            run(cmd, stderr=PIPE, check=True)
        Logger.print_ok()

        # call hostnamectl set-hostname <hostname>
        Logger.print_status(_("Setting hostname to '{}' ...").format(hostname))
        cmd = ["sudo", "hostnamectl", "set-hostname", hostname]
        run(cmd, stderr=PIPE, check=True)
        Logger.print_ok()

        # add hostname to hosts file at the end of the file
        Logger.print_status(_("Writing new hostname to /etc/hosts ..."))
        stdin = f"127.0.0.1       {hostname}\n"
        cmd = ["sudo", "tee", "-a", hosts_file.as_posix()]
        run(cmd, input=stdin.encode(), stderr=PIPE, stdout=PIPE, check=True)
        Logger.print_ok()

        Logger.print_ok(_("New hostname successfully configured!"))
        Logger.print_ok(_("Remember to reboot for the changes to take effect!\n"))

    except CalledProcessError as e:
        Logger.print_error(_("Error during change hostname procedure: {}").format(e))
        return
