# Noe som kanskje må gjøres før kjøring av scriptet fra Ubuntu i WSL
#   1. I kommandolinje på Windows:
#           wsl --set-version Ubuntu 1
#   2. I Ubuntu (eller annen distro):
#           sudo chmod 777 /dev/ttyS*

# Portnavn for enkelte Cisco-enheter brukt:
# Cisco 4221: Gig0/0/X
# Cisco 2901: Gig0/X
# Catalyst 1000 Series: Gig1/0/X
# Catalyst 2960 Series: Fa0/X
# Catalyst 3650: Gig1/0/X

import paramiko
import serial
import time
import sys

def main():
    # Oppretter en tilkobling til Cisco-enheten basert på OS. Kan kjøres fra Windows og Linux.
    while True:
        os = int(input('OS scriptet kjoeres fra (1: Windows, 2: Linux): '))
        if os == 1:
            portNum = input('Portnummer (COM<num>): ')
            consolePort = 'COM'+portNum
            break
        elif os == 2:
            portNum = input('Portnummer (ttyS<num>): ')
            consolePort = '/dev/ttyS'+portNum
            break
        else:
            print('OS er ikke valgt.')
    try:
        console = serial.Serial(
            port=consolePort,
            baudrate=9600,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=8
        )
    except serial.serialutil.SerialException as e:
        print('Feil med aa koble til enheten...')
        sys.exit()
    else:
        #Velger hva som skal konfigureres.
        while True:
            device = int(input('Enhet som skal settes opp (1: Ruter, 2: Svitsj): '))
            if device == 1 or 2:
                break
            else:
                print('Enhet er ikke valgt.')
        print('Gjoer klar til SSH konfigurasjon:')
        hostname = input('Hostname til enhet: ')
        # Standard brukernavn og passord er "cisco". Kan legge til eget med å fjerne hardkodet brukernavn og passord, og fjerne kommentaren til inputen.
        uName = 'cisco' #input('Brukernavn for SSH: ')
        pWord = 'cisco' #input('Passord for SSH: ')
        pWordEn = 'cisco' #input('Passord for enable: ')
        if device == 1:
            while True:
                subInt = int(input('Skal subinterface konfigureres? ANBEFALT! (Ja: 1, Nei: 2): '))
                if subInt == 1:
                    print('Legger til VLAN, dette vil bli brukt til Management.')
                    vlanID = int(input('VLAN-ID (integer): '))
                    break
                elif subInt == 2:
                    break
                else:
                    print('Valg er ikke tatt, vennligst velg et av alternativene.')
        elif device == 2:
            print('Legger til VLAN, dette vil bli brukt til Management.')
            vlanID = int(input('VLAN-ID (integer): '))
            vlanName = input('Navn paa VLAN: ')
        else:
            print('Ukjent feil har oppstaatt. Vennligst start paa nytt.')
            sys.exit()
        if device == 2:
             while True:
                intConfig = int(input('Skal det konfigureres access paa en port (Ja: 1, Nei: 2): '))
                if intConfig == 1:
                    interface = input('Port til enhet (Eks. Gig1/0/1, Gig0/1, Fa0/1): ')
                    break
                elif intConfig == 2:
                    break
                else:
                    print('Feil input er skrevet, svar paa nytt.')
        else:
            interface = input('Port til enhet (Eks. Gig1/0/1, Gig0/1, Fa0/1): ')
        ip = input('IP-adresse: ')
        subnet = input('Subnettmaske: ')
        if device == 2:
            defaultGateway = input('Default Gateway som svitsj skal ha: ')
            while True:
                trunk = int(input("Skal alle portene starte med trunk (Ja: 1, Nei: 2): "))
                if trunk == 1:
                    print("Navn paa porter som skal ha trunk uten siste nummer paa port.")
                    print("'/1' blir automatisk lagt til etter.")
                    portName = input("(Eksempel på hva som skal skrives: 'Gig1/0', 'Gig0', 'Fa0'): ")
                    while True:
                        try:
                            intRange = int(input("Antall porter: "))
                            break
                        except TypeError:
                            print("Et heltall maa skrives, proev paa nytt.")
                    break
                elif trunk == 2:
                    break
                else:
                    print('Du har ikke valgt gyldig. Proev paa nytt.')
            #while True:
            #    dL2L3 = int(input('Type svitsj (L2: 2, L3: 3):' ))
            #    if dL2L3 == 2 or 3:
            #        break
            #    else:
            #        print('Du har ikke valgt gyldig. Proev paa nytt.')
        else:
            pass

        initialConf = '\r\n\r\nno\r\nyes\r\n\r\n\r\n'
        wrMem = '\r\nend\r\nwr mem\r\n'
        confSSH = f'\r\nend\r\nconf t\r\nip domain-name cisco.local\r\ncrypto key generate rsa modulus 2048\r\n{time.sleep(3)}\r\nip ssh version 2\r\nusername {uName} privilege 15 secret {pWord}\r\nline vty 0 15\r\ntransport input ssh\r\nlogin local\r\n'
        logoff = f'\r\nend\r\nexit\r\n'

            # Konfigurasjoner for rutere:
        if device == 1:
            confStart = f'\r\nen\r\nconf t\r\nno ip domain-lookup\r\nhostname {hostname}\r\nenable secret {pWordEn}\r\n'
            confIntSub = f'\r\nend\r\nconf t\r\nint {interface}.{vlanID}\r\nencapsulation dot1Q {vlanID}\r\nip address {ip} {subnet}\r\nno shutdown\r\nint {interface}\r\nno shutdown\r\n'
            confIntNoSub = f'\r\nend\r\nconf t\r\nint {interface}\r\nip address {ip} {subnet}\r\nno shutdown\r\n'

            console.write(initialConf.encode())
            time.sleep(15)
            console.write(confStart.encode())
            time.sleep(1)
            if subInt == 1:
                console.write(confIntSub.encode())
            else:
                console.write(confIntNoSub.encode())
            time.sleep(1)
            console.write(confSSH.encode())
            time.sleep(3)
            console.write(wrMem.encode())
            time.sleep(1)
            console.write(logoff.encode())

            output = console.read(255).decode()
            print(output)

            # Konfigurasjoner for svitsjer:
        elif device == 2:
            confStartL2 = f'\r\nen\r\nconf t\r\nno ip domain-lookup\r\nhostname {hostname}\r\nenable secret {pWordEn}\r\nvlan {vlanID}\r\nname {vlanName}\r\nexit\r\ninterface vlan {vlanID}\r\nip address {ip} {subnet}\r\nno shutdown\r\nexit\r\nip default-gateway {defaultGateway}\r\n'
            #confStartL3 = f''
            confTrunk = f'\r\nend\r\nconf t\r\nint range {portName}/1-{intRange}\r\nswitchport mode trunk\r\n'
            if intConfig == 1:
                confInt = f'end\r\nconf t\r\nint {interface}\r\nswitchport mode access\r\nswitchport access vlan {vlanID}\r\nno shutdown\r\n'

            console.write(initialConf.encode())
            time.sleep(15)
            #if dL2L3 == 2:
            console.write(confStartL2.encode())
            #else:
            #    console.write(confStartL3.encode())
            time.sleep(1)
            if trunk == 1:
                console.write(confTrunk.encode())
            time.sleep(1)
            if intConfig == 1:
                console.write(confInt.encode())
            time.sleep(1)
            # console.write(confStartL2.encode())
            # time.sleep(1)
            console.write(confSSH.encode())
            time.sleep(3)
            console.write(wrMem.encode())
            time.sleep(1)
            console.write(logoff.encode())

            output = console.read(255).decode()
            print(output)
        else:
            print('Ukjent feil oppsto. Vennligst start paa nytt.')
            sys.exit()


if __name__ == '__main__':
    main()