# DrugInteractionPrediction

In this work, we introduce an AI-enabled pipeline for drug-target relation (DTI) prediction and drug repurposing that uses natural language processing (NLP), deep learning, and structured biomedical databases. The system is designed for non-expert users, like biomedical researchers, to test and refine hypotheses by providing them with predicted binding scores between drugs and targets mentioned in their hypotheses, repurposing recommendations, and relevant clinical information. 

We leverage large language models (LLM) for entity extraction and medical reasoning along with DeepPurpose framework for DTI prediction. This approach helps mitigate the limitations of traditional high-throughput screening strategies by reducing the search space for wet lab validation. Our DTI models are validated on benchmark datasets (Davis and KIBA) and showedggg that MPNN-AAC architecture achieves the best performance. 

In addition, protein and drug name extraction prompts were optimized and validated using the JNLPBA and BC5CDR datasets respectively. Prompts with the highest F1 scores were selected (95% and 96% for the protein and drug name extractor prompts respectively). The system is deployed as a web interface on Google Cloud Platform (GCP) and the source code is publicly available.

Web server deployment is available here: https://druginteraction-280377787251.us-central1.run.app

## Overview

The main task of this AI agent is to facilitate the drug discovery process. Understanding how drug interacts with other proteins and molecules helps developing effective treatments for diseases while minimizing side effects. 

This script utilizes OpenAI's API to extract information from text, including drug and target names, and to predict drug-target interaction (DTI) scores using pretrained models from the DeepPurpose library. Additionally, it fetches amino acid sequences for target proteins and provides general medical information on drugs.

This agent asks the user to input a proposal of the experiment they are working on. 
1. The first step is that it calls two extractor agents; one to extract the drug name and the other to extract the protein name from the experiment proposal.
2. In order to predict interaction, one needs to get the 3D structure of the interacting molecules. For drugs, this is represented by the SMILE sequence. For protein, the amino acid sequence is used. Therefore, two other agents are called to extract the SMILE sequence and the amino acid sequences of both the drug and the protein.
3. Finally, the prediction agent loads a pretrained model, that was already trained on drug protein interaciton data in the other project (DrugInteraction). It then predicts the binding interatction between the given drug and target

4. There is also a medical agent that provides explanation on how the drugs are used
Code is packaged within a Docker image.

## How to run:
1. Clone the repo
2. Add your openAI key to your Dockerfile ENV OPENAI_API_KEY="XXXX"
3. Build your docker image using the following command:
      docker build . -t us-central1-docker.pkg.dev/cobalt-list-456819-t4/drug-tracker/drug-agent:optimised
4. To run it locally, use the following command:
      docker run -it -p 9999:9999 us-central1-docker.pkg.dev/cobalt-list-456819-t4/drug-tracker/drug-agent:optimised
5. To deploy on Google cloud,
    a. make sure to sign in to your GCP account from the terminal
      gcloud auth configure-docker us-central1-docker.pkg.dev
    b. Push the image to the cloud
      docker push us-central1-docker.pkg.dev/cobalt-list-456819-t4/drug-tracker/drug-agent:optimised
   c. Deploy it!


