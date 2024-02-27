# This version bulk converts a specified directory of catalog files which are legacy format
# catalog file exports into schema version 2.0. The program will create a new directory where ever
# it is run from containing the new version. Adjust or remove the file name modification suffix
# if desired.


import json
import glob
import sys
import os

def main():
   files = get_current_files()
   create_output_dir()

   for i, filename in enumerate(files):
       process_file(i,filename)

def get_current_files():
    dir = input('Enter the complete path for the directory of catalog files to be converted: ')
    try:
        if not os.path.exists(dir):
            # Raise an exception with a message
            raise FileNotFoundError(f"The directory '{dir}' does not exist.")
            sys.exit(1)  # Exit the program with a status code of 1
        pattern = os.path.join(dir, '*.json')
        files = []
        for file_path in glob.glob(pattern):
            if "master_catalogue_list_final.json" not in file_path and \
                    "catalog_registry.json" not in file_path and \
                    "new_catalog_template.json" not in file_path:
                files.append(file_path)
        return(files)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)


def create_output_dir():
    # Specify the directory path you want to check and potentially create
    ouptut_dir = "catalog_format_updated"

    # Check if the directory exists
    if not os.path.exists(ouptut_dir):
        # The directory does not exist, create it
        os.makedirs(ouptut_dir)
        print(f"Output directory '{ouptut_dir}' was created.")
    else:
        # The directory already exists
        print(f"Output directory '{ouptut_dir}' already exists.")

def process_file(i, filename):
    print(f"Now processing #{i}: {filename} ")
    catalog_data = read_from_file(filename)
    try:
        if 'objectives' in catalog_data['catalogue'] or \
                'tests' in catalog_data['catalogue'] or \
                'ccis' in catalog_data['catalogue'] or \
                'parameters' in catalog_data['catalogue']:
            reformat_children(catalog_data)

        catalog_data_reformatted = {'catalog': catalog_data['catalogue']}

        purge_system_metadata(catalog_data_reformatted['catalog'])

        f_name, f_extension = os.path.splitext(os.path.basename(filename))
        with open('./catalog_format_updated/'+f_name + '_schema-v2.json', 'w') as f:
            json.dump(catalog_data_reformatted, f, indent=4)

    except KeyError:
        print(f"Error: The file '{filename}' did not follow the expected input format. Skipping.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def read_from_file(filename):
    try:
        with open(filename, 'r') as f:
            catalog_data = json.load(f)
            return catalog_data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{filename}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error reading from file occurred: {str(e)}")

def reformat_children(catalog_data):

    try:
        # convert controls to lookup friendly hashmap
        control_map = {}
        for control in catalog_data['catalogue']['securityControls']:
            key = control['id']
            control_map[key] = control # add record as value for this key

        # reformat parts
        if 'objectives' in catalog_data['catalogue']:
            for objective in catalog_data['catalogue']['objectives']:
                referenced_control = control_map[objective['securityControlId']]
                purge_system_metadata(objective)
                if 'objectives' not in referenced_control :
                    referenced_control['objectives'] = [objective]
                else:
                    referenced_control['objectives'].append(objective)

        if 'tests' in catalog_data['catalogue']:
            for test in catalog_data['catalogue']['tests']:
                referenced_control = control_map[test['securityControlId']]
                purge_system_metadata(test)
                if 'tests' not in referenced_control :
                    referenced_control['tests'] = [test]
                else:
                    referenced_control['tests'].append(test)

        if 'ccis' in catalog_data['catalogue']:
            for cci in catalog_data['catalogue']['ccis']:
                referenced_control = control_map[cci['securityControlId']]
                purge_system_metadata(cci)
                if 'ccis' not in referenced_control :
                    referenced_control['ccis'] = [cci]
                else:
                    referenced_control['ccis'].append(cci)

        if 'parameters' in catalog_data['catalogue']:
            for param in catalog_data['catalogue']['parameters']:
                referenced_control = control_map[param['securityControlId']]
                purge_system_metadata(param)
                if 'parameters' not in referenced_control :
                    referenced_control['parameters'] = [param]
                else:
                    referenced_control['parameters'].append(param)

        reformatted_controls_list = list(control_map.values())

        for control in reformatted_controls_list:
            purge_system_metadata(control)

        # remove from old position
        if 'objectives' in catalog_data['catalogue']:
            del catalog_data['catalogue']['objectives']
        if 'tests' in catalog_data['catalogue']:
            del catalog_data['catalogue']['tests']
        if 'ccis' in catalog_data['catalogue']:
            del catalog_data['catalogue']['ccis']
        if 'parameters' in catalog_data['catalogue']:
            del catalog_data['catalogue']['parameters']
    except Exception as e:
        print(f"An unexpected error occurred, possibly due to unexpected format: {str(e)}")

def purge_system_metadata(dict_record):
    try:
        if 'id' in dict_record:
            del dict_record['id']
        if 'isPublic' in dict_record:
            del dict_record['isPublic']
        if 'id' in dict_record:
            del dict_record['id']
        if 'archived' in dict_record:
            del dict_record['archived']
        if 'createdById' in dict_record:
            del dict_record['createdById']
        if 'lastUpdatedById' in dict_record:
            del dict_record['lastUpdatedById']
        if 'dateCreated' in dict_record:
            del dict_record['dateCreated']
        if 'dateLastUpdated' in dict_record:
            del dict_record['dateLastUpdated']
        if 'securityControlId' in dict_record:
            del dict_record['securityControlId']
        if 'tenantsId' in dict_record:
            del dict_record['tenantsId']
    except Exception as e:
        print(f"Problem cleaning unused metadata. An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
