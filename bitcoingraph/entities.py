import bisect
import csv
import os


class Address:

    counter = 0

    def __init__(self, address, assign_number=False):
        self.address = address
        self.representative = None
        self.height = 0
        if assign_number:
            self.number = Address.counter
            Address.counter += 1

    def get_representative(self):
        r = self
        while r.representative is not None:
            r = r.representative
        return r

    def set_representative(self, address):
        self.representative = address
        if self.height >= address.height:
            address.height = self.height + 1

    def __lt__(self, other):
        return self.address < other.address

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)


class AddressList:

    def __init__(self):
        self.addresses = []

    def add(self, address_string):
        self.addresses.append(Address(address_string, True))

    def group(self, address_strings):
        if len(address_strings) >= 2:
            addresses = list(map(self.search, address_strings))
            representatives = {address.get_representative() for address in addresses}
            highest_representative = None
            for representative in representatives:
                if highest_representative is None or representative.height > highest_representative.height:
                    highest_representative = representative
            representatives.remove(highest_representative)
            for representative in representatives:
                representative.set_representative(highest_representative)

    def search(self, address_string):
        index = bisect.bisect_left(self.addresses, Address(address_string))
        return self.addresses[index]

    def export(self, path):
        with open(os.path.join(path, 'entities.csv'), 'w') as entity_csv_file, \
                open(os.path.join(path, 'rel_address_entity.csv'), 'w') as entity_rel_csv_file:
            entity_writer = csv.writer(entity_csv_file)
            entity_rel_writer = csv.writer(entity_rel_csv_file)
            entity_writer.writerow(['id:ID(Entity)'])
            entity_rel_writer.writerow([':START_ID(Address)', ':END_ID(Entity)'])
            for address in self.addresses:
                representative = address.get_representative()
                if address == representative:
                    entity_writer.writerow([representative.number])
                entity_rel_writer.writerow([address.address, representative.number])

    def print(self):
        for address in self.addresses:
            print(address.address, address.get_representative().address)


def compute_entities(input_path):
    address_list = AddressList()
    print('reading addresses')
    with open(os.path.join(input_path, 'addresses.csv'), 'r') as address_file:
        for line in address_file:
            line = line.strip()
            address_list.add(line)
    print('reading inputs')
    input_counter = 0
    with open(os.path.join(input_path, 'input_addresses.csv'), 'r') as input_file:
        input_addresses = set()
        transaction = None
        for line in input_file:
            entries = line.strip().split(',')
            address = entries[1]
            if transaction is None or transaction == entries[0]:
                input_addresses.add(address)
            else:
                address_list.group(input_addresses)
                input_addresses = {address}
            transaction = entries[0]
            input_counter += 1
            if input_counter % 100000 == 0:
                print('processed inputs: ' + str(input_counter))
        address_list.group(input_addresses)
    print('write to file')
    address_list.export(input_path)


def calculate_input_addresses(input_path):
    with open(os.path.join(input_path, 'rel_input.csv'), 'r', newline='') as input_file,\
            open(os.path.join(input_path, 'rel_output_address.csv'), 'r', newline='') as output_address_file,\
            open(os.path.join(input_path, 'input_addresses.csv'), 'w', newline='') as input_addresses_file:
        input_reader = csv.reader(input_file)
        output_address_reader = csv.reader(output_address_file)
        input_address_writer = csv.writer(input_addresses_file)
        last_output = ''
        last_address = ''
        for input_row in input_reader:
            txid = input_row[0]
            output_ref = input_row[1]

            match_address = last_address if output_ref == last_output else None

            for output_row in output_address_reader:
                output = output_row[0]
                address = output_row[1]
                if output_ref == output:
                    if match_address is None:
                        match_address = address
                    else:
                        match_address = None
                        last_output = output
                        last_address = address
                        break
                elif output_ref < output:
                    last_output = output
                    last_address = address
                    break
                last_output = output
                last_address = address

            if match_address is not None:
                input_address_writer.writerow([txid, match_address])
