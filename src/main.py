import requests
import BillParser
from bs4 import BeautifulSoup



def main():
    hearing_link = input("Enter the hearing link: ").strip()

    r = requests.get(hearing_link)


    soup = BeautifulSoup(r.content, 'html.parser')

    bill_data, date, time = BillParser.parse_bills(soup, hearing_link)


    target_bills = input("Enter the bills you want to search for as a comma separated list(HB 100,HB 200): ")

    target_bills = BillParser.parse_input(target_bills)

    output_name = input("Enter the desired name of the generated .docx file: ")



    final_doc = BillParser.create_final_document(date, bill_data, target_bills)

    final_doc.save(r"Output/" + output_name + r".docx")





main()








