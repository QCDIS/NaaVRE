import requests
import re
import json

# Set the search query and API URL
query = "topic:r-package language:R"
url = "https://api.github.com/search/repositories?q={}".format(query)

# Make the API request
response = requests.get(url)

# Check the response status code
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print(json.dumps(data["items"], indent=4))

    # Extract the list of package names from the response
    # repo["owner"]["login"] to get the owner
    packages = [repo["name"] for repo in data["items"]]

    # Print the list of packages
    print(packages)
else:
    print("Error: Unable to retrieve packages from GitHub.")
