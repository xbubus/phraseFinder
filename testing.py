import unittest
import sys
from bs4 import BeautifulSoup
from finder import Finder


class Test(unittest.TestCase):
    finder=Finder()
    html=""
    path="test.html"
    phrase="Tekst"
    finder.setPhrase(phrase)
    finder.setOffset(30)
    params=["p","h3"]

    try:
        file =open(path,"r")
        html= file.read()
        file.close()
    except:
        print("Cannot open file")
        sys.exit()
    def test_find_phrase_with_params(self):
        soup=BeautifulSoup(self.html,"html.parser")
        self.finder.setParams(self.params)
        a=self.finder.find_phrase_with_params(soup,"test")
        b=['Tekst in paragraph.Tekst in heading', 'Tekst in paragraph.Tekst in heading3']
        self.assertEqual(a,b)
    
    def test_find_phrase_without_params(self):
        soup=BeautifulSoup(self.html,"html.parser")
        a=self.finder.find_phrase_without_params(soup,"test")  
        b=['Tekst in heading1Tekst in paragrap', 'Tekst in heading1Tekst in paragraph.Tekst in headin', 'heading1Tekst in paragraph.Tekst in heading3']
        self.assertEqual(a, b)
 

unittest.main()


