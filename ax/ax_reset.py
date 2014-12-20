#!/usr/bin/env python

import subprocess
import tempfile
import time

import config

class AxSSH(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def _ssh(self, commands):
        t = tempfile.TemporaryFile()
        ssh = subprocess.Popen(['ssh', "%s@%s" % (self.user, self.host)],
                               close_fds=True,
                               shell=False,
                               stdin=subprocess.PIPE,
                               stdout=t)

        ssh.stdin.writelines(commands)
        ssh.wait()

        t.flush()
        t.seek(0)
        lines = t.readlines()
        t.close()

        return lines[4:-3]

    def config_get(self, acos_commands):
        commands = ['en\r\n',
                    '\r\n',
                    'terminal length 0\r\n']
        commands += acos_commands
        commands += ['exit\r\n',
                     'exit\r\n',
                     'y\r\n']

        print commands
        lines = self._ssh(commands)
        print lines
        trim = []
        for line in lines:
            x = line.strip()
            if x == '' or x[0] == '!':
                continue
            trim.append(line)
        return trim

    def config_gets(self, commands):
        return ''.join(self.config_get(commands))

    def erase(self):
        commands = [
            'config\r\n',
            'erase preserve-management preserve-accounts reload\r\n',
            'y\r\n',
            '\r\n',
            #'web-service server\r\n',
            #'web-service port 8080\r\n',
            #'web-service secure-server\r\n',
            #'web-service secure-port 8443\r\n',
            #'write mem\r\n',
            'end\r\n',
        ]
        self.config_gets(commands)

    def enable_web(self):
        commands = [
            'config\r\n',
            'web-service server\r\n',
            'web-service port 8080\r\n',
            'web-service secure-server\r\n',
            'web-service secure-port 8443\r\n',
            'write mem\r\n',
            'end\r\n',
        ]
        self.config_gets(commands)

    def reboot(self):
        commands = [
            'reboot\r\n',
            'yes\r\n',
            'yes\r\n'
        ]
        self.config_gets(commands)

    def show_run(self):
        return self.config_gets(['show run\r\n'])


if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], 'admin', 'nopass')
    ax.erase()
    time.sleep(60)

    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], 'admin', 'nopass')
    ax.enable_web()
    print(ax.show_run())