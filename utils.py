import json
import pickle
from typing import Dict, List, Optional

import autogen
import numpy as np
import requests
from DeepPurpose.dataset import load_broad_repurposing_hub


def load_config(config_file="config.json"):
    with open(config_file, "r") as f:
        return json.load(f)


def extract_last_dti_score(
    chat_history: List[Dict[str, str]]
) -> Optional[Dict[str, float]]:
    required_keys = {
        "ml_dti_score",
        "search_dti_score",
        "kg_dti_score",
        "merged_dti_score",
    }

    for message in reversed(chat_history):
        content = message.get("content", "")
        if isinstance(content, str) and all(key in content for key in required_keys):
            try:
                json_str = content[content.index("{") : content.rindex("}") + 1]
                result = json.loads(json_str)

                return {key: result.get(key) for key in required_keys}
            except (ValueError, json.JSONDecodeError):
                continue

    return None


def extract_last_dti_score_for_multi_target(
    chat_history: List[Dict[str, str]]
) -> Optional[Dict[str, float]]:
    required_keys = {
        "drug",
        "disease",
        "probability",
        "DTI_score",
    }

    for message in reversed(chat_history):
        content = message.get("content", "")
        if isinstance(content, str) and all(key in content for key in required_keys):
            try:
                json_str = content[content.index("{") : content.rindex("}") + 1]
                result = json.loads(json_str)

                return {key: result.get(key) for key in required_keys}
            except (ValueError, json.JSONDecodeError):
                continue

    return None


CONFIG_LIST = load_config()


def create_agent(name, system_message):
    return autogen.AssistantAgent(
        name=name,
        system_message=system_message,
        llm_config=CONFIG_LIST,
    )


def get_target_name_from_uniprot(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("genes", [{}])[0].get("geneName", {}).get("value")
    except requests.RequestException as e:
        print(f"Error retrieving gene name for UniProt ID {uniprot_id}: {e}")
        return None


def get_compound_name(smiles):
    SAVE_PATH = "./saved_path"
    X_repurpose, drug_name, drug_cid = load_broad_repurposing_hub(SAVE_PATH)
    return drug_name[X_repurpose == smiles][0]
