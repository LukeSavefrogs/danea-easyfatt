from pathlib import Path
import winreg as _winreg

def find_install_location(program_reg_key: str):
    """Finds the installation location of a program using the registry.

    Args:
        program_reg_key (str): The registry key of the program to find.

    Raises:
        Exception: If the program is not found.

    Returns:
        Path: The installation path of the program.
    """
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, program_reg_key)
    
    search_targets = ["InstallPath", "InstallLocation"]
    for key_name in search_targets:
        try:
            return Path(_winreg.QueryValueEx(key, key_name)[0])
        except FileNotFoundError:
            continue
    else:
        raise Exception(f"Registry key '{program_reg_key}' not found [{'/'.join(search_targets)}]!")
