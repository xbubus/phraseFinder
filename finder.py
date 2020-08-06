from bs4 import BeautifulSoup
import requests
import sys
import getopt   
import threading 
from queue import Queue


class Finder:
    def __init__(self):
        self.file_path = None
        self.phrase = None
        self.params_optional = None
        self.links = None
        self.queue = None
        self.offset = 30
        self.results = []
        self.counter = 0
        

    def parse_optlist(self, optlist):
        for opt, arg in optlist:
                if opt == '-h':
                    print ("finder.py -f <pathToFile> -p <phraseToFind> -o <optionalParameters>")
                    print ("for example: py finder.py -f \"links.txt\" -p \"your phrase\" -o \"h1,p,h3\"")
                    sys.exit()
                elif opt in ("-f", "--file_path"):
                    self.file_path = arg
                elif opt in ("-p", "--phraseToFind"):
                    self.phrase = arg
                elif opt in ("-o", "--optionalParameters") and len(arg) > 0:
                    self.params_optional = arg.split(',')
        self.validate_args()


    def validate_args(self):
        if not self.file_path or not self.phrase:
            print("You must enter path to file and phrase to find: ")
            print ("finder.py -f <pathToFile> -p <phraseToFind>")
            sys.exit()

    def load_links(self, path: str):
        try:
            print('Opening:', path)
            file =open(path,"r")
            links= file.readlines()
            file.close()
            links = [x.strip() for x in links]
            return links      
        except:
            print("Cannot open file")
            sys.exit();

    def run(self):
        self.links = self.load_links(self.file_path)
        self.setup_workers(32)
        self.add_links_to_queue()
    def setPhrase(self,phrase):
        self.phrase=phrase
    def setOffset(self,offset):
        self.offset=offset
    def setParams(self,params):
        self.params_optional=params
    def add_links_to_queue(self):
        try:
            for link in self.links:
                if link:
                    self.queue.put(link)
            self.queue.join()
        except:
            print("Something went wrong")
            sys.exit(0)

    def setup_workers(self, num_workers):
        self.queue = Queue(num_workers*2)
        for num in range(num_workers):
            thread = threading.Thread(target = self.process_link)
            thread.daemon = True
            thread.start()
                    
    def get_raw_html(self, link):
        page=requests.get(link) 
        soup=BeautifulSoup(page.content,"html.parser")
        return soup

    def find_all(self, a_str, sub):
        start = 0
        a_str = a_str.lower();
        sub = sub.lower();
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub) 
            
    def process_link(self):
        my_counter = self.counter
        self.counter+=1 
        jobs_counter = 0
        while True:
            link = self.queue.get()
            print('im', my_counter, 'and this is my ', jobs_counter, 'job', link)
            text_params = ""
            try:
                soup = self.get_raw_html(link)
                if self.params_optional:
                    result = self.find_phrase_with_params(soup, link)
                else:
                    result = self.find_phrase_without_params(soup, link)
                self.results.append((link, result))
                self.queue.task_done()
            except:
                self.results.append((link, [-1]))
                self.queue.task_done()
            jobs_counter+=1
                        
    def find_phrase_with_params(self,soup,link):
        currentResult = []
        textParameters = ""
        wordsindex=[]
        a=soup.find_all(self.params_optional)
        if a is None:
             currentResult.append(0)
             return currentResult
        for t in a: 
            textParameters += t.text 
            wordsindex = list(self.find_all(textParameters, self.phrase)) 
        if len(wordsindex)== 0: 
            currentResult.append(0) 
        else: 
            for index in wordsindex:
                i1=index-self.offset
                if i1<0:
                    i1=0
                i2=index+self.offset+len(self.phrase)
                if i2>len(textParameters):
                    i2=len(textParameters)
                textToPrint=textParameters[i1:i2].strip().replace('\n','').replace('\r','') #zapisuje 
                currentResult.append(textToPrint)
        return currentResult

    def find_phrase_without_params(self, soup,link):
        currentResult=[]
        wordsindex=list(self.find_all(soup.text, self.phrase)) 
        if len(wordsindex)==0: 
            currentResult.append(0)
        else:
            for index in wordsindex:
                i1=index-self.offset
                if i1<0:
                    i1=0
                i2=index+self.offset+len(self.phrase)
                if i2>len(soup.text):
                    i2=len(soup.text)
                textToPrint = soup.text[i1:i2].strip().replace('\n','').replace('\r','')
                currentResult.append(textToPrint)
        return currentResult

    def print_results(self):
        for result in self.results:
            print("\nWebsite: "+result[0])
            if result[1][0]==-1:
                print("Invalid Link/Cannot Open Link")
            elif result[1][0]==0:
                print("No results")
            else:
                for r in result[1]:
                    print(r)
                
if __name__ == "__main__":
    try:
        argv = sys.argv[1:]
        optlist, args = getopt.getopt(argv,"hf:p:o:",["filePath","phraseToFind=","optionalParameters="])
        finder = Finder()
        finder.parse_optlist(optlist)
        finder.run()
        finder.print_results()



    except getopt.GetoptError:
        print ("finder.py -f <pathToFile> -p <phraseToFind> -o <optionalParameters>")
        print ("for example: py finder.py -f \"links.txt\" -p \"your phrase\" -o \"h1,p,h3\"")
        sys.exit()


        

