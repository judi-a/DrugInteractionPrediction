from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from drug_extractor_agent import drug_names_extractor_agent, target_names_extractor_agent, get_dti_score

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=["GET", "POST"])
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extractDrugNames', methods=["GET", "POST"])
def extractDrugNames():
    if request.method == "POST":
        proposal = request.form.get('proposal')
        print (proposal)
        drug_names = "Aspirin"
        #drug_names = drug_names_extractor_agent(proposal)
        print("\n The proposal is: ")
        print (proposal)
        print("\n The drugs you are using in this proposal are: ")
        print (drug_names)
        # Call the agent to extract target names
        target_names = "Cox1"
        #target_names = target_names_extractor_agent(proposal)
        print("\n The target proteins that the above drugs are binding to in this proposal are: ")
        print (target_names)
        score = get_dti_score(drug_names, target_names)
        
        return render_template("index.html", drug_names=drug_names, target_names=target_names, score=score)
    
    

    return render_template("index.html")



if __name__ == '__main__':
     app.run(host='0.0.0.0', port=9999)
