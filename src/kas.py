# KAS : Knobs And Scripts

import getopt
import getpass
import os
import pwd
import signal
import sys
from datetime import datetime

import cfg

# Globals
global archive  # directory of repo(s), where it is all kept
global base  # directory of this executable
global flavor  # type of vcs, if any
global index  # sys.argv index
global repo  # the specific fileset location, with or without a vcs
global url  # the url of the optional vcs
global version  # this executable version
global versioned  # is a vcs being used, True/False


# ------- banner -------
def banner():
    print(f"KAS: Knobs And Scripts, version {version}")


# ------- create -------
# kas create [-g|--git|-h|--github] [-p|--private] [-u|--url url] [-n|--name username] [-t|--token token] [-r repo]
def create():
    global archive, flavor, index, repo, url, versioned

    print('action: create')
    is_git = False
    is_github = False
    is_private = False
    url = ''
    name = ''
    token = ''
    token_prompted = False
    repo = ''
    vcs = None

    now = datetime.now()
    stamp = now.strftime("%d-%b-%Y %H:%M:%S")
    login = pwd.getpwuid(os.getuid())[0]

    try:
        #noinspection SpellCheckingInspection
        options = 'ghpu:n:t:r:'
        long_opts = ['git', 'github', 'private', 'url=', 'name=', 'token=', 'repo=']
        opts, args = getopt.getopt(sys.argv[index:], options, long_opts)
    except getopt.error as msg:
        print(f"ERROR: {msg}")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-g', '--git'):
            flavor = 'git'
            is_git = True
        elif opt in ('-h', '--github'):
            flavor = 'github'
            is_github = True
        elif opt in ('-p', '--private'):
            is_private = True
        elif opt in ('-u', '--url'):
            url = arg
        elif opt in ('-n', '--name'):
            name = arg
        elif opt in ('-t', '--token'):
            token = arg
        elif opt in ('-r', '--repo'):
            repo = arg
        else:
            print(f"ERROR: unknown create option: " + opt)
            sys.exit(2)

    # sanity checks
    if is_git and is_github:
        print("ERROR: can only use --git or --github, not both")
        sys.exit(2)

    if is_git or is_github:
        import vcs_github as vcs
        versioned = True
        if len(url) == 0:
            print("ERROR: --url required")
            sys.exit(2)
        if len(name) == 0:
            print("ERROR: --name required")
            sys.exit(2)
        if len(token) == 0:
            token_prompted = True
            token = vcs.prompt_token()

    if is_private and not is_github:
        print("WARNING: --private is only used wit --github")

    if len(repo) == 0:
        repo = getpass.getuser() + '_' + sys.platform
        print(f" ! repo name not specified, using default: {repo}")

    # create the archive + repo directory
    target = archive + os.sep + repo
    if not os.path.exists(target):
        os.makedirs(target, exist_ok=True)
        print(f" + created archive directory: {target}")
    else:
        print(f" = archive directory exists: {target}")

    # create a README.md if it does not exist
    path = target + os.sep + "README.md"
    if not os.path.exists(path):
        text = f"# KAS - Knobs And Scripts repository\n" \
               f"### Created: {stamp} by {login}<br/>\n" \
               f"#### Place fully-qualified file paths and/or directories below these comments.<br/>\n" \
               f"#### Blank lines and lines beginning with # are ignored.<br/>\n\n"
        with open(path, 'w') as o:
            o.writelines(text)
        print(f" + created new README.md")

    # create the git or github repo
    if versioned:
        print(f" = vcs type: {flavor}")
        vcs.create(archive, repo, flavor, url, name, token, is_private)

    # create the metadata yaml file
    now = datetime.now()
    stamp = now.strftime("%d-%b-%Y %H:%M:%S")
    login = pwd.getpwuid(os.getuid())[0]
    yaml = archive + os.sep + repo + '.yaml'
    if not os.path.exists(yaml):
        text = ''
        if not token_prompted:
            text = token
        meta = f"# KAS repository {repo} metadata\n" \
               f"# Created: {stamp} by {login}\n" \
               f"flavor: {flavor}\n" \
               f"url: {url}\n" \
               f"repo: {repo}\n" \
               f"name: {name}\n" \
               f"token: {text}\n" \
               f"private: {is_private}\n"
        with open(yaml, 'w') as o:
            o.writelines(meta)


# ------- collect -------
# kas collect [-r repo]
def collect():
    global archive, index, repo

    print('action: collect')
    repo = ''

    try:
        options = 'r:'
        long_opts = ['repo=']
        opts, args = getopt.getopt(sys.argv[index:], options, long_opts)
    except getopt.error as msg:
        print(f"ERROR: {msg}")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-r', '--repo'):
            repo = arg
        else:
            print(f"ERROR: unknown create option: " + opt)
            sys.exit(2)

    # sanity checks
    if len(repo) == 0:
        repo = getpass.getuser() + '_' + sys.platform
        print(f" ! repo name not specified, using default: {repo}")

    import local
    local.collect(archive, repo)


# ------- commit -------
def commit():
    print('action: commit')


# ------- distribute -------
# kas distribute [-r repo]
def distribute():
    global archive, index, repo

    print('action: distribute')
    repo = ''

    try:
        options = 'r:'
        long_opts = ['repo=']
        opts, args = getopt.getopt(sys.argv[index:], options, long_opts)
    except getopt.error as msg:
        print(f"ERROR: {msg}")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-r', '--repo'):
            repo = arg
        else:
            print(f"ERROR: unknown create option: " + opt)
            sys.exit(2)

    # sanity checks
    if len(repo) == 0:
        repo = getpass.getuser() + '_' + sys.platform
        print(f" ! repo name not specified, using default: {repo}")

    import local
    local.distribute(archive, repo)


# ------- pull -------
def pull():
    print('action: pull')


# ------- push -------
def push():
    print('action: push')


# ------- setup -------
def setup():
    global repo

    print('action: setup')

    try:
        options = 'r:'
        long_opts = ['repo=']
        opts, args = getopt.getopt(sys.argv[index:], options, long_opts)
    except getopt.error as msg:
        print(f"ERROR: {msg}")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-r', '--repo'):
            repo = arg
        else:
            print(f"ERROR: unknown create option: " + opt)
            sys.exit(2)

    if len(repo) < 1:
        repo = os.path.expanduser('~') + os.sep + 'kas-archive'
        print(f" ! repo directory not specified, using default: {repo}")

    if len(archive) > 0:
        answer = input(f"archive {archive} is already setup. Do you want to change it (y/N)? ")
        answer = answer.lower()
        if not answer == 'y':
            return

    cfg.setup(repo)


# ------- signal_handler -------
def signal_handler(sig, frame):
    print(f"\nExiting ELS\n")
    sys.exit(0)


# ------- usage -------
def usage():
    print()
    print("usage")
    sys.exit(1)


# ------- main --------------------------------------------------------------
if __name__ == '__main__':

    # initialize
    archive = ''
    index = 1
    flavor = 'none'
    version = 1.0
    versioned = False

    signal.signal(signal.SIGINT, signal_handler)
    #print('Press Ctrl+C')
    #signal.pause()

    # get the base executable directory
    base = os.path.dirname(__file__)
    base = os.path.dirname(base)
    base = os.path.abspath(base)

    banner()
    print(f" = base: {base}")

    cmd = '-'
    if len(sys.argv) > index:
        # get the command
        cmd = sys.argv[index]
        index += 1

        # read the .kas configuration
        file = cfg.find(base)
        if len(file) > 0:
            kas = cfg.get(file)
            archive = kas.get('archive')
            if len(archive) == 0:
                print(f"ERROR: configuration file {file} has an empty archive definition")
                sys.exit(1)
            print(f" = archive directory: {archive}")
        else:
            if not cmd == 'setup':
                print("ERROR: configuration file .kas cannot be found. Use: kas setup [directory]")
                sys.exit(1)

        # vcs commands -------
        print()
        if cmd == 'create':
            create()
        elif cmd == 'pull':
            pull()
        elif cmd == 'commit':
            commit()
        elif cmd == 'push':
            push()
        # kas commands -------
        elif cmd == 'collect':
            collect()
        elif cmd == 'distribute':
            distribute()
        elif cmd == 'setup':
            setup()
        else:
            print(f"ERROR: unknown action: {cmd}")
            usage()
    else:
        usage()

# end
