import os

async def traverse_directory(current_dir, visited_dirs,list_contents):
    if os.path.isdir(current_dir):
        print(f"Reading directory: \n{current_dir}")
        visited_dirs[current_dir] = 'read'
        
        contents = os.listdir(current_dir)
        for item in contents:
            item_path = os.path.join(current_dir, item)
            if os.path.isfile(item_path):
                print(f"Reading file: {item_path}")
                list_contents.append(item_path)
            elif os.path.isdir(item_path):
                print(f"calling another dir\n{item_path}")
                await traverse_directory(item_path, visited_dirs,list_contents)
    return list_contents

def read_file_content(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""



async def save_content_to_file(file_path: str, new_dir: str, content: str):
    """
    """
    new_file_path = os.path.join(new_dir, file_path)
    try:
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        with open(new_file_path, 'w') as file:
            file.write(content)
        print(f"Content successfully saved to: {new_file_path}")

    except Exception as e:
        print(f"Error saving content to {new_file_path}: {e}")

