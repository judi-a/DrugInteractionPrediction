from openai import OpenAI
import os
import zipfile

import requests
from DeepPurpose import DTI as models
from DeepPurpose import oneliner
from DeepPurpose.dataset import *
from DeepPurpose.utils import *
from utils import get_compound_name, get_target_name_from_uniprot
from DeepPurpose.oneliner import repurpose 
import pandas as pd
import numpy as np
from prettytable import PrettyTable
import pickle 


SAVE_PATH = "./saved_path"


client = OpenAI()

def drug_names_extractor_agent(text):


  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are an assistant that extracts drug names from text."
              },
              {
                  "role": "user",
                  "content": f"Extract all drug names from the following biomedical text. Extract the drug names only, not the enzymes or proteins that the drugs bind to. Return the result as a Python list of strings — with no explanation, no text before or after. If there are no drug names, return an empty list: []. Only include drug names — not other chemicals, genes, or diseases.{text}"
                 
              }
      ]

    )
  drug_names = response.choices[0].message.content
  return drug_names

def target_names_extractor_agent(text):

  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are an assistant that extracts targets that drugs bind to from text."
              },
              {
                  "role": "user",
                  "content": f"Extract all protein names or protein families from the following biomedical sentence. Return the result as a Python list of strings. Include actual protein names, protein complexes, and commonly known protein family names — even if they are short (e.g., E1A) or alphanumeric. Do not include cell types or chemicals. If there are no protein names, return an empty list. [] {text}"
              }
      ]

    )
  target_names = response.choices[0].message.content
  return target_names
  
def get_multiple_dti_scores(
    drug: str,
    target_names: list,
    is_smiles=False,
    is_sequence=False,
) -> float:
   
    print (target_names)
    if not is_sequence:
        print ("in the not is_sequence")
        target_sequences = []
        for target in target_names:
            print (target)
            try:
                target_sequences.append(get_target_sequence(target))
            except ValueError:
                print(
                    f"Logging: Returning 0 because target sequence for '{target}' was not found."
                )
                return 0
    else:
        target_sequences = target_names

    #load pretrained model on BindingDB
    net = models.model_pretrained('models/model_MPNN_CNN/')
    print ("loaded the model")
    #Use the broad data to get the drug SMILE 
    X_repurpose, drug_name, drug_cid = load_broad_repurposing_hub_override("./data")
   
    print ("passed save path")
    if is_smiles:
        idx = X_repurpose == drug
    else:
        idx = drug_name == drug
    if not any(idx):
        print(f"Logging: Returning 0 because drug '{drug}' was not found.")
        return 0
    res = models.virtual_screening(
        X_repurpose[idx].repeat(len(target_names)),
        target_sequences,
        net,
        drug_name[idx].repeat(len(target_names)),
        target_names,
    )
    #squared_numbers = [x * proba for x in res]
    #average = sum(squared_numbers) / len(squared_numbers)


    return res


def get_dti_score(drug: str, target: str, is_smiles=False, is_sequence=False) -> float:

    if not is_sequence:
        try:
            target_sequence = get_target_sequence(target)
        except ValueError:
            print(
                f"Logging: Returning 0 because target sequence for '{target}' was not found."
            )
            return 0

    else:
        target_sequence = target

    print ("Target sequence is "+ target_sequence)
    
    #load pretrained model on BindingDB
    #net = models.model_pretrained('models/model_MPNN_CNN/') #
    net = models.model_pretrained('models/model_Morgan_AAC/')

    

    print ("loaded the model")
    #Use the broad data to get the drug SMILE 
    X_repurpose, drug_name, drug_cid = load_broad_repurposing_hub_override("./data")
    print ("loaded broad data")
    if is_smiles:
        idx = X_repurpose == drug
    else:
        idx = drug_name == drug
    if not any(idx):
        print(f"Logging: Returning 0 because drug '{drug}' was not found.")
        return 0
    print(f"\n The drug SMILE sequence is {X_repurpose[idx]}")
    res = models.virtual_screening(
        X_repurpose[idx], [target_sequence], net, drug_name[idx], [target]
    )

    return res[0]


def get_target_sequence(target: str) -> str:
    print ("Getting the amino acod sequence of the target")
    base_url = "https://rest.uniprot.org/uniprotkb/search"

    params = {
        "query": f"protein_name:{target} AND organism_id:9606",
        "format": "json",
        "fields": "sequence"
    }
    try:
        print("Parameters are: ", params)
        #response = requests.get(base_url, params=params)
        
        response = requests.get(base_url, params=params)
        #print ("Response is:",response.json())
        
        response.raise_for_status()

        data = response.json()
        #print ("Data returned is: ",data)
        if not data["results"]:
            raise ValueError(f"No sequence found for target '{target}'")

        sequence = data["results"][0]["sequence"]["value"]
        print(f"The amino acid sequence of the target is {sequence}")
        return sequence

    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

def prediction_agent(drug_names, target_names, is_smiles=False, is_sequence=False) -> float:
    print ("Inside prediction agent, with drugs ", drug_names)
    #print (len(drug_names.split(",")))
    #if len(drug_names.split(",")) == 1:
    if len(drug_names)>1:
        print ("Multiple drugs. Currently not supported. Using only the first one")
        
    drug_names=drug_names[0]

    if(len(target_names) > 1):
        print ("multiple targets", target_names)
        result = get_multiple_dti_scores(drug_names, target_names)
    else:
        print ("One single target", target_names)
        result = get_dti_score(drug_names, target_names[0])


    if result is not None:
        print("Result of DTI analysis:")
        print(result)
        return result
    else:
        print("DTI analysis failed due to an error.")


    ####
 
def repurpose_agent(target_names, repurposeLib = "antiviral"):
    print((target_names))
    print ("their length is ")
    print (len(target_names.split(",")))
    if len(target_names.split(",")) > 1: #multiple targets detected 
        print ("multiple targets, calling get_multiple_dti")
        multi_targets = target_names.split(",")
        #result = get_multiple_dti_scores(drug_names, multi_targets)
    else:
        print ("one target")
        target_sequence = get_target_sequence( target_names)
        print (target_sequence)
        result = repurpose_override(repurposeLib,target = target_sequence, target_name=target_names)
        print ("Done with repurpose")
        print (result)
        return result
    

def repurpose_override(repurposeLib, target, target_name,
                       finetune_epochs = 10,
					finetune_LR = 0.001,
					finetune_batch_size = 32,
					convert_y = True,
					subsample_frac = 1,
					pretrained = True,
					split = 'random',
					frac = [0.7,0.1,0.2],
					agg = 'agg_mean_max',
					output_len = 30):
    
    if repurposeLib == "broad":
        X_repurpose, drug_names,_ = load_broad_repurposing_hub_override()
    elif repurposeLib == "antiviral":
        X_repurpose, drug_names = load_antiviral_drugs_override()
    elif repurposeLib == "cancer":
        X_repurpose, drug_names = load_Cancer_drugs()
    else:
        X_repurpose, _, drug_names = load_antiviral_drugs_override()



    pretrained_model_names = ['model_MPNN_CNN'] #, 'model_CNN_CNN']
    #pretrained_model_names = [['MPNN', 'CNN'], ['CNN','CNN'], ['Morgan', 'CNN'], ['Morgan', 'AAC'], ['Daylight', 'AAC']]
    y_preds_models = []
    print('Beginning to load the pretrained models...')
    for idx, model_name in enumerate(pretrained_model_names):

        model = models.model_pretrained('models/'+model_name)
        print ("Done with model loading")
        y_pred = models.virtual_screening(X_repurpose, target, model, drug_names, target_name, convert_y = convert_y, verbose = False)
        y_preds_models.append(y_pred)
        print('Predictions from model ' + str(idx + 1) + ' with drug encoding ' + model_name[0] + ' and target encoding ' + model_name[1] + ' are done...')
        print('-------------')
        
    print('models prediction finished...')
    print('aggregating results...')
    
    if agg == 'mean':
        y_pred = np.mean(y_preds_models, axis = 0)
    elif agg == 'max_effect':
        if convert_y:        
            y_pred = np.min(y_preds_models, axis = 0)
        else:
            y_pred = np.max(y_preds_models, axis = 0)
    elif agg == 'agg_mean_max':
        if convert_y:        
            y_pred = (np.min(y_preds_models, axis = 0) + np.mean(y_preds_models, axis = 0))/2
        else:
            y_pred = (np.max(y_preds_models, axis = 0) + np.mean(y_preds_models, axis = 0))/2          

    print("Finished repurposing, show print now ")
    fo = os.path.join("result/", "repurposing.txt")
    print_list = []
    
    with open(fo, 'w') as fout:

        print('---------------')
        if target_name is not None:
            print('Drug Repurposing Result for ' + target_name)

        if model.binary:
            table_header = ["Rank", "Drug Name", "Target Name", "Interaction", "Probability"]
        else:
            # Regression
            table_header = ["Rank", "Drug Name", "Target Name", "Binding Score"]

        table = PrettyTable(table_header)
        print_list = []

        if drug_names is not None:
            f_d = max([len(o) for o in drug_names]) + 1
            for i in range(len(y_pred)):
                if model.binary:
                    if y_pred[i] > 0.5:
                        string_lst = [drug_names[i], target_name, "YES", "{0:.2f}".format(y_pred[i])]
                    else:
                        string_lst = [drug_names[i], target_name, "NO", "{0:.2f}".format(y_pred[i])]
                else:
                    # Regression: Rank, Drug Name, Target Name, Binding Score
                    string_lst = [drug_names[i], target_name, "{0:.2f}".format(y_pred[i])]
                    string = 'Drug ' + '{:<{f_d}}'.format(drug_names[i], f_d=f_d) + \
                            ' predicted to have binding affinity score ' + "{0:.2f}".format(y_pred[i])
                print_list.append((string_lst, y_pred[i]))

        # Sorting logic
        if convert_y:
            print_list.sort(key=lambda x: x[1])
        else:
            print_list.sort(key=lambda x: x[1], reverse=True)

        # Strip scores and keep just strings
        print_list = [i[0] for i in print_list]

        for idx, lst in enumerate(print_list):
            lst = [str(idx + 1)] + lst
            table.add_row(lst)
            

        fout.write(table.get_string())

    # Read and display top results
    with open(fo, 'r') as fin:
        lines = fin.readlines()
        for idx, line in enumerate(lines):
            if idx < output_len + 3:
                print(line, end='')
            else:
                print('Checkout ' + fo + ' for the whole list')
                break
        print()

    # Save results to pickle
    #with open(os.path.join("result/", 'output_list.pkl'), 'wb') as f:
    #    pickle.dump(print_list, f, pickle.HIGHEST_PROTOCOL)

    return table.rows[:output_len]





def medical_agent_drug(drug_names):

  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are a medical doctor who provides explanation to how these drugs are used."
              },
              {
                  "role": "user",
                  "content": f"Tell me how these drugs are used and what they are important at: {drug_names}"
              }
      ]

    )
  return response.choices[0].message.content

def medical_agent_target(target_names):

  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are a medical doctor who provides explanation to how these proteins are used."
              },
              {
                  "role": "user",
                  "content": f"Tell me how these drugs are used and what they are important at: {target_names}"
              }
      ]

    )
  return response.choices[0].message.content

def load_broad_repurposing_hub_override(path = './data'):
    df = pd.read_csv(path+"/broad.tab", sep = '\t')
    print ("loaded broad data")
    df = df.fillna('UNK')
    
    arr = df.title.values
    # Step 1: Convert to string type
    arr_str = arr.astype(str)

    # Step 2: Apply lowercase
    lower_arr = np.char.lower(arr_str)
    
    return df.smiles.values, lower_arr, df.cid.values.astype(str)

def load_antiviral_drugs_override(path = './data'):
    print ("loading antiviral")
    df = pd.read_csv(path+"/antiviral_drugs.tab", sep = '\t')
    print ("loaded antiviral data")
    return df.SMILES.values, df[' Name'].values

def load_Cancer_drugs(path = './data'):
    print ("loading IC50 data")
    df = pd.read_csv(path+"/cancer_drugs.csv")
    return df['Smiles'].values, df['Name'].values



if __name__ == "__main__":
  main()