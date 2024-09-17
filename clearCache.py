import os
import shutil
from tkinter import Tk
from tkinter.filedialog import askdirectory


def select_profiles_directory():
    """Mở hộp thoại để chọn thư mục profiles."""
    Tk().withdraw()  # Ẩn cửa sổ chính của Tkinter
    selected_dir = askdirectory(title="Select Profiles Directory")

    if not selected_dir:
        print("No directory selected.")
        exit(1)

    return selected_dir


def clear_cache_data(profiles_dir):
    """Xóa dữ liệu trong thư mục Cache_Data của tất cả các profile trong profiles_dir."""
    # Duyệt qua tất cả các folder trong thư mục profiles
    for profile in os.listdir(profiles_dir):
        profile_path = os.path.join(profiles_dir, profile)

        # Kiểm tra xem profile có phải là thư mục không
        if os.path.isdir(profile_path):
            default_dir = os.path.join(profile_path, 'Default')
            cache_dir1 = os.path.join(default_dir, 'Cache')
            cache_dir = os.path.join(cache_dir1, 'Cache_Data')

            # Kiểm tra xem thư mục Default có tồn tại không
            if os.path.exists(default_dir):
                # Kiểm tra xem thư mục Cache_Data có tồn tại không
                if os.path.exists(cache_dir):
                    print(f"Clearing all data in: {cache_dir}")

                    # Xóa tất cả nội dung trong thư mục Cache_Data
                    for item in os.listdir(cache_dir):
                        item_path = os.path.join(cache_dir, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                else:
                    print(f"Folder Cache_Data not found in {default_dir}")
            else:
                print(f"Folder Default not found in {profile_path}")


def main():
    # Chọn thư mục profiles
    profiles_dir = select_profiles_directory()

    # Kiểm tra xem thư mục profiles có tồn tại không
    if not os.path.exists(profiles_dir):
        print(f"Folder 'profiles' not found in {profiles_dir}.")
        exit(1)

    # Xóa dữ liệu trong thư mục Cache_Data của tất cả các profile
    clear_cache_data(profiles_dir)


if __name__ == "__main__":
    main()
