from pyweb import pydom
from pyodide.http import open_url
from pyscript import display
from js import console
#from agents.drug_extractor_agent import extractor_call

title = "Pandas (and basic DOM manipulation)"
page_message = "This project lets you input your proposal, containing one drug name and one protien, and it outputs their intarction predicted score."
proposal = "I will use Aspirin and COX1"

pydom["title#header-title"].html = title
pydom["a#page-title"].html = title
pydom["div#page-message"].html = page_message
pydom["input#txt-url"][0].value = proposal

def log(message):
    # log to pandas dev console
    print(message)
    # log to JS console
    console.log(message)

def loadFromURL(event):
    pydom["div#pandas-output-inner"].html = ""
    url = pydom["input#txt-url"][0].value

    log(f"Trying to fetch CSV from {url}")
    df = pd.read_csv(open_url(url))

    pydom["div#pandas-output"].style["display"] = "block"
    pydom["div#pandas-dev-console"].style["display"] = "block"

    display(df, target="pandas-output-inner", append="False")
 
def runExtractorAgent(event):
    pydom["div#pandas-output-inner"].html = ""
    proposal = pydom["input#txt-url"][0].value

    log(f"Running Extractor agent to extract drug and target names {proposal}")
    #df = pd.read_csv(open_url(proposal))
    #results = extractor_call(proposal)
    results = test(proposal)
    pydom["div#pandas-output"].style["display"] = "block"
    pydom["div#pandas-dev-console"].style["display"] = "block"

    display(results, target="pandas-output-inner", append="False")


def test(proposal):
    print ("Ok input received")
    return (f"This should be the result from text {proposal}")
