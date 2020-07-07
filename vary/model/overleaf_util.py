# from bs4 import BeautifulSoup # Useful if we use an accoun t or retrieve the CSRF token from the login page
import requests
import re
import json
import zipfile
import os

def fetch_overleaf(invite_key, output_folder):
    """
    Gets the content of a LaTeX project on Overleaf, from a READ-ONLY invite link and exports it to the output folder
    """

    if not re.match("[a-z]+", invite_key):
        os.write(2, b"This is not a valid invite key. The invite key is the group of letters after the '/read/' in the read-only link\n")
        exit()

    invite_url = "https://www.overleaf.com/read/" + invite_key
    grant_url = invite_url + "/grant"
    session = requests.Session()



    # Login
    # Not necessary unless you want to import a project with a read / write link
    # 
    # email = INSERT EMAIL
    # password = INSERT PASSWORD
    # login_url = "https://www.overleaf.com/login"
    # r = session.get(login_url)
    # csrf = BeautifulSoup(r.text, 'html.parser').find('input', { 'name' : '_csrf' })['value']
    # r = session.post(login_url, { '_csrf' : csrf , 'email' : email , 'password' : password })

    # Loads the invite page on the website to get the cookies
    r = session.get(invite_url)

    # Headers of the post request
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Host": "www.overleaf.com",
        "Origin" : "https://www.overleaf.com",
        "TE": "Trailers",
        "Content-Length": "48"
    }

    # CSRF token used to validate the POST request
    csrf = re.search('window.csrfToken = "([^"]*)";', r.content.decode("utf-8")).group(1)

    # Solution without having to search for the csrf token in the javascript page
    # It seems to be possible to use the csrf token found on the login page to do the post
    #
    # r = session.get(login_url)
    # csrf = BeautifulSoup(r.text, 'html.parser').find('input', { 'name' : '_csrf' })['value']

    data = '{"_csrf":"%s"}' % csrf

    # POST request that allows the user to access the document
    r = session.post(
        grant_url,
        data = data,
        cookies = session.cookies,
        headers = headers
    )

    # Real path of the project
    project_path = json.loads(r.content)['redirect']

    zip_name = "sources.zip"
    download_url = "https://www.overleaf.com%s/download/zip" % project_path
    # Download the project
    r = session.get(download_url, stream=True)
    # Write the response to a zip file
    with open(zip_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)

    # Extract the file to the specified folder
    with zipfile.ZipFile("sources.zip","r") as zip_ref:
        zip_ref.extractall(output_folder)

    # Clean the archive
    os.remove(zip_name)