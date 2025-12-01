import csv


def write_to_file(file, struct):
    with open(file, "w") as f:
        full_dict = "{"
        for k,v in struct.items():
            full_dict += f"\"{k}\":{v},\n" 
        full_dict = full_dict[:-2] + "}"
        f.write(full_dict)
    f.close()


def read_csv_and_create_dict(read_file):

    dict_parva_eighteen = {}
    p_eighteen_counter = 0
    dict_parva_hundred = {}
    p_hundred_counter = 0


    with open(input_file, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # if CSV has header
        for row in reader:
            col_1, col_2 = row[0], row[1]  
            if col_1 not in dict_parva_eighteen:
                p_eighteen_counter+=1
                p_hundred_counter+=1
                dict_parva_eighteen[col_1] = f"\"{p_eighteen_counter}\""
                dict_parva_hundred[col_1] = {f"{col_2}" : f"\"{p_hundred_counter}\""}
            else:
                if col_2 not in dict_parva_hundred[col_1]:
                    print(p_hundred_counter)
                    p_hundred_counter+=1
                    dict_parva_hundred[col_1][f"{col_2}"] = f"\"{p_hundred_counter}\""
    print(dict_parva_hundred)



    return (dict_parva_eighteen, dict_parva_hundred)


if __name__ == '__main__':

    input_file = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\Mahabharat_parva_classification.csv"
    output_file_col_1 = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\parva_18.txt"
    output_file_col_2 = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\parva_100.txt"

    dict_1, dict_2 = read_csv_and_create_dict(input_file)

    with open(output_file_col_1, "w") as f:
        full_dict = "{"
        for k,v in dict_1.items():
            full_dict += f"\"{k}\":{v},\n" 
        full_dict = full_dict[:-2] + "}"
        f.write(full_dict)
    f.close()

    with open(output_file_col_2, "w") as f:
        full_dict = "{"
        for k,v in dict_2.items():
            full_dict += f"\"{k}\":" + "{\n" 
            for x,y in v.items():
                full_dict += f"\t\"{x}\":{y},\n"
            full_dict = full_dict[:-2] + "\n\t},\n"
        full_dict = full_dict[:-2] + "\n}"
        f.write(full_dict)
    f.close()

    