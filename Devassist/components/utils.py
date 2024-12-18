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

