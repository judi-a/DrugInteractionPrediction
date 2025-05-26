import requests

# Step 1: Search for accession
search_url = "https://rest.uniprot.org/uniprotkb/search"
params = {
    "query": "protein_name:cox-1",
    "format": "json",
    "fields": "accession"
}
response = requests.get(search_url, params=params)
accession = response.json()["results"][0]["primaryAccession"]

# Step 2: Get sequence
fasta_url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
fasta_response = requests.get(fasta_url)
print(fasta_response.text)