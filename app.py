from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from drug_agent import drug_names_extractor_agent, target_names_extractor_agent, prediction_agent, repurpose_agent
from drug_agent import medical_agent_drug,medical_agent_target
import ast

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

CORS(app)  # Enable CORS for all routes

@app.route('/', methods=["GET", "POST"])
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getMedicalInfo', methods=["GET", "POST"])
def getMedicalInfo():
    try:
        drugRepurpose = []
        medical_info_drug=""
        medical_info_protein=""

        show_section_repurpose = session.get("show_section_repurpose")
        show_section_protein = session.get("show_section_protein")
        show_section_drug = session.get("show_section_drug")

        proposal = session.get("proposal")
        if request.method == "POST":

            try:
                drugTarget = session.get('drugTarget') 
                print ("Drug names is")
                print (drugTarget)

                if 'drugbtn' in request.form:
                    show_section_drug = True
                    drug = drugTarget[0]['Drug']
                    medical_info_drug = medical_agent_drug(drug)
                    session['medical_info_drug'] =medical_info_drug
                elif 'proteinbtn' in request.form:
                    show_section_protein = True
                    target = drugTarget[0]['Target']
                    medical_info_protein =  medical_agent_target(target)
                    session['medical_info_protein'] =medical_info_protein
                elif 'Generalrepurposebtn' in request.form:
                    show_section_repurpose = True
                    target = drugTarget[0]['Target']
                    #modify this part
                    print ("This is the general repurpose library")                
                    
                    repurposeLib = "broad"   #change to broad
                    result = repurpose_agent(target, repurposeLib)
                    drugRepurpose = []
                    for row in result:
                        rank = row[0]  # Index 0 → "Name"
                        dn = row[1]
                        tn = row[2]
                        db_score = row[3]
                        drugRepurpose.append({'Rank': rank,'Drug':dn,'Target':tn,'Score':db_score})
                    
                    session['drugRepurpose'] = drugRepurpose
                elif 'specialrepurposebtn' in request.form:
                    show_section_repurpose = True
                    target = drugTarget[0]['Target']
                    #modify this part
                    print ("This is the specialized repurpose library")
                    
                    
                    selected_repurpose_lib = request.form.get('rep')
                    print("Selected repurpose library:", selected_repurpose_lib)
                    if selected_repurpose_lib == "antiviral":
                        print ("will use antiviral rep")
                        repurposeLib = "antiviral"
                    elif selected_repurpose_lib == "cancer":
                        print ("will use cancer drug library")
                        repurposeLib = "cancer"

                    
                    result = repurpose_agent(target,repurposeLib)
                    drugRepurpose = []
                    for row in result:
                        rank = row[0]  # Index 0 → "Name"
                        dn = row[1]
                        tn = row[2]
                        db_score = row[3]
                        drugRepurpose.append({'Rank': rank,'Drug':dn,'Target':tn,'Score':db_score})
                    
                    session['drugRepurpose'] = drugRepurpose
                
                medical_info_drug = session.get("medical_info_drug")
                medical_info_protein = session.get("medical_info_protein")
                drugRepurpose = session.get("drugRepurpose")

                session['show_section_repurpose'] = show_section_repurpose
                session['show_section_protein'] = show_section_protein
                session['show_section_drug'] = show_section_drug

                return render_template("index.html", medical_info_drug=medical_info_drug,medical_info_protein=medical_info_protein,drugTarget=drugTarget,show_section_drug=show_section_drug,show_section_protein=show_section_protein,show_section_repurpose=show_section_repurpose,show_section=True, drugRepurpose=drugRepurpose,proposal=proposal)

            except Exception as e:
                print(f"Error: {e}")
                return render_template('wrong_index.html', error=str(e)), 500
        return render_template("index.html")
    except Exception as e:
        print(f"Error: {e}")
        return render_template('wrong_index.html', error=str(e)), 500
    


@app.route('/extractDrugNames', methods=["GET", "POST"])
def extractDrugNames():
    try:
        if request.method == "POST":
            try:
                print ("In extract drug name")

                show_section = True
                proposal = request.form.get('proposal')
                print (proposal)
                session['proposal'] = proposal
                print ("Testing printing proposal drugs", flush = True)
                #drug_names = "Aspirin"
                drug_names = drug_names_extractor_agent(proposal)
                drug_names_list = ast.literal_eval(drug_names.lower())
                print("\n The proposal is: ")
                print (proposal)
                print("\n The drugs you are using in this proposal are: ")
                print (drug_names)
                # Call the agent to extract target names
                #target_names = "COX1,COX2"
                target_names = target_names_extractor_agent(proposal)
                target_names_list = ast.literal_eval(target_names.lower())

                #print("\n The target proteins that the above drugs are binding to in this proposal are here in app.py: ")
                print("The targets extracted are", target_names)
                if isinstance(target_names_list, list):
                    print("Tareget name is a list.")
                else:
                    print("Target name is NOT a list.")

                if isinstance(drug_names_list, list):
                    print("Drug name is a list.")
                else:
                    print("Drug name is NOT a list.")

                score = prediction_agent(drug_names_list, target_names_list)
                #score=[2.5,3.5]
                print ("The score is", score)

                drugTarget = []
                
                if isinstance(score, (int, float)):
                    print ("it is a float")
                    #scorelist.append = str(round(score,2))
                    drugTarget.append({'Drug':drug_names_list[0],'Target':target_names_list[0],'Score':round(score,2)})

                else:
                
                    for i in range(len(target_names_list)):
                        print ("Item number ")
                        print (i)
                        print (target_names.split(",")[i])
                        print (score[i])
                        drugTarget.append({'Drug':drug_names_list[0],'Target':target_names_list[i],'Score':round(score[i],2)})

                session['drugTarget'] =drugTarget

                print ("The drug target session before exiting extraction is", drugTarget)
                session['show_section_repurpose'] = False
                session['show_section_protein'] = False
                session['show_section_drug'] = False
                session['medical_info_drug'] = ""
                session['medical_info_protein'] = ""
                session['drugRepurpose'] = "" 
                

                return render_template("index.html", drug_names=drug_names, target_names=target_names, score=score,drugTarget=drugTarget,show_section=show_section, proposal = proposal)
            except Exception as e:
                print(f"Error: {e}")
                return render_template('wrong_index.html', error=str(e)), 500
        return render_template("index.html")

    except Exception as e:
        print(f"Error: {e}")
        return render_template('wrong_index.html', error=str(e)), 500
    
if __name__ == '__main__':
     app.run(host='0.0.0.0', port=9999)
