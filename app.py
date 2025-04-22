from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from drug_extractor_agent import drug_names_extractor_agent, target_names_extractor_agent, prediction_agent, repurpose_agent

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=["GET", "POST"])
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extractDrugNames', methods=["GET", "POST"])
def extractDrugNames():
    if request.method == "POST":
        try:
            show_section = True
            proposal = request.form.get('proposal')
            print (proposal)
            print ("Testing printing proposal drugs", flush = True)
            drug_names = "Aspirin"
            #drug_names = drug_names_extractor_agent(proposal)
            print("\n The proposal is: ")
            print (proposal)
            print("\n The drugs you are using in this proposal are: ")
            print (drug_names)
            # Call the agent to extract target names
            target_names = "COX1"
            #target_names = target_names_extractor_agent(proposal)
            #print("\n The target proteins that the above drugs are binding to in this proposal are here in app.py: ")
            print (target_names)
            #score = prediction_agent(drug_names, target_names)
            score=2.5
            print ("Trying repurposeing")
            result = repurpose_agent(target_names)

            drugRepurpose = []
            print ("looks like the error is here")
            for row in result:
                rank = row[0]  # Index 0 → "Name"
                dn = row[1]
                tn = row[2]
                db_score = row[3]
                drugRepurpose.append({'Rank': rank,'Drug':dn,'Target':tn,'Score':db_score})
  # Index 1 → "Age"
            # return render_template("index.html", drug_names=drug_names, target_names=target_names, score=score)
        
            drugTarget = []
            if isinstance(score, (int, float)):
                print ("it is a float")
                #scorelist.append = str(round(score,2))
                drugTarget.append({'Drug':drug_names,'Target':target_names,'Score':round(score,2)})

            else:
                for i in range(len(score)):
                    print ("Item number ")
                    print (i)
                    print (target_names[i])
                    print (score[i])
                    drugTarget.append({'Drug':drug_names,'Target':target_names.split(",")[i],'Score':round(score[i],2)})

            return render_template("index.html", drug_names=drug_names, target_names=target_names, score=score,show_section=show_section, drugTarget=drugTarget, drugRepurpose = drugRepurpose)
        except Exception as e:
            print(f"Error: {e}")
            return render_template('wrong_index.html', error=str(e)), 500

    return render_template("index.html")


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=9999)
