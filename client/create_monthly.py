from string import Template
from random import randint

cron_file = Template('''# Runs the smolt checkin client
# Please note that calling with -c will cause smolt to pause a random amount of
# time between 0 and 3 days before actually sending, this is to prevent ddos on
# the server
$minute $hour $day * * smolt /usr/bin/smoltSendProfile -c > /dev/null 2>&1
''')

def main():
    minute = randint(0,59)
    hour = randint(0, 24)
    day = randint(0, 28) #account for febu-hairy
    
    print cron_file.substitute(minute=minute, day=day, hour=hour)
    
if __name__ == '__main__':
    main()