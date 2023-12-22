import csv
from Cell import Cell

# def write(file_path: str, cell: Cell, value: int) -> None:
#     with open(file_path, 'r') as file:
#         csv_reader = list(csv.reader(file))

#     try:
#         csv_reader[cell.column][cell.row] = value
#     except IndexError:
#         print("Row or column index out of range.")
#         print("Row: " + str(cell.row) + " Column: " + str(cell.column))

#     with open(file_path, 'w', newline='') as file:
#         csv_writer = csv.writer(file)
#         csv_writer.writerows(csv_reader)

# def increment(file_path: str, cell: Cell, value: int) -> None:
#     with open(file_path, 'r') as file:
#         csv_reader = list(csv.reader(file))

#     try:
#         csv_reader[cell.column][cell.row] = int(csv_reader[cell.column][cell.row]) + value
#     except IndexError:
#         print("Row or column index out of range.")
#         print("Row: " + str(cell.row) + " Column: " + str(cell.column))

#     with open(file_path, 'w', newline='') as file:
#         csv_writer = csv.writer(file)
#         csv_writer.writerows(csv_reader)

def write_table(file_path, table):
    with open(file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(table)