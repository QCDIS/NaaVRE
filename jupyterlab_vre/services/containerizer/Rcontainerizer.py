import os

# TODO: create an interface for other programming languages

def get_type(value):
    if value == "str" or value == "list":
        return "character"
    elif value == "int":
        return "integer"
    elif value == "float":
        return "numeric"
    else:
        raise ValueError("Not a valid type")

class Rcontainerizer:

    @staticmethod
    def get_files_info(cell=None, image_repo=None, cells_path=None):
        if not os.path.exists(cells_path):
            os.mkdir(cells_path)
        cell_path = os.path.join(cells_path, cell.task_name)

        cell_file_name = cell.task_name + '.R'
        dockerfile_name = 'Dockerfile.' + image_repo + '.' + cell.task_name

        if os.path.exists(cell_path):
            for files in os.listdir(cell_path):
                path = os.path.join(cell_path, files)
                if os.path.isfile(path):
                    os.remove(path)
        else:
            os.mkdir(cell_path)

        cell_file_path = os.path.join(cell_path, cell_file_name)
        dockerfile_file_path = os.path.join(cell_path, dockerfile_name)
        return {'cell': {
            'file_name': cell_file_name,
            'path': cell_file_path},
            'dockerfile': {
                'file_name': dockerfile_name,
                'path': dockerfile_file_path}
        }

    @staticmethod 
    def build_templates(cell=None, files_info=None):
  
        # create the source code file
        with open(files_info['cell']['path'], "w") as file:
            file.write("setwd('/app') \n\n")

            # we also want to always add the id to the input parameters
            inputs = cell.inputs 
            types = cell.types
            inputs.append('id')
            types['id'] = 'str'
            print("inputs: ", cell.inputs)
            print("types: ", cell.types)
            print("outpus ", cell.outputs)

            # we should dynamically add this value to the script
            # this is done using the 'optparse' library, which does something similar as in the Python script
            file.write("# retrieve input parameters\n")
            file.write("library(optparse) \n")
            file.write("option_list = list( \n")

            for i, (value) in enumerate(inputs):
                my_type = get_type(types[value])
                file.write('''\t make_option(c("--{}"), action="store", default=NA, type='{}', help="my description")'''.format(value, my_type)) # https://gist.github.com/ericminikel/8428297
                
                if i != len(inputs) - 1:
                    file.write(",")
                file.write("\n")
            
            # TODO: in the jinja template this step is also repeated for params, but in my script it seems that params are already included in the inputs?

            file.write(")\n\n")
            file.write("# set input parameters accordingly \n")
            file.write("opt = parse_args(OptionParser(option_list=option_list)) \n")

            # replace inputs
            file.write("library(jsonlite) \n")
            original_source = cell.original_source
            for value in inputs:
                file.write('''{} = fromJSON(opt${}) \n'''.format(value, value))
            file.write("\n")

            # check that the fields are set
            file.write("# check if the fields are set \n")
            for value in inputs: 
                file.write("if(is.na({}){{ \n".format(value))
                file.write("   stop('the `{}` parameter is not correctly set. See script usage (--help)') \n".format(value))
                file.write("}\n")
            file.write("\n")

            # print source
            file.write("# source code \n")
            file.write(original_source)

            # outputs
            outputs = cell.outputs # TODO: retrieve this dynamically

            if len(outputs) > 0:
                file.write("\n\n# capturing outputs \n")
                for out in outputs:
                    file.write("file <- file(paste0('/tmp/{}_', id, '.json')) \n".format(out))
                    file.write("writeLines(toJSON({}, auto_unbox=TRUE), file) \n".format(out))
                    file.write("close(file) \n")

        # create the Dockerfile
        with open(files_info['dockerfile']['path'], "w") as file:
            
            # Step 1: base image.
            file.write("FROM {}\n\n".format(cell.base_image))
            file.write("USER root \n\n") # in case of this image, we need root permissions

            # Step 2: install dependencies. for now, a naive way
            print(cell.dependencies)
            for dep in cell.dependencies:
                file.write('''RUN R -e "install.packages('{}', repos='http://cran.rstudio.com')" \n'''.format(dep['name']))
            file.write("\n")

            file.write("RUN mkdir -p /app \n")
            file.write("COPY {} /app".format(files_info['cell']['file_name']))

