from docxtpl import DocxTemplate
from docxtpl import RichText
import requests
from docxtpl import DocxTemplate
from docxtpl import RichText
from docxcompose.composer import Composer
import re

class Bill:


    def __init__(self, chamber="", committee_names = [""], date="", time="", number="", short_title="", description="", text_link="", status_link="", hearing_link=""):
        def find_yt_link(chamber):
            match chamber.strip().lower():
                case "senate":
                    return "https://www.youtube.com/channel/UCekvvdL_uyq2DUyj1GjlrOA"
                case "house":
                    return "https://www.youtube.com/channel/UCvoLAX1ww3e63K8qQ5of0bw"
                case default:
                    return "NO LINK FOUND"
        def gen_committees(committee_names):
            output = ""
            for committee in committee_names:
                output = output + re.sub(pattern="\s\s+", repl=" ", string=committee) + "\n"

            return output.strip()

        self.chamber = chamber
        self.committee_names = gen_committees(committee_names)
        self.date = date
        self.time = time

        self.number = number
        self.short_title = short_title
        self.description = re.sub(pattern="\s\s+", repl=" ", string=description)
        
        self.text_link = text_link

        self.status_link = status_link

        self.hearing_link = hearing_link

        self.chamber_yt_link = find_yt_link(chamber)

    def __str__(self) -> str:
        return "Num: " + self.number + "\nShort Title:" + self.short_title 
    

    def gen_context(self, template):
        return {
            'chamber' : self.chamber,
            'committee_names' : self.committee_names,
            'date' : self.date, 
            'time' : self.time,
            'bill_number' : self.number,
            'short_title' : self.short_title,
            'text_link' : RichText(self.number, url_id=template.build_url_id(self.text_link), color='0000EE', underline=True, font='Arial', size=20),
            'status_link' : RichText("Status & Testimony", url_id=template.build_url_id(self.status_link), color='0000EE', underline=True, font='Arial', size=20),
            'description' : self.description,
            'testimony_link' : RichText("https://www.capitol.hawaii.gov/login/login.aspx", url_id=template.build_url_id("https://www.capitol.hawaii.gov/login/login.aspx"), color='0000EE', underline=True, font='Arial', size=20),
            'hearing_link' : RichText(self.hearing_link, url_id=template.build_url_id(self.hearing_link), color='0000EE', underline=True, font='Arial', size=20),
            'chamber_yt_link' : RichText(self.chamber_yt_link, url_id=template.build_url_id(self.chamber_yt_link), color='0000EE', underline=True, font='Arial', size=20)
        }
    
    
def create_final_document(date, bill_data, bill_number_list,):
    template = DocxTemplate(r"Documents\BillTemplate.docx")
    output_doc = DocxTemplate(r"Documents\HeaderTemplate.docx")

    #add date to header
    output_doc.render({ 'date' :  date})
    comp = Composer(output_doc)



    #any bill with a matching name is added to the document
    for bill in bill_data:  
        for num in bill_number_list:
            if re.search(pattern=num.strip(), string=bill.number.strip(), flags=re.IGNORECASE):
                template.render(bill.gen_context(template))
                comp.append(template)

    
    return comp


def parse_bills(soup, hearing_link):
    output = [] 

    #find house or senate
    first_span = soup.find("span")

    if first_span.text.strip() == "THE SENATE":
        chamber = "SENATE"
    else:
        chamber = "HOUSE"

    date = ""
    time = ""
    committee_names = []

    number = "",
    short_title = "",
    description = "",

    text_link = "",

    status_link = "",


    all_info = soup.find_all("p", {"class":"MsoNormal"})
    
    for i in range(0, len(all_info)):
        #

        

        match all_info[i].text.strip().lower():
            case "date:":
                i += 1
                date = all_info[i].text.strip()
            case "time:":
                i += 1
                time = all_info[i].text.strip()
            case default:

                #The current line is the same of one of the committees
                if re.match(pattern='committee', string=all_info[i].text.strip(), flags=re.IGNORECASE):
                    committee_names.append(all_info[i].text.strip())

                #The current line is the name of one of a bill
                elif re.match(pattern='sb|hb', string=all_info[i].text.strip(), flags=re.IGNORECASE):
                    try:
                        number = all_info[i].text.strip()
                        text_link = all_info[i].find('a')['href']
                        
                        #skips over useless info untill it gets to status and testimony link
                        while re.search(pattern='status', string=all_info[i].text, flags=re.IGNORECASE) == None :
                            i+=1


                        status_link = all_info[i].find('a')['href']

                        i+=1
                        short_title = all_info[i].text.strip()

                        i+= 1
                        description = all_info[i].text.strip()


                        output.append( 
                            Bill(
                                chamber,
                                committee_names,
                                date,
                                time,
                                
                                number,
                                short_title,
                                description ,

                                text_link,

                                status_link,

                                hearing_link

                                )
                        )
                    except:
                        print("error parsing bill " + number)

                    #print(output[len(output)-1].number)


    return output, date, time
            

def parse_input(input):
    return re.split(",", input)


