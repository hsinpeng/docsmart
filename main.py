import platform

def main():
    print("--------------------------------------------------")
    # Get the OS name string
    os_name = platform.system()
    if os_name == "Darwin":
        print("Running on macOS")
        version, _, architecture = platform.mac_ver()
        print(f"macOS Version: {version}, Architecture: {architecture}")
    elif os_name == "Windows":
        print("Running on Windows")
        release, version, sp, os_type = platform.win32_ver()
        print(f"Windows Release: {release}")    # e.g., "10" or "11"
        print(f"Build Version: {version}")      # e.g., "10.0.22631"
        print(f"Service Pack: {sp}")            # e.g., "SP0"
        print(f"OS Type: {os_type}")            # e.g., "Multiprocessor Free"
    elif os_name == "Linux":
        print("Running on Linux")
        distro_info = platform.freedesktop_os_release()
        print(f"Distribution Name: {distro_info.get('NAME')}")  # e.g., "Ubuntu"
        print(f"Version: {distro_info.get('VERSION')}")         # e.g., "24.04 LTS"
        print(f"Version ID: {distro_info.get('VERSION_ID')}")   # e.g., "24.04"
        print(f"ID (Family): {distro_info.get('ID')}")          # e.g., "ubuntu" or "debian"
    else:
        print(f"Running on an unknown OS: {os_name}")
    print("--------------------------------------------------")

    # Main program
    try:
        print("Hello from docsmart!")
        
    except Exception as e: # Runs for any other unexpected errors
        print(f"An unexpected error occurred: {e}")

    finally: # ALWAYS runs, no matter what happens above (even if there is a return statement)
        pass


if __name__ == "__main__":
    main()