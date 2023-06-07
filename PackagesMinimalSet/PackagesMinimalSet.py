import subprocess


# Step 1: get all dependencies that are not installed in the base image
def dependencies_not_in_dockerimage(image, packages):
    result = []
    for i, package in enumerate(packages):
        try:
            cmd = "docker exec {} Rscript -e 'library({})'".format(image, package)
            res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            result.append(package)
    return result


# Step 2: get all dependencies that are necessary to run the script succesfully
def dependencies_to_be_installed(image, packages, code):
    result = []
    for i, package in enumerate(packages):

        # obtain all other packages and concat this as a string
        other_packages = [x for j, x in enumerate(packages) if j != i]
        pkg_str = "".join([("library({});".format(x)) for x in other_packages])

        try:
            cmd = "docker exec {} Rscript -e '{}{}'".format(user_container, pkg_str, code)
            res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            result.append(package)
    return result


def minimal_set_dependencies(base_image, user_container, packages, code):
    # Step 1
    candidate_packages = dependencies_not_in_dockerimage(base_image, packages)
    print("Candidate images: ", candidate_packages)

    # Step 2
    result = dependencies_to_be_installed(user_container, candidate_packages, code)
    print("Minimal set: ", result)
    return result


minimal_set_dependencies(
    "f3533c4dbecb",
    "c924abf79138",
    ["tidyselect", "readr", "stringi"],
    "read_csv(\"/home/jovyan/data.csv\")"
)
