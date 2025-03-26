
import sys

from tpweb.data.domain import Domain, DomainDoesNotExistError
from tpweb.func.user import do_user_exists
from tpweb.func.domain import do_domain_exists, is_valid_domain

def create(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin domain create [OPTIONS] <username> <domainname>")
        print()
        print("  Create a new user.")
        print()
        print("Options:")
        print("  --web   Create a new web domain.")
        print("  --dns   Create a new dns domain.")
        print("  --mail  Create a new mail domain.")
        print("  --template=webTemplate  Use a web template.")
        print("  --dns-template=dnsTemplate  Use a dns template.")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) < 2:
        print("Usage: tpweb-bin domain create [OPTIONS] <username> <domainname>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username = args[0]
    domainname = args[1]

    needs_web = "--web" in args
    needs_dns = "--dns" in args
    needs_mail = "--mail" in args

    webTemplate = None
    dnsTemplate = None
    
    #if has args that starts with --template=
    for arg in args:
        if arg.startswith("--template="):
            webTemplate = arg.split("=")[1]
            break

        if arg.startswith("--dns-template="):
            dnsTemplate = arg.split("=")[1]

            break

    if not needs_web and not needs_dns and not needs_mail:
        print("Error: No domain type specified.")
        sys.exit(1)

    # Check if user exists
    if do_user_exists(username) == False:
        print("Error: User %s does not exist." % username)
        sys.exit(1)

    # Check if domainname is valid (regex)
    if is_valid_domain(domainname) == False:
        print("Error: Invalid domain name.")
        sys.exit(1)

    # Check if domain already exists
    domain = Domain()
    already_exists = False
    try :
        domainData=domain.get(domainname)
        if domainData:
            already_exists = True
    except DomainDoesNotExistError:
        pass

    if already_exists:
        print("Error: Domain %s already exists." % domainname)
        sys.exit(1)

    # Create domain
    domain.create(username, domainname, Web=needs_web, DNS=needs_dns, Mail=needs_mail, webTemplate=webTemplate, dnsTemplate=dnsTemplate)