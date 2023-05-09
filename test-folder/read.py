import json
import rpy2.robjects as robjects
import requests

static_repos = [{
    "name": "CRAN",
    "file": "cranPackages"
}, {
    "name": "BioConductor",
    "file": "bioconductorPackages"
}, {
    "name": "R-Forge",
    "file": "rforgePackages"
}]

# Load the JSON string from a file
def packages_repositories():
    for i, repo in enumerate(static_repos):
        with open('{}.json'.format(repo['file']), 'r') as f:
            json_string = f.read()
            packages = json.loads(json_string)
            repos[i]['len_packages'] = len(packages)
            repos[i]['packages'] = packages
    return repos

def get_package_details(package):

    # Step 1: Check kernel
    try:
        return dict(zip(list(resultRKernel.names), list(resultRKernel))) # TODO: make it more readable
    except:
        print("Not locally, proceed...")

    # Step 2: Check Repository MetaData
    repos = packages_repositories()
    for repo in repos:
        if package in repo['packages']:
            return {
                'repository': repo['name'] # TODO: add more metadata
            }
    
    # Step 3: Check GitHub
    query = "topic:r-package language:R {}".format(package)
    url = "https://api.github.com/search/repositories?q={}".format(query)
    response = requests.get(url)
    try:
        if response.status_code != 200:
            raise Exception("")

        # Parse the JSON response
        data = response.json()
        items = data["items"]

        # check if there are results
        if len(items) == 0:
            raise Exception("")

        # Naive way: grab the first repository
        repo = items[0]
        return {
            'repository': "GitHub",
            'full_package_name': repo["full_name"]
        }
    except Exception as e:
        a = 1
    return "Error: The package cannot be found"



#print(get_package_details("adegenet"))
print(get_package_details("mariokart"))
# get_package_details("dplyr")

# print("package diference: ", len(reps[1]['packages']) - len(reps[0]['packages']))
# print(len(set(reps[1]['packages']) - set(reps[0]['packages'])))
# print(len(set(reps[0]['packages']) - set(reps[1]['packages'])))