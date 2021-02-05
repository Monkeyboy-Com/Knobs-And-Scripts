# vcs_github.py - KAS version control functions for GitHub

import os
import pwd
import shutil
import socket
import subprocess
import sys
from datetime import datetime

import yaml

from github import Github


# ------- create -------
def create(archive, repo, flavor, url, name, token, is_private):
    now = datetime.now()
    stamp = now.strftime("%d-%b-%Y %H:%M:%S")
    login = pwd.getpwuid(os.getuid())[0]
    target = archive + os.sep + repo

    # make sure git is available
    path = shutil.which('git')
    if len(path) < 1:
        print('ERROR: cannot find git')
        sys.exit(1)

    # change to the kas target root directory
    os.chdir(target)

    # init the git repo if it does not exist
    created = False
    if not os.path.exists(target + os.sep + ".git"):
        print(" + ", end='', flush=True)
        result = subprocess.run(["git", "init"])
        if result.returncode != 0:
            print(f"ERROR: {result.stdout}")
            sys.exit(3)
        created = True
    else:
        print(f" = local repo {repo} already exists")

    # create a README.md if it does not exist
    path = target + os.sep + "README.md"
    if not os.path.exists(path):
        text = f"# KAS - Knobs And Scripts repository\n" \
               f"Created: {stamp} by {login}<br/>\n" \
               f"Host: {socket.gethostname()}\n"
        with open(path, 'w') as o:
            o.writelines(text)
        print(f" + created new README.md")

    # add README.md
    print(' = Attempting to add README.md')
    result = subprocess.run(["git", "add", path])
    if result.returncode != 0:
        print(f"ERROR: {result.stdout}")
        sys.exit(3)

    # commit
    print(' = Attempting to commit')
    if created:
        text = "KAS initial commit"
    else:
        text = "KAS commit"
    subprocess.run(["git", "commit", "-m", text])  # ignore any errors

    # set the branch name to default main
    print(' = Attempting to set branch name to main')
    result = subprocess.run(["git", "branch", "-M", "main"])
    if result.returncode != 0:
        print(f"ERROR: {result.stdout}")
        sys.exit(3)

    # create the new repo on GitHub
    if flavor == 'github':
        print(' = Existing GitHub repos:')
        g = Github(token)
        for there in g.get_user().get_repos():
            print("     " + there.name)
            if there.name == repo:
                print(f"ERROR: GitHub repo {repo} already exists")
                sys.exit(2)

        print(f"Attempting to create repo '{repo}' on GitHub")
        user = g.get_user()
        added = user.create_repo(repo, 'KAS repository', '', is_private)
        origin = added.clone_url
    else:
        if url[len(url - 1):] != "/":
            url += '/'
        origin = url + name

    # set the origin
    print(' = Attempting to set the remote origin')
    result = subprocess.run(["git", "remote", "add", "origin", origin])
    if result.returncode != 0:
        text = result.stdout
        if text != 'None':
            print(f"ERROR: {text}")
        sys.exit(3)

    source = 'https://' + token + '@github.com/' + name + '/' + repo + '.git'

    # push set upstream branch
    print(' = Attempting to push')
    result = subprocess.run(["git", "push", "--set-upstream", source, "main"])
    if result.returncode != 0:
        print(f"ERROR: {result.stdout}")
        sys.exit(3)

# To update repo:
#   git add [file]
#   git commit -m 'message'
#   git push

# ------- read_meta -------
def read_meta(archive, repo):
    file = archive + os.sep + repo + '.yaml'
    if not os.path.exists(file):
        print(f"ERROR: cannot find repo metadata file: {file}")
        sys.exit(3)

    print(f" = Reading metadata: {file}")
    with open(file) as m:
        meta = yaml.load(m, Loader=yaml.FullLoader)

    print(meta.get('flavor'))
    print(meta.get('url'))
    print(meta.get('repo'))
    print(meta.get('name'))
    print(meta.get('token'))
    print(meta.get('private'))