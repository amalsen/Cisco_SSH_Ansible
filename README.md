# Cisco_SSH_Ansible
Pythonkode må kjøres før Ansible kjøres

## Nettverksoppsett
![Nettverk i Cisco Packet Tracer (images/network.png)](https://github.com/amalsen/Cisco_SSH_Ansible/blob/main/images/network.png "Nettverk i Cisco Packet Tracer")
Bilde av alle enhetene som er inkludert. Denne repoen benyttes kun for oppsettet lagt opp for student 2. Fremgangsmåten tar i utgangspunkt at datamaskinen som Ansible kjøres fra kjøres fra den øverste datamaskinen koblet til (MGMT).

## Python
### Forutsetninger
- Cisco-enheter
- Datamaskin med mulighet for serialkobling
- Windows eller Linux
- Pyserial installert
### Forberedelser
- Som standard er brukernavn for SSH og passord for SSH og enable "cisco".
  For å endre på dette må linjene 56-58 endres med å ta bort hardkodet verdier og fjerne kommentar for input.
  ```python
  uName = 'cisco' #input('Brukernavn for SSH: ')
  pWord = 'cisco' #input('Passord for SSH: ')
  pWordEn = 'cisco' #input('Passord for enable: ')
  ```
### Bruk
- Koble til Cisco-enhet via konsollkabel.
- Kjør koden med `python [stien til koden]/ssh.py`.
- Følg instruksene som dukker opp.
- Husk riktig navn på porter:
  ```
  Cisco 4221: Gig0/0/X
  Cisco 2901: Gig0/X
  Catalyst 1000 Series: Gig1/0/X
  Catalyst 2960 Series: Fa0/X
  Catalyst 3650: Gig1/0/X
  ```

## Ansible
### Forutsetninger
- Cisco-enheter med oppsatt SSH med bruk av `python/ssh.py`
- Linux med Ansible og Paramiko intallert fra brukeren som skal kjøre scriptene
- Om Ansible Core er installert med pipx:
  - Kjør `pipx inject ansible-core paramiko`
### Forberedelser
- Kopier mappen "ansible" til ditt hjemområde i Linux.
- Endre "user" i `collection_path` i `ansible/ansible.cfg` slik at den peker mot ditt hjemområde.
- Endre IP-adresser i `ansible/hosts` til IP-adressene du vil bruke.
  Standard IP mot MGMT-PC:
  ```
  cisco_router_one: 192.168.22.254
  cisco_router_two: 192.168.22.253
  cisco_switch_out: 192.168.22.200
  cisco_switch_in_one: 172.16.22.200
  cisco_switch_in_two: 172.16.22.201
  ```
- Endre `ansible_user` og `ansible_password` i `ansible/hosts` til det som er konfigurert med Python. Er det forskjeller mellom enhetene må disse verdiene legges manuelt for hver enhet i listen.
- Legge til flere konfigurasjoner om ønskelig. [Dokumentasjon til Ansible Cisco.Ios](https://docs.ansible.com/ansible/latest/collections/cisco/ios/index.html)
### Oppsett
- `ansible/cisco_router_one.yml`: Cisco 4221
- `ansible/cisco_router_two.yml`: Cisco 2901
- `ansible/cisco_switch_in_one.yml`: Catalyst 1000 Series
- `ansible/cisco_switch_in_two.yml`: Catalyst 2960 Series
### Bruk
- Kjør:
  1. `ansible-playbook ~/ansible/cisco_router_one.yml`
  2. `ansible-playbook ~/ansible/cisco_router_two.yml`
  3. `ansible-playbook ~/ansible/cisco_switch_in_one.yml`
  4. `ansible-playbook ~/ansible/cisco_switch_in_two.yml`