if __name__ == '__main__':
    orig_filename = "Main"
    folder_name = "ArrayTest"
    with open(f"XMLs/{folder_name}/{orig_filename}NoSpaces.xml", "w") as target:
        with open(f"XMLs/{folder_name}/{orig_filename}.xml", "r") as file:
            for line in file:
                line = line.replace(' ', '')
                if line:
                    target.write(line)

    with open(f"{folder_name}/{orig_filename}NoSpaces.xml", "w") as target:
        with open(f"{folder_name}/{orig_filename}.xml", "r") as file:
            for line in file:
                line = line.replace(' ', '')
                if line:
                    target.write(line)