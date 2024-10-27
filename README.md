# MapAssist
A watsonx AI based web application to help people in distress during a disaster.

## Installation
1. Have a Python3 installation ready
	- Refer [this doc](https://www.python.org/downloads/) to install 
2. Create a python virtual environment with pip. Example, `python3 -m venv mapassist`
3. Activate virtual environment, Example, `source <path to virtual env bin>`
4. Change to the project root and install requirements, `pip install -r requirements.txt`
5. Run the app using `streamlit run app.py`
6. Go to the following address in the browser, http://127.0.0.1:8501


## Application Flow

1. Ask for user location (browser permission) => User lat long
2. Based on their location, we check if there is an ongoing disaster (in our db) and if they need  immediate care => Ask and redirect to 911 for critical issues
2. User starts chat
	- can type raw text or select top suggested questions (hard-coded)
		- determine a severity score using simple LLM with defined prompt
	- based on score we have 3 separate flows and we also bucketize the user's distress into predefined buckets
		- may ask follow up questions if needed

Flow 1 => CRITICAL => Redirect to government agencies / 911. 

Flow 2 => Low => Awarness based queries
	- We identify requires resources based on user's query (vector database)
	- Feed data into RAG and ask for query resulution + Follow up chat OR Restart flow
	- Response can be summarized or may have interactive resources

Flow 3 => Medium (Community support)
	- Based on bucket of problem, identify personnels in the community who can help (show in map)
	- User can probably further describe their probllem and we can further filter the set of results in our database


Additional features
- Geo tagged images (uploaded by people)
- Queries heatmap
- Disaster heatmap
- Mental distress + Peer interaction
- Check on the critical ones also
