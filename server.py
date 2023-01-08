import socket
import signal
import sys
import random

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port
# Default: Login page.
login_page = "<h1>Please Login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % port

#### Helper functions
# Printing.
def print_value(tag, value):
    print("Here is the", tag)
    print("\"\"\"")
    print(value)
    print("\"\"\"")
    print

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)

# TODO: put your application logic here!
password_Dictionary = {}
secret_Dictionary = {}
cookie_Dictionary = {}
passFile = open('passwords.txt', 'r')
secretFile = open ('secrets.txt', 'r')

# Read login credentials for all the users
for passLine in passFile:
    splitLine1 = passLine.split()
    password_Dictionary[splitLine1[0]] = splitLine1[1]

# Read secret data of all the users
for sLine in secretFile:
    splitLine2 = sLine.split()
    secret_Dictionary[splitLine2[0]] = splitLine2[1]

### Loop to accept incoming HTTP connections and respond.
while True:
    client, addr = sock.accept()
    req = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = req.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)

    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions

    # You need to set the variables:
    # (1) `html_content_to_send` => add the HTML content you'd
    # like to send to the client.
    # Right now, we just send the default login page.
    html_content_to_send = login_page
    # But other possibilities exist, including
    # html_content_to_send = success_page + <secret>
    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page
    
    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.
    headers_to_send = ''

    list1 = []
    list2 = []
    username = ""
    password = ""

    headerList = headers.split('\n')
    numOfHeaders = len(headerList)
    lastLine = headerList[numOfHeaders-1].split(" ")

    if lastLine[0] == "Cookie:":
        #There exists a cookie
        token = lastLine[1].split("=")
        cookieNum = token[1]

        if len(cookie_Dictionary) != 0 and token[0] == "token":
            #There are cookies
            if cookieNum in cookie_Dictionary:
                if body == "action=logout":
                    headers_to_send = 'Set-Cookie: token=' + cookieNum + '; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n'
                else:
                    html_content_to_send = success_page + cookie_Dictionary.get(cookieNum)
            else:
                html_content_to_send = bad_creds_page
        else:
            #There are no cookies in the cookie dictionary so it can't possibly be a correct cookie or the cookie isnt a token
            if body != "":
                if body == "action=logout":
                    html_content_to_send = logout_page
                else:
                    list1 = body.split('=')
                    list2 = list1[1].split('&')
                    username = list2[0]
                    password = list1[2]

                    if username in password_Dictionary:
                        if password in password_Dictionary.values():
                            #Both the username and password exist in the dictionary
                            if password_Dictionary.get(username) == password:
                                #CASE A:
                                #Username and Password is correct (SUCCESS!!!)
                                html_content_to_send = success_page + secret_Dictionary.get(username)
                                rand_val = random.getrandbits(64)
                                headers_to_send = 'Set-Cookie: token=' + str(rand_val) + '\r\n'
                        
                                #Stores Secret in Cookie Dictionary to bypass User Authentication
                                cookie_Dictionary[str(rand_val)] = secret_Dictionary.get(username)
                            else:
                                html_content_to_send = bad_creds_page
                        else:
                            html_content_to_send = bad_creds_page
                    else:
                        html_content_to_send = bad_creds_page 
    else:
        #Cookie header is absent
        if body != "":
            if body == "action=logout":
                html_content_to_send = logout_page
            else:
                list1 = body.split('=')
                list2 = list1[1].split('&')
                username = list2[0]
                password = list1[2]

                if username in password_Dictionary:
                    if password in password_Dictionary.values():
                        #Both the username and password exist in the dictionary
                        if password_Dictionary.get(username) == password:
                            #CASE A:
                            #Username and Password is correct (SUCCESS!!!)
                            html_content_to_send = success_page + secret_Dictionary.get(username)
                            rand_val = random.getrandbits(64)
                            headers_to_send = 'Set-Cookie: token=' + str(rand_val) + '\r\n'
                        
                            #Stores Secret in Cookie Dictionary to bypass User Authentication
                            cookie_Dictionary[str(rand_val)] = secret_Dictionary.get(username)

                        else:
                            html_content_to_send = bad_creds_page
                    else:
                        html_content_to_send = bad_creds_page
                else:
                    html_content_to_send = bad_creds_page
    
    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)    
    client.send(response)
    client.close()
    
    print("Served one request/connection!")
    print

# We will never actually get here.
# Close the listening socket
sock.close()