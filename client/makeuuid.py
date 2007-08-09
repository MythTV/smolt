from sys import argv

if __name__ == "__main__":
    hw_uuid_file = argv[1]
    try:
        uuid = file(hw_uuid_file).read().strip()
    except IOError:
        try:
            uuid = file('/proc/sys/kernel/random/uuid').read().strip()
            file(hw_uuid_file, 'w').write(uuid)
        except IOError:
            sys.stderr.write('Unable to determine UUID of system!\n')
            sys.exit(1)
