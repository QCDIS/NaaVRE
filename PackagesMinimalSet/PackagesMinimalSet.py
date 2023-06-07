
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