def convert_to_linux_path(windows_path: str) -> str:
    linux_path = windows_path.replace("\\", "/")
    linux_path = "/proj/BV_data/" + linux_path[linux_path.find("TrackingPRC"):]
    return linux_path
